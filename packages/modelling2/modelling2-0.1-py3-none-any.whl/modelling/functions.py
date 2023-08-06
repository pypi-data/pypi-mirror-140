from modelling import *
import gdal as gdal
import geopy.geocoders as gcd

# region -------------------------- FUNCTIONS --------------------------


def clip_layer(path_to_file, zone_polygon, epsg=2193):
    """
    Clip a shape file to a zone
    :param path_to_file: Tolerance to split and connect lines and points
    :param zone_polygon: GeoDataFrame of zones. All polygons are joined to get the clipping extent
    :type zone_polygon: GeoDataFrame
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame with geometry inside zone polygon
    """

    # Create the crs
    crs = "epsg:{}".format(epsg)

    # Create a new geodataframe for the merged zone
    zone = gp.GeoDataFrame(geometry=[zone_polygon.unary_union])
    zone.crs = crs

    # Read in the gis file
    df = gp.read_file(path_to_file, bbox=tuple(zone.total_bounds))
    df.crs = crs

    # Get assets which intersect with the zones
    join_df = gp.sjoin(df, zone, how="inner", op='intersects')

    # Remove the columns of the zone
    df = join_df[df.columns]
    df.crs = crs

    return df


def different_attributes(left_df, left_key, right_df, right_key, left_attribute, right_attribute, epsg=2193):
    """
    Compare a dataframe to another based off of an id for each row. For rows with the same id, compare the columns
    of the left and right attributes to see which attributes differ.
    Example: Compare two dataframes based off of COMPKEY to see whether the diameter of a line has changed
    :param left_df: Left GeoDataFrame to compare
    :param left_key: Unique id column name for the left GeoDataFrame
    :param right_df: Right GeoDataFrame to compare
    :param right_key: Unique id column name for the right GeoDataFrame
    :param left_attribute: Left attribute to compare
    :param right_attribute: Right attribute to compare
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame with different attributes
    """

    # Create the crs
    crs = "epsg:{}".format(epsg)

    # Copy the dataframes so they are not edited
    left_df = left_df.copy()
    right_df = right_df.copy()

    # Make sure the keys are of the same type to compare
    left_df[left_key] = left_df[left_key].astype(str)
    right_df[right_key] = right_df[right_key].astype(str)

    # Merge both of the dataframes on the keys
    merge_df = gp.GeoDataFrame(left_df.merge(right_df, how='inner', left_on=left_key, right_on=right_key))

    # Find where the attributes differ
    diff_df = merge_df[merge_df[left_attribute] != merge_df[right_attribute]]
    diff_df = diff_df.set_geometry('geometry_x').drop(columns='geometry_y')

    diff_df.crs = crs

    return diff_df


def different_length(left_df, left_key, right_df, right_key, left_attribute, right_attribute, tol, crs=default_crs_source):
    """
    Compare a dataframe to another based off of an id for each row. For rows with the same id, compare the columns
    of the left and right attributes to see which attributes differ.
    Example: Compare two dataframes based off of COMPKEY to see whether the diameter of a line has changed
    :param left_df: Left GeoDataFrame to compare
    :param left_key: Unique id column name for the left GeoDataFrame
    :param right_df: Right GeoDataFrame to compare
    :param right_key: Unique id column name for the right GeoDataFrame
    :param left_attribute: Left attribute to compare
    :param right_attribute: Right attribute to compare
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame with different attributes
    """
    left_df = left_df.copy()
    right_df = right_df.copy()

    left_df[left_key] = left_df[left_key].astype(str)
    right_df[right_key] = right_df[right_key].astype(str)

    merge_df = gp.GeoDataFrame(left_df.merge(right_df, how='inner', left_on=left_key, right_on=right_key))
    merge_df.crs = crs

    diff_len_df = pd.merge(merge_df.drop_duplicates(subset=left_key),
                           pd.DataFrame(merge_df.groupby(right_key)[right_attribute].sum()).reset_index(),
                           how='inner', left_on=left_key, right_on=right_key, suffixes=('_ind', '_tot'))  # Get the total length of pipes

    diff_len_df = diff_len_df[(diff_len_df[left_attribute] * (1 + tol) < diff_len_df[right_attribute + '_tot']) | (
            diff_len_df[left_attribute] * (1 - tol) > diff_len_df[right_attribute + '_tot'])]

    diff_len_df = diff_len_df.set_geometry('geometry_x').drop(columns='geometry_y')

    diff_len_df.crs = crs

    return diff_len_df


