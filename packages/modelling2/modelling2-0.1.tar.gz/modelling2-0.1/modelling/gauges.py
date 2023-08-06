from modelling import *

class Gauges:
    def __init__(self, gaugesummaryids, subzoneassetids=None, between_unix=[0, 1e10], plottype='bokeh',
                 unix_tz=['UTC', 'NZ'], statistictype=None, database='prod'):
        if subzoneassetids is None:
            self.points = self.get_points(gaugesummaryids)
            self.subzones = None
        else:
            self.subzones = self.get_subzones(subzoneassetids)
            self.points = gp.sjoin(self.get_points(gaugesummaryids), self.subzones, lsuffix='point', rsuffix='zone')
        self.ids = self.points.index.values
        self.data = None
        self.dataids = None
        self.times = between_unix
        self.plottype = plottype
        self.timezones = unix_tz
        self.database = database

        self.statistictype = statistictype

        self.get_data_type()

    def get_points(self, gaugesummaryids):
        query = """select gs.gaugesummaryid, gs.description as gaugedescription, gs.datavariabletypeid, gs.resolution, a.* from gaugesummary gs 
        join asset a on gs.assetid=a.assetid
        where gs.gaugesummaryid in (%s)""" % str(gaugesummaryids)[1:-1]

        points = db.read_df(query, database=self.database)
        points['gaugesummaryid'] = points['gaugesummaryid'].astype(int)
        points = points.set_index('gaugesummaryid')
        return points

    def get_subzones(self, assetids):
        query = """select * from asset a
        where a.assetid in (%s)""" % str(assetids)[1:-1]

        subzones = db.read_df(query, database=self.database)
        return subzones

    # def get_excel_elevation(self, sheet, gauge_key):
    #     # Compare survey and lidar
    #     df = pd.read_excel(
    #         r"C:\Users\THO88602\Mott MacDonald\Watercare Model Conversion - Data Collection\2019-04-30 Field Test Results\2019-06-10 Hibiscus Final Download\Hibiscus Survey Results.xlsx",
    #         sheet_name=sheet)
    #     df[gauge_key] = df[gauge_key].astype(int)
    #     df = df.set_index(gauge_key)
    #
    #     self.points['elevation'] = df['Elevation'] - df['Dip mm']/1000

    # def get_data_head(self):
    #     print('Getting Data Head...')
    #     query = """select gs.gaugesummaryid, ad.value as elevation, ad.assetdatasourceid, ads.rank from modelling.assetdata ad
    #         join modelling.assetdatasource ads on ad.assetdatasourceid=ads.assetdatasourceid
    #         join modelling.assetrelationship ar on ad.assetid=ar.relatedassetid
    #         join modelling.gaugesummary gs on gs.assetid=ar.assetid
    #         where ad.assetdatatypeid=11 and ar.assetrelationshiptypeid=3 and gs.gaugesummaryid in """ + fn.id_to_string(self.dataids)
    #
    #     df = fn.postgres_to_df(query, has_geometry=False)
    #     df = df.set_index('gaugesummaryid')
    #
    #     for gaugesummaryid in self.dataids:
    #         try:
    #             elevation = df.loc[gaugesummaryid, :].reset_index()
    #             elevation = elevation.loc[elevation['rank'].idxmin(), 'elevation'].squeeze()
    #             self.data.loc[gaugesummaryid, 'value'] = self.data.loc[gaugesummaryid, 'value'] + elevation
    #         except:
    #             print(str(gaugesummaryid) + ' has no elevation.')

    def get_data_type(self):
        print('Getting Data Types...')
        query = """select gs.gaugesummaryid, dvt.type, dvu.unitlabel from modelling.gaugesummary gs
            join modelling.datavariabletype dvt
            on gs.datavariabletypeid=dvt.datavariabletypeid
            join modelling.datavariableunit dvu
            on dvt.datavariableunitid=dvu.datavariableunitid
            where gs.gaugesummaryid in """ + fn.id_to_string(self.ids)

        df = db.read_df(query, database=self.database)
        df = df.set_index('gaugesummaryid')

        self.points['datatype'] = df['type']
        self.points['dataunit'] = df['unitlabel']

    def get_data(self):
        print('Getting Data...')
        if self.dataids is None:
            self.dataids = self.ids

        query = ''
        for id in self.dataids:
            query += 'select * from modelling.gaugedata_getgroupeddata({0}, {1}, {2}, 2, {3}) union '.format(int(id), int(self.times[0]), int(self.times[1]), int(self.points.loc[id, 'resolution']))
        query = query[:-6] + 'order by gaugesummaryid, unixdatetime;'

        df = db.read_df(query, database=self.database)
        if ~df.empty:
            df['gaugesummaryid'] = df['gaugesummaryid'].astype(int)
            df['datetime'] = pd.DatetimeIndex(pd.to_datetime(df['unixdatetime'], unit='s')).tz_localize(self.timezones[0]).tz_convert(self.timezones[1])
            # df = df[df['value'] > 0]
            df = df.set_index('gaugesummaryid')


            self.data = df
            self.dataids = self.data.index.unique()

    # def convert_data_unit(self):
    #     print('Converting Units...')
    #     if self.conversion:
    #         for gaugesummaryid in self.dataids:
    #             self.data['value'] = self.data['value'] * self.points.loc[gaugesummaryid, 'baseunitconversion']

    def plot_gauges_bokeh(self, path, name):
        print('Creating %s Plot' % name)

        # x_range=(1558699200000, 1559304000000), y_range=(0, 80)

        color = iter(['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000'])
        plot = bkplt.figure(name=name, title=name, x_axis_type='datetime', x_axis_label='Date')
        plot.title.text_font_size = '24pt'

        plot.xaxis.axis_label_text_font_size = "20pt"
        plot.xaxis.major_label_text_font_size = "16pt"
        plot.yaxis.axis_label_text_font_size = "20pt"
        plot.yaxis.major_label_text_font_size = "16pt"
        plot.sizing_mode = 'stretch_both'

        if self.data is None:
            self.get_data()

        legendkey = 'gaugedescription'

        for gaugesummaryid in self.dataids:
            point = self.points.loc[gaugesummaryid, :]
            point = point.loc[~point.index.duplicated(keep='first')].squeeze()
            df = self.data.loc[gaugesummaryid, :].copy()

            plot.yaxis.axis_label = '%s (%s)' % (point['datatype'], point['dataunit'])
            legend = point[legendkey]

            df['gaugename'] = legend

            plot.line(source=bkmod.ColumnDataSource(df), x='datetime', y='value', color=next(color), legend=legend)

        hover = bkmod.HoverTool()
        tooltip = [('Gauge', '@gaugename'), ('Datetime', '@datetime{%F %T}'), ('Value', '@value')]
        formatter = {'datetime': 'datetime'}
        hover.tooltips = tooltip
        hover.formatters = formatter
        plot.add_tools(hover)

        plot.legend.location = "top_left"
        plot.legend.click_policy = "hide"
        plot.legend.label_text_font_size = "12pt"

        print('Saving %s Plot' % name)

        bkplt.output_file(path + '\\' + name + '.html')
        bkplt.save(plot, path + '\\' + name + '.html')

    def plot_gauges_matplotlib(self, path, name):
        print('Creating %s Plot' % name)

        # x_range=(1558699200000, 1559304000000), y_range=(0, 80)

        color = iter(['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000'])
        fig, ax = plt.subplots()
        ax.set_title(name)

        if self.data is None:
            self.get_data()

        legendkey = 'gaugedescription'

        for gaugesummaryid in self.dataids:
            point = self.points.loc[gaugesummaryid, :]
            point = point.loc[~point.index.duplicated(keep='first')].squeeze()
            df = self.data.loc[gaugesummaryid, :].copy()

            ax.set_ylabel('%s (%s)' % (point['datatype'], point['dataunit']))
            ax.set_xlabel('Datetime')
            legend = point[legendkey]

            df['gaugename'] = legend
            df.plot.line(ax=ax, x='datetime', y='value', color=next(color), label=legend)

        stat = self.get_statistic(ax)


        print('Saving %s Plot' % name)
        plt.savefig(path + '\\' + name + '.png')
        plt.close(fig)

    def get_statistic(self, ax):
        pts = self.points.loc[self.dataids, :]
        if self.statistictype == 'calflow':
            monitor_gaugesummaryid = pts[pts.datavariabletypeid!=1841].index
            modelled_gaugesummaryid = pts[pts.datavariabletypeid==1841].index

            monitor_data = self.data.loc[monitor_gaugesummaryid, 'value']
            modelled_data = self.data.loc[modelled_gaugesummaryid, 'value']
            if not monitor_data.empty and not modelled_data.empty:
                diff_data = monitor_data.reset_index(drop=True) - modelled_data.reset_index(drop=True)
                stat = 1 - sum(diff_data.abs() >= monitor_data.abs().max()*0.1)/len(monitor_data)

                ax.text(0.03, -0.25, '{}% of the data is within 10% of the maximum monitored value'.format(int(stat * 100)),
                        transform=ax.transAxes)
        elif self.statistictype == 'calpressure':
            monitor_gaugesummaryid = pts[pts.datavariabletypeid != 11199].index
            modelled_gaugesummaryid = pts[pts.datavariabletypeid == 11199].index

            monitor_data = self.data.loc[monitor_gaugesummaryid, 'value']
            modelled_data = self.data.loc[modelled_gaugesummaryid, 'value']
            if not monitor_data.empty and not modelled_data.empty:
                diff_data = monitor_data.reset_index(drop=True) - modelled_data.reset_index(drop=True)
                stat = sum(diff_data.abs() <= 1) / len(monitor_data)

                ax.text(0.03, -0.25, '{}% of modelled pressure within 1m'.format(int(stat * 100)),
                        transform=ax.transAxes)

        return None

    def plot_subzone_gauges(self, path):
        if self.subzones is None:
            print("Subzone not specified")
            return

        for i, zone in self.subzones.iterrows():
            zone_name = zone['name']
            self.dataids = self.points[self.points['name_zone'] == zone_name].index.values
            self.get_data()
            if len(self.dataids) > 0:
                if self.plottype == 'bokeh':
                    self.plot_gauges_bokeh(path, zone_name)
                elif self.plottype == 'matplotlib':
                    self.plot_gauges_matplotlib(path, zone_name)

    def plot_assetid_gauges(self, path):
        assetkey = 'assetid'
        namekey = 'name'
        if self.subzones is not None:
            assetkey += '_point'
            namekey += '_point'

        for assetid in self.points[assetkey].unique():
            self.dataids = self.points[self.points[assetkey] == assetid].index.values
            self.get_data()
            if len(self.dataids) > 0:
                if self.plottype == 'bokeh':
                    self.plot_gauges_bokeh(path, self.points.loc[self.dataids, namekey].unique()[0])
                elif self.plottype == 'matplotlib':
                    self.plot_gauges_matplotlib(path, self.points.loc[self.dataids, namekey].unique()[0])
