# output : pd.DataFrame
# index : datetime
# dtype : float64
# from .subclass import acct, comm, company
# from .Jaye import *
from .settings import BASE_URL_PUBLIC, BASE_URL_ACCOUNT
from collections import namedtuple
from rich.console import Console
from time import sleep

from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
from pytz import timezone, utc

import numpy as np
import pandas as pd
import requests
import json
import os


class Cash:
    def __init__(self):
        self.tx = pd.DataFrame()
        self.token = ""

    def balance(self):
        url = BASE_URL_ACCOUNT + "/cash/balance/"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        return response.json()

    def transaction(self):
        return self.tx


class Account:
    def __init__(self,jaye):
        self.cash = Cash()
        self.is_login = False
        self.myinfo = {}
        self.jaye = jaye
        self.token = ""

    def login(self, jaye_account,password):
        # 로그인 중이라면 중복 로그인 방지
        if self.is_login:
            print('접속 중인 기존 계정을 로그아웃하십시오')
            return None

        # 로그 아웃 상태라면 로그인 실행
        url = BASE_URL_ACCOUNT + '/accounts/login/'
        data = {"jaye_account": jaye_account, "password": password}
        # 로그인 실패 시 return으로 함수 실행 중단

        headers = {"accept": 'application/json', 'content-type': 'application/json;charset=UTF-8'}
        response = requests.post(url, data=json.dumps(data), headers=headers)

        self.myinfo = response.json()

        user_token = 'token ' + self.myinfo["token"]

        # initialize trade
        # STRATEGIES from settings.py

        url = BASE_URL_PUBLIC + '/trade/strategies/'
        headers = {'Authorization': user_token}
        response = requests.get(url, headers=headers)
        STRATEGIES = response.json()

        for i in STRATEGIES:
            self.jaye.trade[i] = Strategy(i, user_token)
        self.jaye.trade["strategies"] = STRATEGIES

        trade_tuple = namedtuple('trade', ["strategies"] + STRATEGIES)
        self.jaye.trade = trade_tuple(**self.jaye.trade)

        # insert token
        self.cash.token = user_token
        self.token = user_token
        self.is_login = True

    def logout(self):
        url = BASE_URL_ACCOUNT + '/accounts/logout/'
        response = requests.post(url)
        self.cash = Cash()
        self.is_login = False
        self.myinfo = {}
        # parents instance jaye
        self.jaye.Analysis = Analysis()
        self.jaye.trade = {}
        # self.jaye.simulation = simulation()


class Analysis:
    def __init__(self):
        self.token = ''
        pass

    @property
    def assets(self):
        url = BASE_URL_PUBLIC + "/analysis/assets/"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        try:
            df_assets = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            print('JSONDecodeError occured')
            return None
        except:
            print(response.json())
            return None

        return df_assets

    def factor_history(self, symbol, start, end):
        url = BASE_URL_PUBLIC + f"/analysis/factor-history/?company={symbol}&from={start}&to={end}"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        try:
            df_factor_history = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            print('JSONDecodeError occured')
            return None
        except:
            print(response.json())
            return None

        return df_factor_history

    def factors(self, symbol_list):
        url = BASE_URL_PUBLIC + f"/analysis/factors/?code_list={'%2C'.join(symbol_list)}"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        try:
            df_factors = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            print('JSONDecodeError occured')
            return None
        except:
            print(response.json())
            return None

        return df_factors

    def fundamental(self, symbol, start, end):
        url = BASE_URL_PUBLIC + f"/analysis/fundamental/?company={symbol}&from={start}&to={end}"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        try:
            df_fundamental = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            print('JSONDecodeError occured')
            return None
        except:
            print(response.json())
            return None

        return df_fundamental

    def market(self,symbol,start,end):
        url = BASE_URL_PUBLIC + f"/analysis/market/?company={symbol}&from={start}&to={end}"
        headers = {'Authorization': self.token}
        response = requests.get(url, headers=headers)
        try:
            df_market = pd.DataFrame(response.json())
        except json.JSONDecodeError:
            print('JSONDecodeError occured')
            return None
        except:
            print(response.json())
            return None

        return df_market


class Strategy:
    def __init__(self,name,token):
        self.strategy_name = name
        self.token = token

    def returns(self, start,end):
        headers = {"Authorization" : self.token}
        url = BASE_URL_PUBLIC + f"/performance/return/?strategy%20name={self.strategy_name}&from={start}&to={end}"
        response = requests.get(url, headers=headers)
        df_returns = pd.DataFrame(response.json())
        return df_returns

    def stats(self, start, end, rolling=255, risk_free_rate=0, base_index='INDEX-KRX-KOSPI-KOSPI'):
        rolling = str(rolling)
        risk_free_rate = str(risk_free_rate)
        base_index = str(base_index)

        headers = {"Authorization": self.token}
        url = BASE_URL_PUBLIC + f"/performance/stats/?strategy%20name={self.strategy_name}&from={start}&to={end}&rolling={rolling}&risk_free_rate={risk_free_rate}&base_index={base_index}"
        response = requests.get(url, headers=headers)
        df_returns = pd.DataFrame(response.json())
        return df_returns

    def asset_allocation(self, start, end):
        headers = {"Authorization": self.token}
        url = BASE_URL_PUBLIC + f"/performance/asset-allocation/?strategy%20name={self.strategy_name}&from={start}&to={end}"
        response = requests.get(url, headers=headers)
        df_allocation = pd.DataFrame(response.json())
        return df_allocation


class Simulation:
    def __init__(self):
        pass

