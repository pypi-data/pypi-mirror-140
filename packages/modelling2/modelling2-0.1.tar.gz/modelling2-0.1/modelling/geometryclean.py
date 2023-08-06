from modelling import *
from shapely.geometry import LineString, MultiPoint, Point
import shapely.ops
import networkx as nx


class GISNetwork:
    def __init__(self, lines, points, point_id):
        """
        Constructor for the GISNetwork class
        :param lines: GeoDataFrame for the lines of the network
        :type lines: gp.GeoDataFrame
        :param points: GeoDataFrame for the points of the network
        :type points: gp.GeoDataFrame
        :param point_id: Unique identifier for the id of the points. Used for creating a connected network
        :type point_id: str
        :return GISNetwork:
        """

        self.lines = lines.reset_index(drop=True)
        self.lines.geometry = self.lines.geometry.apply(lambda geom: geom[0] if geom.geom_type == 'MultiLineString' else geom)

        self.point_id = point_id
        self.points = points.reset_index(drop=True)
        self.points.geometry = self.points.geometry.apply(lambda geom: geom[0] if geom.geom_type == 'MultiPoint' else geom)

        if not self.points[self.point_id].is_unique:
            raise RuntimeError('{} column is not unique'.format(self.point_id))

        self.isolated = self.points
        self.endpoints = self.lines.geometry.apply(lambda geom: MultiPoint([(geom.coords[0]), (geom.coords[-1])]))

        self.subnetworks = None
        self._update_totals()

    def connect_network(self, tol, min_lines=0):
        """
        Constructor for the GISNetwork class
        :param tol: Tolerance to split and connect lines and points
        :type tol: float
        :param min_lines: Minimum lines in a network, smaller networks are deleted.
        :type min_lines: int
        """

        print('Finding isolated endpoints:')
        self._get_sindex(tol)                       # Get spatial index of the points for speed
        self._find_isolated_endpoints(tol)          # Find isolated endpoints

        print('Creating new endpoints:')
        self._create_isolated_endpoints()           # Create endpoints on lines which aren't within distance of points
        self._get_sindex(tol)                       # Update spatial index of the points

        print('Simplifying invalid geometry:')
        self._simplify_self_intersecting_lines()    # Simplify any lines which are self intersecting

        print('Splitting lines by points:')
        self._split_lines_from_points(tol)          # Split all lines from nearest points

        print('Snapping lines to nearest points:')
        self._snap_lines_to_points(tol)             # Snap every line to the closest points and connect the network

        print('Collecting sub networks:')
        self._get_subnetworks()

        if min_lines > 0:
            print('Removing small sub networks:')
            self._remove_islands(min_lines)         # Remove any isolated networks with less than min_lines

    def plot(self):
        """
        Plots the network using bokeh. Different colors are specified for the lines, existing points, and new points.
        """

        df_list = [self.lines, self.points[~self.points[self.point_id].str.contains('MM2')], self.points[self.points[self.point_id].str.contains('MM2')]]
        mplt.geom_bokeh_plot(df_list)

    def plot_networks(self):
        """
        Plots the different subnetworks using bokeh. Different node colors are specified for each subnetwork.
        """

        df_list = []
        df_list.append(self.lines)
        for i, row in self.subnetworks.iterrows():
            df_list.append(self.points[self.points[self.point_id].isin(row.nodes)])
        mplt.geom_bokeh_plot(df_list)

    def _update_totals(self):
        """
        Update the total lines and nodes
        """
        self.total_lines = self.lines.shape[0]
        self.total_points = self.points.shape[0]

    def _find_isolated_points(self, max_distance):
        """
        Find points which are more than the max distance away from line endpoints.
        :param max_distance: Max distance to check from the line endpoints
        """
        endpoints = self.endpoints.buffer(max_distance).unary_union
        return self.points.geometry.difference(endpoints)

    def _get_sindex(self, max_distance):
        """
        Create the spatial index with the max distance as the tolerance. Used for speed
        :param max_distance: Max distance away to check from points
        """
        self.buffer_sindex = self.points.geometry.buffer(max_distance).sindex

    def _find_isolated_endpoints(self, max_distance):
        """
        Find all isolated endpoints of lines. Update the isolated attribute
        :param max_distance: Max distance away to check from points
        """

        # Get all the line endpoints
        all_endpoints = self.endpoints.unary_union
        total = len(all_endpoints)

        cnt = 0
        isolated = [] # append the points

        # Look at each point
        for endpt in all_endpoints:
            # Find the ones which are close based on the spatial index
            close_pts = self._get_close_points(endpt)

            # If the points arent within the max distance append the line endpoint to the list
            if not close_pts.empty:
                if close_pts.distance(endpt).min() > max_distance:
                    isolated.append(endpt)
            else:
                isolated.append(endpt)

            # Update the progress bar
            self._update_progress(cnt/total)
            cnt += 1

        # Update the progress bar
        self._update_progress(1)
        self.isolated = isolated

    def _create_isolated_endpoints(self):
        """
        Create points on the isolated endpoints of lines.
        """

        total = len(self.isolated)
        cnt = 0

        # Loop through each line endpoint and append it to the DataFrame.
        for pt in self.isolated:
            # Create points starting from MM2000 onwards
            df = gp.GeoDataFrame({self.point_id: ['MM' + str(cnt + 1999)]}, geometry=[pt])
            self.points = self.points.append(df, ignore_index=True, sort=False)

            # Update the progress
            self._update_progress(cnt/total)
            cnt += 1

        self._update_progress(1)
        self._update_totals()

    def _snap_lines_to_lines(self, max_distance):
        """
        Snap lines to the closest line within the max distance
        :param max_distance: Max distance to snap lines
        """
        lines_union = self.lines.geometry.unary_union
        self.lines.geometry = self.lines.geometry.apply(lambda geom: shapely.ops.snap(geom, lines_union, max_distance))

    def _get_close_points(self, geom):
        """
        Get the close points to the geometry input. This is not exact since we are using spatial indexing.
        The result may include some false positives, but will not include any false negatives.
        :param geom: Geometry to check are within the buffered points spatial index
        """
        possible_matches_index = list(self.buffer_sindex.intersection(geom.bounds))
        return self.points.iloc[possible_matches_index].geometry

    def _simplify_self_intersecting_lines(self):
        """
        Simplify lines which are self intersecting to ensure all lines are valid geometries
        :param geom: Geometry to check are within the buffered points spatial index
        """

        # Simplify the geometry, increasing the tolerance until all lines are simplified
        tol = 0.1
        self_intersecting = self.lines.loc[~self.lines.geometry.is_simple, self.lines.geometry.name].simplify(tol).copy()
        while not all(self_intersecting.is_simple):
            self_intersecting = self.lines.loc[~self.lines.geometry.is_simple, self.lines.geometry.name].simplify(tol).copy()
            tol += 0.1

        # Show a progress bar and update lines
        self._update_progress(1)
        self.lines.loc[~self.lines.geometry.is_simple, self.lines.geometry.name] = self_intersecting

    def _split_lines_from_points(self, max_distance):
        """
        Split lines by points within a distance less than the max distance
        :param max_distance: Max distance to snap lines
        """

        newlines = []
        geom_col = self.lines.geometry.name

        # loop through the lines and split all lines within the max distance
        for i, row in self.lines.iterrows():
            line = row[geom_col]

            # Create points close to the line
            buff_points = self._get_close_points(line)
            buff_points = buff_points.unary_union.buffer(max_distance * 0.8)

            # Split the line and append it to the list newlines
            newlines.append(shapely.ops.split(line, buff_points))

            # Update the progress
            progress = (i+1)/self.total_lines
            self._update_progress(progress)

        # Update the lines
        self.lines.geometry = newlines
        self.lines = self.lines.explode()
        self.lines = self.lines.reset_index(drop=True)
        self._update_totals()

    def _snap_lines_to_points(self, max_distance):
        """
        Snap lines to points within a distance less than the max distance
        :param max_distance: Max distance to snap lines
        """

        newlines = []
        geom_col = self.lines.geometry.name

        # Loop through each line
        for i, row in self.lines.iterrows():
            line = row[geom_col]
            line_coords = line.coords[:]
            end_nodes_id = [None, None]

            # Get the close points
            close_pts = self._get_close_points(line)

            # If there are close points
            if not close_pts.empty:
                # Look at both endpoints of the line
                for end in [0, -1]:
                    # Find the closest point within the max distance
                    endpoint = Point(line_coords[end])
                    dist = close_pts.distance(endpoint)

                    if dist.min() < max_distance:
                        j = dist.idxmin()

                        # Update the line endpoint to be the same as the point coord
                        closest_pt = self.points.loc[j, geom_col]
                        line_coords[end] = closest_pt.coords[0]

                        # Update the start and end point ids
                        end_nodes_id[end] = self.points.loc[j, self.point_id]

            # Update the start and end point ids on the line o create the subnetworks
            self.lines.loc[i, 'from_id'] = end_nodes_id[0]
            self.lines.loc[i, 'to_id'] = end_nodes_id[-1]

            # Update the progress
            progress = (i+1)/self.total_lines
            self._update_progress(progress)

            newlines.append(LineString(line_coords))

        # Update the geometry and remove line with the same start and endpoint
        self.lines.geometry = newlines
        self.lines = self.lines[~(self.lines.from_id == self.lines.to_id)]

    def _get_subnetworks(self):
        """
        Get all connected subnetworks after snapping lines to points
        """

        # Create a graph from the lines
        G = nx.from_pandas_edgelist(self.lines, 'from_id', 'to_id')

        # Create a set of all the nodes
        all_nodes = set(G.nodes)
        total = len(all_nodes)

        cols = ['nodes', 'num_nodes', 'edges', 'num_edges']
        subnetworks = pd.DataFrame(columns=cols)

        # Do until we have no more nodes left in the set
        while len(all_nodes) > 0:
            # Get a random node from the set
            for x in all_nodes:
                rand_node = x
                break

            # Get the connected nodes and edges
            tree = nx.algorithms.bfs_tree(G, rand_node)

            ids_from_nodes = set([node for node in tree.nodes])
            ids_from_edges = set([edge for edge in tree.edges])

            # Append the subnetwork nodes and edges
            subnetworks = subnetworks.append(
                pd.Series([list(ids_from_nodes), len(ids_from_nodes), list(ids_from_edges), len(ids_from_edges)],
                          index=cols), ignore_index=True)

            # Remove the nodes in the network from the set
            all_nodes.difference_update(ids_from_nodes)

            # Update the progress
            progress = (total - len(all_nodes))/total
            self._update_progress(progress)

        self.subnetworks = subnetworks

    def _remove_islands(self, max_lines):
        """
        Get small subnetworks less the max_lines in size
        :param max_lines: Maximum number of subnetwork edges for which to remove
        """

        # Get the subnetworks with less than max_lines edges
        self.subnetworks = self.subnetworks[self.subnetworks.num_edges <= max_lines]

        # Get the nodes and edges to remove
        nodes_to_remove = [inner for outer in self.subnetworks.nodes.values for inner in outer]
        edges_to_remove = [inner for outer in self.subnetworks.edges.values for inner in outer]
        edges_to_remove = list(map(list, zip(*edges_to_remove)))

        # Remove nodes attached to lines
        to_keep = ~self.points[self.point_id].isin(nodes_to_remove)
        self.points = self.points[to_keep]

        # Remove isolated nodes
        to_keep = self.points[self.point_id].isin(self.lines.from_id.append(self.lines.to_id, ignore_index=True))
        self.points = self.points[to_keep]

        # Remove edges
        to_keep = ~(((self.lines.from_id.isin(edges_to_remove[0])) & (self.lines.to_id.isin(edges_to_remove[1]))) |
                    ((self.lines.from_id.isin(edges_to_remove[1])) & (self.lines.to_id.isin(edges_to_remove[0]))))
        self.lines = self.lines[to_keep]

        # Update the progress
        self._update_progress(1)

    @staticmethod
    def _update_progress(progress):
        """
        Create and update the progress bar
        :param progress: Percent of progress from 0-1
        """

        # Modify this to change the length of the progress bar
        bar_length = 30
        status = ""

        # Update int to float
        if isinstance(progress, int):
            progress = float(progress)

        # Handle when progress is not between 0 and 1, or is not a number
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"

        # Create the bar length
        block = int(round(bar_length * progress))

        # Create the text and update the previous line
        text = "Percent: [{0}] {1}% {2}".format("#" * block + "-" * (bar_length - block), progress * 100, status)
        print(text, end='\r')

    def meters_to_closest_point_on_lines(self, meters, max_distance):
        """
        NOT FULLY TESTED
        Find the closest node to a meter, by first finding the closest line then the closest node.
        :param meters: GeoDataFrame with the meters
        :param max_distance: Max distance to search
        """

        self._get_sindex(max_distance)
        line_si = self.lines.geometry.buffer(0.01).sindex
        line_unary = self.lines.unary_union

        meters['closest_point_id'] = None
        for i, row in meters.iterrows():
            meter = row.geometry

            point_on_line = line_unary.interpolate(line_unary.project(meter))
            possible_matches_index = list(line_si.intersection(point_on_line.bounds))
            closest_pipe_idx = self.lines.iloc[possible_matches_index].geometry.distance(meter).idxmin()

            # closest_pipe_idx = self.lines.geometry.distance(meter).idxmin()

            line = self.lines.loc[closest_pipe_idx, self.lines.geometry.name]
            line_coords = line.coords[:]

            dist = [meter.distance(Point(line_coords[end])) for end in [0, -1]]
            closest_endpoint = dist.index(min(dist)) * -1
            endpoint = Point(line_coords[closest_endpoint])

            close_pts = self._get_close_points(endpoint)
            dist = close_pts.distance(endpoint)
            if dist.min() < max_distance:
                j = dist.idxmin()
                meters.loc[i, 'closest_point_id'] = self.points.loc[j, self.point_id]

        meters = meters.merge(self.points, how='left', left_on='closest_point_id', right_on=self.point_id)

        return meters

    def create_unique_names(self, line_id, field_name='name'):
        """
        Create unique names for the lines
        :param line_id: Column to create unique id for in the lines
        :param field_name: The new name of the field created
        """
        self.lines[field_name] = self.lines.groupby(line_id)[line_id].apply(
            lambda ids: (ids + '_' + (np.arange(len(ids)) + 1).astype(str)) if len(ids) > 1 else ids)

