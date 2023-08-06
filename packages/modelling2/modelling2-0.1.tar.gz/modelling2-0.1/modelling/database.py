from modelling import *
import psycopg2 as pg
import shapely.wkb as swkb
import shapely.geos as geos


def _connect(database):
    """
    Connects to the database using your credentials
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :return: Connection to the database
    :rtype: pg.connection object
    """

    username = "james_thorne"
    password = "jbTOpx5VQ16PmMAramc4Z1aItQINNfO3gLAphrvMKbjXWVK9qZ"

    if database not in ['dev', 'prod']:
        raise ConnectionError('Database name must be dev or prod')

    # Connect to the database
    return pg.connect(user=username,
                     password=password,
                     host=database + ".db-postgres.h2knowhow.com",
                     port="5432",
                     database="modelling",
                     application_name="Python Modelling Package")


def get_geometry_col(df):
    """
    Gets the geometry column from a dataframe based off of the name
    :param df: Dataframe to search for column
    :type df: pd.DataFrame
    :return: Column name of geometry
    :rtype: str
    """

    # Drop empty columns
    df = df.dropna(axis=1)

    # Look for columns with shape or geometry in them
    geom_cols = [col
                 for col in df.columns
                 for geom in ['geometry', 'shape']
                 if col.find(geom) >= 0]

    # Return the first valid column with those names
    for col in geom_cols:
        try:
            int(str(df.iloc[0][col]), 16)
            return col
        except ValueError:
            pass

    # If no columns are valid return None
    return None


def _create_geodataframe(df):
    """
    Create a geodataframe if we have geometry
    :param df: DataFrame to convert to GeoDataFrame if possible
    :type df: pd.DataFrame
    :return: Dataframe with geometry or not
    :rtype: pd.DataFrame if no geometry, gp.GeoDataFrame if has geometry
    """

    # Get the geometry column based off the the column names
    geom_col = get_geometry_col(df)

    # If a geometry column is not found return the same Dataframe
    if geom_col is None:
        return df

    # If a geometry column is found convert it to a GeoDataFrame
    # convert geom col to shapely geometry
    df[geom_col] = df[geom_col].apply(lambda g: swkb.loads(str(g), hex=True))
    srid = geos.lgeos.GEOSGetSRID(df[geom_col].iat[0]._geom)

    # if no defined SRID in geodatabase, returns SRID of 0
    crs = None
    if srid != 0:
        crs = "epsg:{}".format(srid)
    return gp.GeoDataFrame(df, crs=crs, geometry=geom_col)


def read_df(query, database='dev'):
    """
    Read query from database to a dataframe
    :param query: Query to execute on the database
    :type query: str
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :return: Dataframe read from the database
    :rtype: pd.DataFrame if no geometry, gp.GeoDataFrame if has geometry
    """

    # Clean up the query
    query = query.replace('\n', ' ').replace('\t', ' ')

    # Connect to the database
    con = _connect(database)

    try:
        # Read the query using pandas
        df = pd.read_sql(query, con)
        df = _create_geodataframe(df)
        return df
    except (Exception, pg.Error) as error:
        print("Error:", error)
    finally:
        con.close()


def _get_indices(word, word_list):
    return [i for i, x in enumerate(word_list) if x == word]


def get_tables(query):
    tables = []
    words = [w for w in query.split(' ') if w != '']
    for kw in ['from', 'update', 'into', 'join']:
        for i in _get_indices(kw, words):
            tables.append(words[i + 1])
    return tables


def get_table(query):
    """
    Return the first table name in query
    :param query: Query to execute on the database
    :type query: str
    :return: Table name from the database
    :rtype: str
    """

    words = list(filter(None, query.replace('\n', ' ').replace('\t', ' ').split(' ')))
    if words[0].lower() == 'insert':
        return words[words.index('into') + 1]
    elif words[0].lower() in ('select', 'delete'):
        return words[words.index('from') + 1]
    elif words[0].lower() == 'update':
        return words[words.index('update') + 1]
    raise KeyError('query does not start with "select, "delete", "update", or "insert"')


def get_table_columns(table):
    """
    Get the columns of a specific table
    :param table: Table name from the database
    :type table: str
    :return: Columns from the specified table
    :rtype: list
    """
    return read_df("select * from " + table + " limit 1;").columns


