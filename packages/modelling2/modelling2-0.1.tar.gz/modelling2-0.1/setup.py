import setuptools

requirements = ['geopandas', 'pandas', 'datetime', 'numpy', 'gdal', 'arcgis', 'psycopg2', 'matplotlib', 'bokeh', 'geopy', 'networkx']

setuptools.setup(
    name='modelling2',
    version='0.1',
    packages=['modelling'],
    install_requires=requirements,
    url='',
    license='MIT',
    author='James Thorne',
    author_email='james.thorne@mottmac.com',
    description='Tools used for hydraulic modelling'
)
