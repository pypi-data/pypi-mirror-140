# output : pd.DataFrame
# index : datetime
# dtype : float64

# from datetime import datetime, date, time, timedelta
# from dateutil.parser import parse
# from pytz import timezone, utc
# from collections import namedtuple
# from .applications import *
# from .subclass import *


# import json
# import requests
# import numpy as np
# import pandas as pd
# import os
# from .settings import *


class Jaye:
    def __init__(self):
        self.account = account(self)
        self.analysis = analysis()
        self.trade = {}
        self.simulation = simulation()
        self.version = '0.0.9'