def node_elevations(node_df, raster_path, field_name='gndlvl', epsg=2193):
    """
    Get the elevation for the nodes from the raster specified
    :param node_df: GeoDataFrame of points
    :param raster_path: Path to the raster
    :param field_name: The resulting column name to store the elevation
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame with a new column containing the point elevations
    """

    # Create the crs
    crs = "epsg:{}".format(epsg)

    # Copy the dataframes so they are not edited
    node_df = node_df.copy()

    # Get raster points
    dataset = gdal.Open(raster_path)
    band = dataset.GetRasterBand(1)
    elevations = band.ReadAsArray(0, 0, dataset.RasterXSize, dataset.RasterYSize)
    x_origin, pixel_width, _, y_origin, _, pixel_height = dataset.GetGeoTransform()

    # Convert MultiPoints to Points
    geom = node_df.geometry.apply(lambda p: p[0] if p.type == 'MultiPoint' else p)

    # Define a function to get the point elevation. If the point location is outside the raster, return -1
    def _get_elevation(point):
        try:
            return elevations[int((point.y - y_origin) / pixel_height)][int((point.x - x_origin) / pixel_width)]
        except IndexError:
            return -1

    # Get the elevation of the points
    node_df[field_name] = geom.apply(lambda p: _get_elevation(p))
    node_df.crs = crs

    return node_df


def nearest_pipe_diameters(node_df, pipe_df, diameter_key='NOM_DIA_MM'):
    """
    Get the diameter of the nearest pipe to a node
    :param node_df: GeoDataFrame of points
    :param pipe_df: GeoDataFrame of lines
    :param diameter_key: Diameter key for the lines
    :return df: GeoDataFrame of points with the nearest pipe diameter key
    """

    # Copy the dataframe to avoid editing data
    node_df = node_df.copy()
    pipe_df = pipe_df.copy()

    # For each node
    for i, row in node_df.iterrows():
        pt = row.geometry

        # Find pipes which are close to the nodes
        possible_matches_index = list(pipe_df.sindex.intersection(pt.buffer(0.1).bounds))
        possible_matches = pipe_df.iloc[possible_matches_index]

        # If we found some close pipes, get the closest one. Otherwise set the diameter to 0
        if len(possible_matches) > 0:
            node_df.at[i, diameter_key] = possible_matches.loc[possible_matches.distance(pt).idxmin(), diameter_key]
        else:
            node_df.at[i, diameter_key] = 0

    return node_df


def buffer_intersect(df_target, df_buffer, buffer_size, epsg=2193):
    """
    Get the diameter of the nearest pipe to a node
    :param df_target: GeoDataFrame of points
    :param df_buffer: GeoDataFrame of lines
    :param buffer_size: Diameter key for the lines
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame of points with the nearest pipe diameter key
    """

    # Create the crs
    crs = "epsg:{}".format(epsg)

    # Copy the dataframe to avoid editing data
    df_target = df_target.copy()
    df_buffer = df_buffer.copy()

    # Buffer and create a new df
    df_buffer = gp.GeoDataFrame(df_buffer.buffer(buffer_size)).rename(columns={0: 'geometry'}).set_geometry('geometry')
    df_buffer.crs = crs

    df_target = gp.sjoin(df_target, df_buffer, how="inner", op='intersects')
    df_target.crs = crs
    return df_target


def save_df(input_dict):
    """
    Save a group of DataFrames to their respective files
    :param input_dict: Dictionary with a GeoDataFrame as the key, and the resulting file path as the value
    """
    for output_df, filename in input_dict:
        try:
            output_df.to_file(filename)
        except ValueError:
            print('Empty Dataframe: ' + filename + '\n')


def get_point_address(node_df, field_name='address'):
    """
    Get the address of a point and save it under a new
    :param df_target: GeoDataFrame of points
    :param df_buffer: GeoDataFrame of lines
    :param buffer_size: Diameter key for the lines
    :param epsg: EPSG number of the coordinate reference system
    :return df: GeoDataFrame of points with the nearest pipe diameter key
    """

    # Used to stop ssl errors
    gcd.options.default_ssl_context = ctx

    # Copy the dataframe
    node_df = node_df.copy()

    # Create the crs target
    crs_target = "epsg:4326"
    crs_original = node_df.crs

    # Google api key
    # api_key='AIzaSyAeG9AXUhjNBtnS5x4mgI5_2-8RIUE1geM'

    # Create the geolocator
    geolocator = gcd.Nominatim(timeout=3)

    # Convert the df to the correct crs and geometry format
    node_df = node_df.to_crs(crs_target)
    geom = node_df.geometry.apply(lambda p: p[0] if p.type == 'MultiPoint' else p)

    # Get the point addresses
    node_df[field_name] = geom.apply(lambda p: geolocator.reverse((str(p.y) + ',' + str(p.x))))

    # Convert it back to the orginal crs
    node_df = node_df.to_crs(crs_original)
    return node_df


def get_point_xy(df, drop=True):
    df = df.copy()

    geom = df.geometry.apply(lambda p: p[0] if p.type == 'MultiPoint' else p)

    df['x'] = geom.apply(lambda pt: pt.x)
    df['y'] = geom.apply(lambda pt: pt.y)
    if drop:
        df = df.drop(labels=df.geometry.name, axis=1)
    return df