def _create_insert(df, table, insert_pk=False):
    """
    Create a sql insert statement for a dataframe. The columns of the DataFrame must be exactly the same as the
    columns to insert into the database table.
    :param df: Dataframe to write to the database
    :type df: pd.DataFrame if no geometry, gp.GeoDataFrame if has geometry
    :param table: Table name from the database
    :type table: str
    :param insert_pk: Insert the pk of the table
    :type insert_pk: bool
    :return: SQL insert query
    :rtype: str
    """

    df = df.copy()

    # Get the table columns
    table_cols = get_table_columns(table)
    unknown_cols = [col for col in df.columns if col not in table_cols]

    if len(unknown_cols) > 0:
        # Check all the columns are in the table
        raise KeyError('{} not in {}'.format(unknown_cols, table))
    elif not insert_pk:
        # Check if we are trying to insert the pk
        if len([col for col in df.columns if col in table_cols[0]]) > 0:
            raise KeyError('Cannot insert pk {}'.format(table_cols[0]))

    # Create the insert for the string columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = "'" + df[col].astype(str) + "'"

    # Create the insert for the geometry column
    if hasattr(df, 'geometry'):
        geom_name = df.geometry.name
        srid = geos.lgeos.GEOSGetSRID(df[geom_name].iat[0]._geom)
        df[geom_name] = df.geometry.apply(lambda geom: "ST_GeometryFromText('{}', {})".format(str(geom), srid))

    # Create the insert for the datetime columns
    for col in df.select_dtypes(include='datetime').columns:
        if col in ['lastmodified', 'whencreated']:
            df[col] = "now()"

    # Create the insert statement
    sql_insert = "insert into " + table + " (" + ','.join(df.columns) + ") values \n"
    sql_insert += "(" + df.to_csv(header=False, index=False).replace('\r\n', '),\n(')[:-3] + ";"
    sql_insert = sql_insert.replace('"', '')
    sql_insert = sql_insert.replace("'None'", "NULL")

    return sql_insert


def _write_insert(query, get_result=False, database='dev'):
    """
    Write sql insert from _create_insert to the database
    :param query: Query to write to the database
    :type query: str
    :param get_result: Return the results into a DataFrame
    :type get_result: bool
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :return: Columns from the specified table
    :rtype: list
    """

    # Clean up the query
    query = query.replace('\n', ' ').replace('\t', ' ')

    # Make sure the first word is insert because we are executing query directly
    firstword = list(filter(None, query.replace('\n', ' ').replace('\t', ' ').split(' ')))[0]
    if firstword.lower() != 'insert':
        raise RuntimeError('First work of statement must be "insert"')

    # Initialise
    result = None

    # Return all results
    if get_result:
        if query[-1] == ';':
            query = query[:-1]
        query += ' returning *;'

    # Connect to the db
    con = _connect(database)

    try:
        # Execute the query directly
        cursor = con.cursor()
        cursor.execute(query)

        # Get the results and write to a dataframe
        if get_result:
            table = get_table(query)
            result = cursor.fetchall()
            result = pd.DataFrame(result, columns=get_table_columns(table))
            result = _create_geodataframe(result)

        # Commit if all succeeds
        con.commit()
    except (Exception, pg.Error) as error:
        con.rollback()
        print("Error:", error)
    finally:
        con.close()
        return result


def write_df(df, table, database='dev', get_result=False, insert_pk=False,
             has_conflict=False, on_conflict=' on conflict do nothing;'):
    """
    Create sql insert from dataframe and write to the database. Columns must match the table.
    :param df: Dataframe to write to the database
    :type df: pd.DataFrame or gp.GeoDataFrame
    :param table: Table to insert into
    :type table: str
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :param get_result: Return the results into a DataFrame
    :type get_result: bool
    :param insert_pk: Insert the primary key into the database
    :type insert_pk: bool
    :param has_conflict: If query has conflict, append the param on_conflict
    :type has_conflict: bool
    :param on_conflict: the on conflict statement to append
    :type on_conflict: str
    """

    query = _create_insert(df, table, insert_pk=insert_pk)
    if has_conflict:
        query = query[:-1] + on_conflict
    _write_insert(query, get_result=get_result, database=database)


def transfer(query, table, from_db='prod', to_db='dev', has_conflict=False, on_conflict=' on conflict do nothing;',
             insert_pk=False):
    """
    Transfer query from one database to another
    :param query: Query to transfer to the database
    :type query: str
    :param table: The name of the table
    :type table: str
    :param from_db: The name of the database to move from
    :type from_db: str
    :param to_db: The name of the database to move to
    :type to_db: str
    :param has_conflict: If query has conflict, append the param on_conflict
    :type has_conflict: bool
    :param on_conflict: the on conflict statement to append
    :type on_conflict: str
    :param insert_pk: Insert the primary key into the database
    :type insert_pk: bool
    """

    # Check if valid databases
    if from_db == to_db:
        raise ConnectionError('From and to database must be different')

    # Read the dataframe
    df = read_df(query, database=from_db)

    # Drop the primary key
    if not insert_pk:
        df = df.drop(df.columns[0], axis=1)

    # Write the dataframe
    write_df(df, table, database=to_db, has_conflict=has_conflict, on_conflict=on_conflict, insert_pk=insert_pk)


