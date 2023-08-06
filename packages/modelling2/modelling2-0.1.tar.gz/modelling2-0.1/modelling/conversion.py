from modelling import *

def filter_gis(df):
    df = df.copy()
    df = df[df['SERVICE'].isin(['Local'])]
    df = df[~df['PROCESS'].isin(['Hydrant Conn', 'Service Conn', 'Sprinkler Conn'])]
    return df


def compare_df(left_df, left_key, right_df, right_key, status_key='STATUS', status_val='IN', crs=default_crs_source):
    left_df = left_df.copy()
    right_df = right_df.copy()

    left_df[left_key] = left_df[left_key].astype(str)
    right_df[right_key] = right_df[right_key].astype(str)

    merge_df = gp.GeoDataFrame(left_df.merge(right_df, how='inner', left_on=left_key, right_on=right_key))

    new_df = left_df[(~left_df[left_key].isin(right_df[right_key])) & (left_df[status_key] == status_val)]
    missing_df = right_df[~right_df[right_key].isin(left_df[left_key])]
    abandoned_df = merge_df[merge_df[status_key] != status_val]
    abandoned_df = abandoned_df.set_geometry('geometry_y').drop(columns='geometry_x')

    new_df.crs = crs
    missing_df.crs = crs
    abandoned_df.crs = crs

    return new_df, missing_df, abandoned_df


def get_consumption_fields(consumption_df, parcels_df, connection_df):
    consumption_df = consumption_df.copy()
    parcels_df = parcels_df.copy()
    connection_df = connection_df.copy()

    parcels_df = parcels_df[parcels_df['status'] == 'Current']
    connection_df.loc[:, 'ADDRKEY'] = connection_df['ADDRKEY'].astype(int).astype(str)
    connection_df = connection_df[['GIS_ID', 'ACCTNO', 'ADDRKEY']]
    consumption_df.loc[:, 'water_mete'] = consumption_df['water_mete'].astype(int).astype(str)

    consumption_merge = gp.sjoin(consumption_df, parcels_df, how='left', op='intersects')
    consumption_merge = consumption_merge.merge(connection_df, how='left', left_on='water_mete', right_on='ADDRKEY')
    consumption_merge = consumption_merge.drop_duplicates(['Account_ID'])

    consumption_merge = consumption_merge.reset_index(drop=True)
    consumption_merge['water_mete'] = consumption_merge.groupby('water_mete')['water_mete'].apply(
        lambda n: (n + '_' + (np.arange(len(n)) + 1).astype(str)) if len(n) > 1 else n)

    consumption_merge = get_consumption_demand_category(consumption_merge)

    return consumption_merge


def get_consumption_demand_category(consumption_df):
    consumption_df = consumption_df.copy()

    filename = pkg_resources.resource_filename('modelling', 'Dataframes/demand_categories.csv')
    df_demand = pd.read_csv(filename, index_col=0)

    for cl in pd.unique(consumption_df['account_cl']):
        indexes = consumption_df['account_cl'] == cl
        consumption_df.loc[indexes, 'DEMAND'] = df_demand.loc[df_demand['ACCOUNT_CLASS'] == cl, 'DEMAND_CATEGORY'].values[0]

    return consumption_df



def pipe_cw(pipes_df, material_key='MATERIAL', installed_key='INSTALLED'):
    pipes_df = pipes_df.copy()

    filename = pkg_resources.resource_filename('modelling', 'Dataframes/roughness.csv')
    df_cw = pd.read_csv(filename, index_col=0)

    # Data from Watercare
    all_materials = list(df_cw.MATERIAL)[:-1]
    age_ranges = {'AGE_1': [0, 25], 'AGE_2': [26, 40], 'AGE_3': [41, 9999]}

    pipes_df['AGE'] = dt.now().year - pipes_df[installed_key].str[:4].astype(int)
    for key, value in age_ranges.items():
        age_indexes = pipes_df['AGE'].between(value[0], value[1], inclusive=True)
        for mat in pd.unique(pipes_df[material_key]):
            mat_indexes = pipes_df[material_key] == mat

            indexes = mat_indexes & age_indexes
            if mat not in all_materials:
                mat = 'Other'
            pipes_df.loc[indexes, 'CW'] = df_cw[df_cw.MATERIAL == mat][key].values[0]

    return pipes_df


def pipe_internal_diameter(pipes_df, diameter_key='NOM_DIA_MM', material_key='MATERIAL'):
    pipes_df = pipes_df.copy()

    filename = pkg_resources.resource_filename('modelling', 'Dataframes/internal_diameters.csv')
    df_id = pd.read_csv(filename, index_col=0)

    pipes_df['INT_DIA_MM'] = pipes_df[diameter_key]
    for mat in df_id.columns:
        mat_indexes = pipes_df[material_key] == mat
        for dia in df_id.index:
            dia_indexes = pipes_df[diameter_key] == dia
            indexes = mat_indexes & dia_indexes

            if df_id.loc[dia, mat] > 0:
                pipes_df.loc[indexes, 'INT_DIA_MM'] = df_id.loc[dia, mat]

    return pipes_df