def get_line_xy(df, drop=True):
    df = df.copy()

    geom = df.geometry.apply(lambda p: p[0] if p.type == 'MultiLineString' else p)

    df['x'] = geom.apply(lambda line: list(line.coords.xy[0]))
    df['y'] = geom.apply(lambda line: list(line.coords.xy[1]))
    if drop:
        df = df.drop(labels=df.geometry.name, axis=1)
    return df


def get_poly_xy(df, drop=True):
    df = df.copy()

    geom = df.geometry.apply(lambda p: p[0] if p.type == 'MultiPolygon' else p)

    df['x'] = geom.apply(lambda poly: list(poly.exterior.coords.xy[0]))
    df['y'] = geom.apply(lambda poly: list(poly.exterior.coords.xy[1]))
    if drop:
        df = df.drop(labels=df.geometry.name, axis=1)
    return df


def id_to_string(ids, is_string=False):
    """
    Create a string from a Tuple/List/Series of ids
    :param ids: Tuple/List/Series of ids to convert to a string
    :param is_string: Is the id a string or an int. Adds quotation marks to each id in the string
    :return: String with the ids seperated by commas
    """
    if len(ids) > 0:
        df = pd.DataFrame(ids)
        if is_string:
            string = "('" + df.to_csv(header=False, index=False).replace("\r\n", "','")[:-3] + "')"
        else:
            string = "(" + df.to_csv(header=False, index=False).replace("\r\n", ",")[:-1] + ")"
        return string
    else:
        return '(null)'


def unix_to_datetime(unix_series, from_tz='UTC', to_tz='NZ'):
    """
    From a Series of unixdatetimes convert it to a datetime in the correct timezones
    List of timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :param unix_series: Series of unixdatetimes
    :param from_tz: Timezone to convert from as a string.
    :param to_tz: Timezone to convert to as a string
    :return: Series with datetimes and timezone
    """
    return pd.to_datetime(unix_series, dayfirst=True, unit='s').dt.tz_localize(from_tz).dt.tz_convert(to_tz)


def datetime_to_unix(datetime_series, tz=None):
    """
    From a Series of datetimes convert it to a unixdatetime in the correct timezones
    List of timezones: https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
    :param datetime_series: Series of datetimes
    :param tz: The timezone of the datetime series
    :return: Series with datetimes and timezone
    """

    # Convert to the correct timezone, otherwise
    if datetime_series.dt.tz is None:
        if tz is None:
            raise RuntimeError('Series is not datetime aware, please specify the timezone')
        else:
            datetime_series = datetime_series.copy().dt.tz_localize(tz)

    return (datetime_series.astype(int)//1e9).astype(int)


def group_to_df(df, groupby, col):
    """
    Group a DataFrame by a column and create a new DataFrame with the results
    :param df: DataFrame to group results
    :param groupby: The columns of the new DataFrame
    :param col: The values of the new DataFrame
    :return: DataFrame with the grouped results
    """
    dict_df = dict(tuple(df.groupby(groupby)[col]))
    return pd.DataFrame(dict_df)


def plot_shapely(shapely_geom, **kwargs):
    """
    Plot shapely geometry
    :param shapely_geom: Geometry or list of Geometries
    """

    # If the geomerty isnt an iterable object, wrap it in a list
    try:
        iter(shapely_geom)
    except TypeError:
        shapely_geom = [shapely_geom]

    # Create a GeoDataFrame and plot the geometry
    gp.GeoDataFrame(geometry=shapely_geom).plot(**kwargs)


def infoworks_to_df(path):
    """
    Plot shapely geometry
    :param path: Path to the infoworks .sli or .prn file
    """

    # Check the path is of the right format
    if not path.endswith(".sli") or not path.endswith(".prn"):
        return None

    # Open the file and read it to text
    with open(path, 'r') as f:
        text = f.readlines()

    # Get the lines which contain the times, and the first line of data
    if path.endswith(".sli"):
        time_idx = 4
        start_idx = 5
    elif path.endswith(".prn"):
        time_idx = 3
        start_idx = 4

    # Split the line with the line with the times
    time_line = text[time_idx].split(',').replace(' ', '')

    # Get params
    initial_time = dt.strptime(time_line[1] + time_line[2], '%d/%m/%y%H:%M').timestamp()
    num_data = int(time_line[5])
    split = int(float(time_line[3])) * 60

    # Create the times and values
    times = np.linspace(initial_time, initial_time + (num_data-1)*split, num_data)
    values = ''.join(text[start_idx:]).split('\n')[:-1]

    # Convert to list
    times = [np.int(t) for t in times]
    values = [float(x) for x in values]

    return pd.DataFrame({'time': times, 'value': values})


# endregion -------------------------- FUNCTIONS --------------------------