def name_to_assetid(series, assettypeids, workid=None, scenarioid=None, scenariocomponenttype=1, database='dev'):
    """
    Get the assetid from the name using the scenarioid, assettypeid, and/or workid
    :param series: Series with the names of the assets
    :type series: pd.Series
    :param assettypeids: Asset type ids to search
    :type assettypeids: List, str, or int
    :param workid: Workid to search. IF a scenarioid is specified, use that instead
    :type workid: str or int
    :param scenarioid: Scenarioid to search for MODELLED assets
    :type scenarioid: str or int
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    """

    # Check the inputs are specified
    if workid is None and scenarioid is None:
        raise RuntimeError('workid or scenarioid must be specified')

    # Join the list to a string for the sql query
    if isinstance(assettypeids, list):
        assettypeids = ','.join(assettypeids)

    # Get list of names and change series type
    series = series.astype(str)
    names = series.to_csv(header=False, index=False).replace('\r\n', "','")[:-3]

    if scenarioid is not None:
        # Get modelled assets in a scenario
        query = """
        select distinct on (d.assetid, d.assetdatatypeid) 
            a.*
        from modelling.assetdata d
        inner join modelling.asset a on 
            a.assetid = d.assetid
        inner join modelling.assetassettype aat on 
            aat.assetid = d.assetid
        inner join modelling.assetdatasource s on 
            s.assetdatasourceid = d.assetdatasourceid
        inner join modelling.getscenariocomponentpath({0}, {1}) p on 
            p.scenariocomponentid = d.scenariocomponentid 
        where a.workid = (select s.workid from modelling.scenario s where s.scenarioid={0}) 
        and aat.assettypeid in ({2}) and d.use and d.assetdatatypeid = 20 and d.value = 1
        and a.names in ('{3}')
        order by d.assetid asc, d.assetdatatypeid asc, p.distance asc, s.rank asc;""".format(
            scenarioid,
            scenariocomponenttype,
            assettypeids,
            names
        )
    else:
        # Look at all assets in the workid
        query = """
        select a.assetid, a.name from modelling.asset a 
        join modelling.assetassettype aat on 
            a.assetid=aat.assetid
        where a.workid={0} and aat.assettypeid in ({1}) and a.name in ('{2}');""".format(
            workid,
            assettypeids,
            names
        )

    # Create the resulting series
    res = pd.DataFrame({'sidx': series.index}, index=series)

    # Read the query results from the database
    df = read_df(query, database=database).set_index('name')

    # Get the assetid from the name (matching the dataframe index)
    res['assetid'] = df.assetid
    res = res.set_index('sidx')
    return res.assetid


def insert_fireflow(success_file, scenarioid, database='dev', hydrant_col='Hydrant',
                    result_col='PassedFireclass'):
    """
    Insert fireflow results from the azure model runner.
    :param success_file: File path for the fireflow results
    :type success_file: str
    :param scenarioid: Scenarioid to check the hydrant names
    :type scenarioid: int
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :param hydrant_col: Name of the column with the hydrant name in the success_file
    :type hydrant_col: str
    :param result_col: Name of the column with the result in the success_file
    :type result_col: str
    """

    # Available classes
    classdict = {
        'Failed FW2-1': 0,
        'FW2-1': 1,
        'FW2': 2,
        'FW3': 3,
        'FW4': 4,
        'FW5': 5,
        'FW6': 6
    }

    # Read the file
    df = pd.read_csv(success_file)
    df = df.drop_duplicates(hydrant_col)

    # Populate the columns to insert
    df['assetid'] = name_to_assetid(df[hydrant_col], 505, scenarioid=scenarioid, database=database)
    df['scenarioid'] = scenarioid
    df['resulttypeid'] = 304
    df['value'] = df[result_col].apply(lambda f: classdict[f])

    # Drop unused data
    df = df.dropna()
    df = df[df.columns[-4:]]

    # Write the results
    write_df(df, 'modelling.result', database=database, has_conflict=True,
             on_conflict=' on conflict (scenarioid, assetid, resulttypeid) do update set value=excluded.value;')


def insert_pipebreak(success_file, scenarioid, database='dev', pipe_col='Pipe',
                    result_col='CustomersAffected'):
    """
    Insert pipebreak results from the azure model runner.
    :param success_file: File path for the fireflow results
    :type success_file: str
    :param scenarioid: Scenarioid to check the pipe names
    :type scenarioid: int
    :param database: The name of the database to connect to (dev, prod)
    :type database: str
    :param pipe_col: Name of the column with the pipe name in the success_file
    :type pipe_col: str
    :param result_col: Name of the column with the result in the success_file
    :type result_col: str
    """

    # Read the file
    df = pd.read_csv(success_file)
    df.drop_duplicates(pipe_col)

    # Populate the columns to insert
    df['assetid'] = name_to_assetid(df[pipe_col], 3, scenarioid=scenarioid, database=database)
    df['scenarioid'] = scenarioid
    df['resulttypeid'] = 305
    df['value'] = df[result_col]

    # Drop unused data
    df = df.dropna()
    df = df[df.columns[-4:]]

    # Write the results
    write_df(df, 'modelling.result', database=database, has_conflict=True,
             on_conflict=' on conflict (scenarioid, assetid, resulttypeid) do update set value=excluded.value;')

