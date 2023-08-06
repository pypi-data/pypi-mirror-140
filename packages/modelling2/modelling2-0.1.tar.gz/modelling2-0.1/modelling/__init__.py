import geopandas as gp
import pandas as pd
import numpy as np
import pkg_resources
from datetime import datetime as dt

import bokeh.tile_providers as bktile
import bokeh.plotting as bkplt
import bokeh.models as bkmod
import bokeh.io as bkio

import matplotlib.pyplot as plt

import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

default_crs_source = '+proj=tmerc +lat_0=0 +lon_0=173 +k=0.9996 +x_0=1600000 +y_0=10000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs' # EPSG 2193

# Import modules
import modelling.functions as fn
import modelling.database as db
import modelling.gauges as cl
import modelling.plotting as mplt
import modelling.geometryclean as st