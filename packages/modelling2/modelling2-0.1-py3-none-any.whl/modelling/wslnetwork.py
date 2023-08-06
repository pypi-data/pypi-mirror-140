from modelling import *
try:
    from arcgis.geometry import Polygon, filters
    from arcgis.features import FeatureLayer
    from shapely.geometry import LineString, Polygon, Point
except ImportError as e:
    raise ImportError('To collect Watercare GIS install the arcgis module')


class Network:
    def __init__(self, df_type, zone, drop_shape):
        self.df_type = df_type
        self.zone = zone
        self.drop = drop_shape
        self.server = "https://wslgis.water.co.nz/arcgis/rest/services/Services/WaterLT/MapServer/"

    def web_to_sdf(self, url, where):
        flayer = FeatureLayer(url)

        if not self.zone.empty:
            zone_polygon = {"rings": [list([list(pt) for pt in self.zone.geometry.unary_union.exterior.coords])],
                            "spatialReference": {'wkid': 2193, 'latestWkid': 2193}}
            result = flayer.query(where=where, geometry_filter=filters.intersects(zone_polygon))
            if len(result) > 0:
                sdf = result.sdf
            else:
                sdf = None
        else:
            sdf = flayer.query(where=where).sdf
        return sdf

    def sdf_to_df(self, sdf):
        df = sdf.copy()
        first_shape_keys = sdf.SHAPE[0].keys()

        if 'x' in first_shape_keys and 'y' in first_shape_keys:
            df['geometry'] = df.apply(lambda row: Point((row.SHAPE['x'], row.SHAPE['y'])), axis=1)
        elif 'paths' in first_shape_keys:
            df['geometry'] = df.apply(lambda row: LineString(row.SHAPE['paths'][0]), axis=1)
        elif 'rings' in first_shape_keys:
            df['geometry'] = df.apply(lambda row: Polygon(row.SHAPE['rings'][0]), axis=1)

        if self.df_type == 'geopandas':
            df = gp.GeoDataFrame(df, geometry='geometry')
        elif self.df_type == 'pandas':
            df = pd.DataFrame(df)

        if self.drop:
            df = df.drop(labels=['SHAPE'], axis=1)

        return df

    def web_to_df(self, url, where):
        df = self.web_to_sdf(url=url, where=where)
        if df is not None:
            df = self.sdf_to_df(sdf=df)
        return df


class LocalNetwork(Network):
    def __init__(self, df_type='geopandas', zone=gp.GeoDataFrame(), drop_shape=True):
        super().__init__(df_type, zone, drop_shape)

    def valves(self, where="1=1"):
        return super().web_to_df(url=self.server + "1", where=where)

    def hydrants(self, where="1=1"):
        return super().web_to_df(url=self.server + "2", where=where)

    def fittings(self, where="1=1"):
        return super().web_to_df(url=self.server + "3", where=where)

    def meters(self, where="1=1"):
        return super().web_to_df(url=self.server + "4", where=where)

    def pipes(self, where="1=1"):
        return super().web_to_df(url=self.server + "5", where=where)

    def structures(self, where="1=1"):
        return super().web_to_df(url=self.server + "6", where=where)

    def pumpstations(self, where="1=1"):
        return super().web_to_df(url=self.server + "7", where=where)

    def reservoirs(self, where="1=1"):
        return super().web_to_df(url=self.server + "8", where=where)


class TransmissionNetwork(Network):
    def __init__(self, df_type='geopandas', zone=gp.GeoDataFrame(), drop_shape=True):
        super().__init__(df_type, zone, drop_shape)

    def valves(self, where="1=1"):
        return super().web_to_df(url=self.server + "10", where=where)

    def fittings(self, where="1=1"):
        return super().web_to_df(url=self.server + "11", where=where)

    def meters(self, where="1=1"):
        return super().web_to_df(url=self.server + "12", where=where)

    def pipes(self, where="1=1"):
        return super().web_to_df(url=self.server + "13", where=where)

    def structures(self, where="1=1"):
        return super().web_to_df(url=self.server + "14", where=where)

    def pumpstations(self, where="1=1"):
        return super().web_to_df(url=self.server + "15", where=where)

    def reservoirs(self, where="1=1"):
        return super().web_to_df(url=self.server + "16", where=where)

    def treatments(self, where="1=1"):
        return super().web_to_df(url=self.server + "17", where=where)

    def sources(self, where="1=1"):
        return super().web_to_df(url=self.server + "18", where=where)

