from modelling import *
import os


#######################################################################################################################
# Calibration Plots
#######################################################################################################################

def _format_output(df, ax, outpath):
    """
    Format the calibration plots and write to a file
    :param df: DataFrame which is being plotted
    :param ax: Axes of the plot
    :param outpath:
    """

    # Move the subplot to allow for legend and title at the top of the figure
    plt.subplots_adjust(top=1.1)
    ax.legend(df.columns.get_level_values(0), loc='upper center', bbox_to_anchor=(0.5, 1.2),
              ncol=2, fancybox=True, fontsize=9)
    plt.tight_layout()

    # Turn the grid on
    ax.grid('on')

    # Output the figure
    fig = ax.get_figure()
    fig.savefig(outpath)
    plt.close(fig)


def _plot_calibration_flow(pt, name, outpath):
    """
    Plot the flow calibration and statistics. Plots are grouped by asset name, with each line being different
    gauges. Modelled data is split by the datavariabletypeid
    :param pt: Pivoted DataFrame which is being plotted
    :param name: Name of the point
    :param outpath: Output file path for the resulting plot
    """

    try:
        df = pt[(name, 'Flow')]
    except KeyError:
        return

    # Get the names of the modelled columns and the observed columns
    modcols = df.columns[df.columns.get_level_values(1) == 1841]
    obscols = df.columns[df.columns.get_level_values(1) != 1841]

    # If they dont exist return nothing
    if len(modcols) == 0 and len(obscols) == 0:
        return

    # Create plot
    fig, ax = plt.subplots()

    # Initialize max percent
    max_percent_within = 0

    # For each combination of observed and modelled data columns...
    for ocol in obscols:
        for mcol in modcols:
            maxdiff = df.loc[:, ocol].abs().max() * 0.1  # ... calculate 10% of the max flow
            percent_within = (abs(df[mcol] - df[ocol]) < maxdiff).sum() / len(df) * 100
            if percent_within > max_percent_within:
                max_percent_within = percent_within  # ... store the max percent of data which is within 10% of the max flow

    # Output and format results
    ax = df[obscols.join(modcols, how='outer')].plot(ax=ax)
    plt.suptitle('{}\n{:.0f}% percent within 10% of maximum flow'.format(name, max_percent_within), fontsize=11)
    _format_output(df, ax, outpath)


def _plot_calibration_pressure(pt, name, outpath):
    """
    Plot the pressure calibration and statistics. Plots are grouped by asset name, with each line being different
    gauges. Modelled data is split by the datavariabletypeid
    :param pt: Pivoted DataFrame which is being plotted
    :param name: Name of the point
    :param outpath: Output file path for the resulting plot
    """

    try:
        df = pt[(name, 'Pressure')]
    except KeyError:
        return

    # Get the relevant datavariabletypeid's
    modcols = df.columns[df.columns.get_level_values(1) == 11199]
    obscols = df.columns[df.columns.get_level_values(1) != 11199]

    # If they dont exist return nothing
    if len(modcols) == 0 and len(obscols) == 0:
        return

    fig, ax = plt.subplots()

    # Initialize max percent ranges
    max_percent_within = {
        1: 0,
        2: 0,
        5: 0
    }

    # For each combination of observed and modelled data columns...
    for ocol in obscols:
        for mcol in modcols:
            for pres_within in max_percent_within.keys(): # ... and each of the pressure criteria
                percent_within = (abs(df[mcol] - df[ocol]) < pres_within).sum() / len(df) * 100
                if percent_within > max_percent_within[pres_within]:
                    max_percent_within[pres_within] = percent_within # ... store the max percent of data which is within the pressure criteria

    # Output and format results
    ax = df[obscols.join(modcols, how='outer')].plot(ax=ax)
    plt.suptitle('{}\n{:.0f}% within 1m, {:.0f}% within 2m, {:.0f}% within 5m'.format(name, max_percent_within[1], max_percent_within[2], max_percent_within[5]), fontsize=11)
    _format_output(df, ax, outpath)


def calibration_plots(scenarioid, outpath, database='prod'):
    """
    Plot the calibration plots for flow and pressure along with the statistics. The resulting plots are
    output into the outpath folder with two new folders for Flow and Pressure created.
    :param scenarioid: Scenario id to plot
    :param outpath: Output file path for the resulting plot
    :param database: dev or prod
    """

    # Query to grab the data
    query = '''
    with s as (
        select * from modelling.scenario s where s.scenarioid={}
    ), mro as (
        select  
            mro.modelrunoptiontypeid,
            case 
                when mro.modelrunoptiontypeid = 9 then mro.value::int * 60 * 60 
                when mro.modelrunoptiontypeid = 10 then mro.value::int / 1000
                else mro.value::int
        	end
        from s
        join modelling.modelrunoption mro on mro.modelrunoptionsetid=s.modelrunoptionsetid
        where mro.modelrunoptiontypeid in (9, 10, 26)
    )
    select gp.name, gs.description, dvt.type, gs.datavariabletypeid, ggd.unixdatetime, ggd.value
    from modelling.geometrypointdata gp 
    join modelling.gaugesummary gs on gp.assetid=gs.assetid 
    join modelling.datavariabletype dvt on dvt.datavariabletypeid=gs.datavariabletypeid 
    join modelling.gaugedata_getgroupeddata(
        gs.gaugesummaryid, 
        (select mro.value from mro where mro.modelrunoptiontypeid = 26), 
        (select sum(mro.value) from mro where mro.modelrunoptiontypeid in (9, 26)), 
        0, 
        (select mro.value from mro where mro.modelrunoptiontypeid = 10)) ggd on 1=1 
    where gp.workid=(select s.workid from s)
    and (gs.scenarioid=(select s.scenarioid from s) or gs.scenarioid is null) 
    and dvt.type in ('Pressure', 'Flow') and dvt.datavariabletypeid != 201
    '''.format(scenarioid)

    dbdf = db.read_df(query, database=database)
    dbdf['time'] = fn.unix_to_datetime(dbdf.unixdatetime, from_tz='UTC', to_tz='UTC')

    # Create a pivot table
    pt = pd.pivot_table(dbdf, values='value', index='time',
                        columns=['name', 'type', 'description', 'datavariabletypeid']).interpolate()

    # Create the subfolders if required
    if not os.path.exists(r"{}\Flow".format(outpath)):
        os.makedirs(r"{}\Flow".format(outpath))
    if not os.path.exists(r"{}\Pressure".format(outpath)):
        os.makedirs(r"{}\Pressure".format(outpath))

    # Make sure the plot doesn't show
    plt.ioff()

    # Create plots for each point
    for name in dbdf.name.unique():
        print('Creating plots for {}...'.format(name))
        _plot_calibration_flow(pt, name, r"{}\Flow\{}.png".format(outpath, name))
        _plot_calibration_pressure(pt, name, r"{}\Pressure\{}.png".format(outpath, name))

    # Make sure the plots show again
    plt.ion()


#######################################################################################################################
# Bokeh Plots
#######################################################################################################################

def geom_bokeh_plot(dfs, outpath, **fig_kwargs):
    """
    Plot a list or single GeoDataFrame to an interactive HTML plot
    :param dfs: GeoDataFrame or list of GeoDataFrames to plot
    :param outpath: Set the output path of the plot, making sure it ends with .html
    """

    # Check the outpath is correct
    if outpath[-4:] != 'html':
        raise TypeError('File path must end with html')

    # Create a list from a GeoDataFrame
    if isinstance(dfs, gp.GeoDataFrame):
        dfs = [dfs]

    # Create the figure and fit it to the screen
    plot = bkplt.figure(match_aspect=True, **fig_kwargs)
    plot.axis.visible = False
    plot.sizing_mode = 'stretch_both'

    # Add the basemap
    prov = bktile.get_provider('CARTODBPOSITRON_RETINA')
    plot.add_tile(prov)

    # Create a list of distinct colors
    color = iter(['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c',
                  '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1',
                  '#000075', '#808080', '#ffffff', '#000000'])

    # Create a function to convert GeoDataFrames to ColumnDataSource
    points_to_bokeh = lambda gdf: bkmod.ColumnDataSource(fn.get_point_xy(gdf))
    lines_to_bokeh = lambda gdf: bkmod.ColumnDataSource(fn.get_line_xy(gdf))
    polys_to_bokeh = lambda gdf: bkmod.ColumnDataSource(fn.get_poly_xy(gdf))

    # Set the crs
    epsg = 3857

    # Loop through the list of dataframes
    for df in dfs:
        # Get a list of geometry type
        geom_types = df.geometry.type.unique()

        for gtype in geom_types:
            # Get the color to plot
            plot_color = next(color)

            if gtype in ("Point", "MultiPoint"):
                # Get the points we want to plot and convert to the proper crs
                points = df[df.geometry.type.isin(("Point", "MultiPoint"))].to_crs(epsg=epsg)
                plot.circle(x='x', y='y', source=points_to_bokeh(points), fill_color=plot_color, line_color=plot_color)

            elif gtype in ("LineString", "MultiLineString"):
                # Get the lines we want to plot and convert to the proper crs
                lines = df[df.geometry.type.isin(("LineString", "MultiLineString"))].to_crs(epsg=epsg)
                plot.multi_line(xs='x', ys='y', source=lines_to_bokeh(lines), line_color=plot_color)

            elif gtype in ("Polygon", "MultiPolygon"):
                # Get the polygons we want to plot and convert to the proper crs
                polygons = df[df.geometry.type.isin(("Polygon", "MultiPolygon"))].to_crs(epsg=epsg)
                plot.patches(xs='x', ys='y', source=polys_to_bokeh(polygons), fill_color=plot_color, line_color=plot_color)

        # Add a tool for hovering over geometry to show attributes
        hover = bkmod.HoverTool()
        hover.tooltips = [(col, '@' + col) for col in df.columns]  # show all columns
        plot.add_tools(hover)

    # Output the file
    bkplt.output_file(outpath)
    bkplt.show(plot)


def bokeh_plot(df, x, y, outpath, **fig_kwargs):
    """
    Plot a DataFrame with x as time and y as the value
    :param df: GeoDataFrame or list of GeoDataFrames to plot
    :param x: Column name for x
    :param y: Column name for y
    :param outpath: Set the output path of the plot, making sure it ends with .html
    :param fig_kwargs: Key worded arguments for bokeh figure
    """

    # Create the figure to the size of the screen
    plot = bkplt.figure(**fig_kwargs)
    plot.sizing_mode = 'stretch_both'

    # Plot the line and set the legend
    legend = x
    plot.line(source=bkmod.ColumnDataSource(df), x=x, y=y, legend_label=legend)

    # Add a tool for hovering to show attributes
    hover = bkmod.HoverTool()
    tooltip = [('Datetime', '@' + x + '{%F %T}'), ('Value', '@' + y)]
    formatter = {'datetime': 'datetime'}
    hover.tooltips = tooltip
    hover.formatters = formatter
    plot.add_tools(hover)

    # Set the legend location
    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    plot.legend.label_text_font_size = "12pt"

    # Save the plot
    bkplt.output_file(outpath)
    bkplt.show(plot)

