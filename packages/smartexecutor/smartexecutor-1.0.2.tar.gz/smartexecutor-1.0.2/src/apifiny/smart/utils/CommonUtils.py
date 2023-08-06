#!/usr/bin/python3

'''
Usage example:
    python3 /local/cchome/pycode/pymulti/scripts/ccc/ccc_stats.py
'''
import errno
import os, sys, json, glob, subprocess, time
import argparse
import pandas as pd
import numpy as np
from collections import OrderedDict
from tabulate import tabulate
from datetime import date, datetime, timedelta
from json.encoder import JSONEncoder
from sys import stdout
import redis
import threading
import getpass
from web_django import *

USER_NAME=getpass.getuser()

DAY_SECS = 24 * 3600
HB_TIMEOUT = 300 #30
CCAWS_REDIS_HOST = os.getenv('CCAWS_REDIS_HOST')  #configure 
CCAWS_REDIS_AUTH = os.getenv('CCAWS_REDIS_AUTH')
HOST_LOCATION = os.getenv('HOST_LOCATION')
MKTPUB_REDIS_HOST = os.getenv('MKTPUB_REDIS_HOST')
MKTPUB_REDIS_AUTH = os.getenv('MKTPUB_REDIS_AUTH')

class TradingStatsAnalyzer:
    PRICE_PATTERNS = ["price_mktpub-book-HUOBI-*"] #, "price_mktpub-book-OKEX_V3_FUTURES-*"]
    STATS_PATTERN = "ccc_stats_*"
    HB_PATTERN = "ccc_hb_*"
    contract_multipliers = {
        'BTCOFQ0': 100, 'ETHOFQ0': 10, 'ETCOFQ0': 10, 'LTCOFQ0': 10, 'XRPOFQ0': 10,
        'BCHOFQ0': 10, 'EOSOFQ0': 10, 'BSVOFQ0': 10, 'TRXOFQ0': 10}
    
    def __init__(self,save_path, listen_port, dest_port,display_level, save, quiet,posmis):
        self.save_path = save_path
        self.listen_port = listen_port
        self.dest_port = dest_port
        self.display_level = display_level
        self.save = save
        self.quiet = quiet
        self.posmis = posmis
        self.conn = redis.StrictRedis(host=CCAWS_REDIS_HOST, port=self.dest_port, db=0, password=CCAWS_REDIS_AUTH) #'localhost' 
        self.pubsub = self.conn.pubsub()
        self.conn_price = redis.StrictRedis(host="127.0.0.1", port=self.listen_port, db=0) # price
        self.pubsub_price = self.conn_price.pubsub()
        self.dstats = {}
        self.dhb = {}
        self.prices = {}
        self.dfPrev = None
        self.current_date = date.today()
        self.min_update_gap = timedelta(seconds=5)
        self.next_update_time = datetime.fromtimestamp(0)
        
    def run(self):
        self.load_prev_stats()
        self.load_sub_prices()
        self.load_sub_stats()
        self.load_sub_heartbeat()
        df = self.gen_stats()
        self.show_stats(df)
        print('\033[2J')
        while True:
            msg1 = self.pubsub.get_message()
            msg2 = self.pubsub_price.get_message()
            if not msg1 and not msg2:
                time.sleep(0.001)
            else:
                if msg1:
                    self.process_redis_message(msg1)
                if msg2:
                    self.process_redis_message(msg2)

            
    
    def process_redis_message(self, msg):
        if msg['type'] == 'pmessage':
            channel = msg['channel'].decode()
            pattern = msg["pattern"].decode()
            if not "liquidator" in channel:
                try:
                    data = json.loads(msg['data'].decode())
                    #print(data)
                    #os._exit(0)
                except:
                    return
                #print(channel, data)
                if pattern == self.STATS_PATTERN:
                    self.dstats[channel[10:]] = data
                elif pattern == self.HB_PATTERN:
                    #print(channel[7:], data)
                    self.dhb[channel[7:]] = data
                elif pattern in self.PRICE_PATTERNS:
                    symbol = channel.split('-')[-1]
                    #print(symbol, data)
                    self.prices[symbol] = data
                    if symbol[-4:] == 'USDT':
                        self.prices[symbol[:-1]] = data
                        self.prices[symbol[:-1]+'C'] = data
                    #symbol = data['symbol']
                    #data = data['data']
                    #print(symbol, data)
                    #self.prices[symbol] = 0.5 * (book['bids'][0][0] + book['asks'][0][0]) 

                if datetime.now() >= self.next_update_time:
                    self.next_update_time = datetime.now() + self.min_update_gap
                    df = self.gen_stats()
                    self.show_stats(df)

    def load_sub_stats(self):
        keys = self.conn.keys(self.STATS_PATTERN)
        for key in keys:
            key = key.decode()
            if "liquidator" in key: continue
            data = self.conn.get(key)
            # print(key, data.decode())
            self.dstats[key[10:]] = json.loads(data.decode())

        channel = self.STATS_PATTERN
        self.pubsub.psubscribe(channel)

    def load_sub_heartbeat(self):
        keys = self.conn.keys(self.HB_PATTERN)
        for key in keys:
            data = self.conn.get(key)
            #print(key.decode(), data.decode())
            self.dhb[key.decode()[7:]] = json.loads(data.decode())

        channel = self.HB_PATTERN
        self.pubsub.psubscribe(channel)

    def load_sub_prices(self):
        for p in self.PRICE_PATTERNS: 
            self.pubsub_price.psubscribe(p)

            keys = self.conn_price.keys(p)
            #print(keys)
            for key in keys:
                key = key.decode()
                symbol = key.split('-')[-1]
                data = self.conn_price.get(key)
                #print(key, data)
                px = float(data.decode()) 
                self.prices[symbol] = float(data.decode()) 
                if symbol[-4:] == 'USDT':
                    self.prices[symbol[:-1]] = px
                    self.prices[symbol[:-1]+'C'] = px
            #print(self.prices)

    def load_prev_stats(self):
        base_dir='/data/cc/prod/ccc/stats/'    
        date = int((datetime.now() - timedelta(days=1)).strftime("%Y%m%d"))
        fp = "{}/{}/ccc_stats_{}.csv".format(base_dir, date, self.dest_port) #add port argument
        print("load ", fp)
        self.dfPrev = pd.read_csv(fp, index_col=0)
        #print(self.dfPrev.loc[self.dfPrev.index.to_series().apply(lambda x: x[:7]=='ccc03HK')])
        ##os._exit(0)

    def gen_stats(self):
        if date.today() > self.current_date:
            self.current_date = date.today() 
            self.load_prev_stats()
        
        #load stats
        dfs = pd.DataFrame(self.dstats).T
        #print(dfs[['symbol']])
        
        # add prices
        ts = pd.Series(self.prices, name='price')
        dfs = dfs.join(ts, on='symbol')
        #print(dfs[['price']])
                
        # add heartbeat
        dfhb = pd.DataFrame(self.dhb).T
        #dfhb['state'] = np.where((dfhb.ts / 1e9) < (time.time() - HB_TIMEOUT), "", dfhb.state)
        dfs = dfs.merge(dfhb, left_index=True, right_index=True, how='outer')
        dfs['ts'] = dfs.ts.fillna(0)
        dfs['state'] = np.where((dfs.ts / 1e9) < (time.time() - HB_TIMEOUT), "", dfs.state)

        # add contract_multiplier
        tsMul = pd.Series(self.contract_multipliers, name="multiplier")
        dfs = dfs.join(tsMul, on="symbol", how='left')
        dfs['multiplier'] = dfs['multiplier'].fillna(1.0)

        # calculate derived values
        dfs = dfs.fillna(0)
        dfs['posUSD'] = np.where(dfs.exchange=='K', dfs.position * dfs.multiplier, dfs.position * dfs.price)
        dfs['pnlUSD'] = dfs.cash + np.where(dfs.exchange=='K', \
                                  np.where(dfs.position==0, 0.0, dfs.position * dfs.multiplier * (1.0 - dfs.pos_px / dfs.price)), dfs.position * dfs.price)
        dfs['netUSD'] = dfs.pnlUSD - dfs.fee
        
        # add previous day stats
        dfs = dfs.merge(self.dfPrev, left_index=True, right_index=True, suffixes=['', '.prev'], how='outer')
        #print(dfs.loc[dfs.index.to_series().apply(lambda x: x[:9]=='gateio_mm')].netUSD)
        #print(dfs.loc[dfs.index.to_series().apply(lambda x: x[:9]=='gateio_mm')]["netUSD.prev"])
        # handle stale instances 
        stale_cond = (dfs.ts / 1e9) < (time.time() - DAY_SECS)
        dfs['stale'] = stale_cond       
        #dfs['position'] = np.where(stale_cond, 0, dfs.position)
        #dfs['cash'] = np.where(stale_cond, dfs.prevNetUSD + dfs.fee, dfs.cash)
        
        # calculate day values
        dfs = dfs.fillna(0)
        dfs['dayNetUSD'] = dfs.netUSD - dfs['netUSD.prev']
        dfs['dayPnlUSD'] = dfs.pnlUSD - dfs['pnlUSD.prev']
        dfs['dayTradeCnt'] = dfs.tradeCnt - dfs['tradeCnt.prev']
        dfs['dayVolUSD'] = dfs.volUSD - dfs['volUSD.prev']
        dfs['dayVolume'] = dfs.volume - dfs['volume.prev']
        
        #df1 = dfs.loc[dfs.index.to_series().apply(lambda x: x[:7]=='ccc03HK')]
        #print(tabulate(df1.round(2), headers='keys', tablefmt='psql', floatfmt=".2f"))
        #os._exit(0)
        
        # add Total line
        dfx = dfs.sort_index().copy()
        dfxd = dfx.apply(pd.to_numeric, errors='ignore')
        dfms = dfxd.groupby('group').sum().apply(pd.to_numeric, errors='coerce')
        dfms['state'] = ''
        dfas = dfxd.sum().to_frame('Total').T.apply(pd.to_numeric, errors='coerce')
        dfx = pd.concat([dfx, dfms, dfas], sort=True) 
        #dfx = dfx.append(dfx.apply(pd.to_numeric, errors='coerce').sum().to_frame('Total').T)

        return dfx

    def show_stats(self, df):
        #print(df[['position', 'stale', 'state']].head())
        #return
        if self.display_level == 1:
            df = df.loc[(df.position.abs() > 1e-8) | (df.stale==0) | (df.index=='Total'), :]
        elif self.display_level == 2:
            df = df.loc[(df.position.abs() > 1e-8) | ((df.state!="") & (df.state!=0)) | (df.index=='Total'), :]
            #pass
        
        cols = list(df.columns)
        day_cols = [x for x in cols if x[:3]=='day']
        prev_cols = [x for x in cols if x[-5:]=='.prev']
        omit_cols = ['ts', 'exchange', 'symbol', 'group', 'model', 'stale', 'position', 'price', 'posUSD', 'state', 'multiplier']
        cols = [x for x in cols if not x in day_cols + prev_cols + omit_cols]
        cols = ['position', 'posUSD'] + day_cols + sorted(cols) + ['price', 'state']
        if(self.posmis == False): df = df[df['group']!='huobi_posmis_maker']
        df = df[cols]
        #os._exit(0)
        # if self.save:
        #     base_dir='/data/cc/prod/ccc/monitor/'
        #     fp = "{}/ccc_model_stats.csv".format(base_dir)
        #     #os.system("mkdir " + os.path.dirname(fp))
        #     df.round(2).to_csv(fp)
        #     #print('file generated:', fp)
        if self.save:
            base_dir=self.save_path
            fp = "{}ccc_model_stats{}.csv".format(base_dir, self.dest_port)
            #os.system("mkdir " + os.path.dirname(fp))
            df.round(2).to_csv(fp)
            #print('file generated:', fp)
        
        if not self.quiet:
            print('\033[0;0f')
            print(datetime.now())
            #print(df.sort_index().round(2))
            print(tabulate(df.round(2), headers='keys', tablefmt='psql', floatfmt=".2f"))

class FileUtil:
    @classmethod
    def mkdir_p(cls, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    @classmethod
    def mkdirs(cls, path):
        cls.mkdir_p(path)

    @classmethod
    def mk_parent_dirs(cls, fpath):
        path = os.path.dirname(fpath)
        cls.mkdirs(path)

    @classmethod    
    def getFirstPath(cls, tmpl):
        fs = glob.glob(tmpl)
        if len(fs) == 0:
            print("Warning: file does not exist:", tmpl)
            return None
        return fs[0]


def anarun(ana):
    while True:
            try:
                ana.run()
            except Exception as e:
                print(e)
            time.sleep(60)


def parse_symbol(sym):
    l = sym.split('.')
    return ('.'.join(l[:-1]), l[-1])

def load_ccc_cid_map():
    return pd.read_csv(f'/home/{USER_NAME}/dev/smartexecutor/simulation/common/cc_cids.csv',index_col=1)['cid']

def create_symbols_cfg(symbols):
    cids = load_ccc_cid_map()
    ports = {x : parse_symbol(x) for x in symbols}
    return [{"port": ports[x], "cid": int(cids[x])} for x in symbols]

def create_new_players_cfg(symbols):
    cfg = []
    for sym in symbols:
        (ticker, exch) = parse_symbol(sym)
        dpath = "/data/cc/prod/ccc_record_2"
        if sym == 'BTCCF0.C':
            player = [sym + "_Player", ["CobJsonPlayer", {"port": [ticker, exch], "path": dpath, "required": False}]]
        else:    
            player = [sym + "_Player", ["CobJsonPlayer", {"port": [ticker, exch], "path": dpath}]]
        cfg.append(player)
    return cfg

def write_concise_obj(f, o, levels, max_levels):
    istr = "    " * levels
    if levels == max_levels:
        f.write(json.dumps(o))
    else:
        if isinstance(o, (list, tuple)):
            f.write("[")
            for i, x in enumerate(o):
                if levels < max_levels:
                    f.write("\n    " + istr)
                write_concise_obj(f, x, levels+1, max_levels)
                if i < len(o)-1:
                    f.write(", ")
            if levels < max_levels:
                f.write("\n" + istr)
            f.write("]")
        elif isinstance(o, (dict)):
            f.write("{")
            for i, (k, v) in enumerate(o.items()):
                if levels < max_levels:
                    f.write("\n    " + istr)
                f.write(JSONEncoder().encode(k) + ": ")
                write_concise_obj(f, v, levels+1, max_levels)
                if i < len(o)-1:
                    f.write(",")
            if levels < max_levels:
                f.write("\n" + istr)
            f.write("}")
        else:
            f.write(json.dumps(o))

def write_concise_json(fn, cfg, max_levels=2):
    FileUtil.mk_parent_dirs(fn)
    with open(fn, "w") as f:
        write_concise_obj(f, cfg, 0, max_levels)
class WebClient():
    def __init__(self,ip, port,status_path):
        self.ip = ip
        self.port = port
        self.status_path = status_path

    def gen_status(self,listen_port,dest_port,display_level,save,quiet,posmis_match):
        ana = TradingStatsAnalyzer(self.status_path, listen_port, dest_port,display_level, save, quiet,posmis_match)
        while True:
                    try:
                        ana.run()
                    except Exception as e:
                        print(e)
                    
                    time.sleep(60)

    def gen_balance(self):
        #TODO
        pass
    def start_service(self):
        cmd = 'python3 manage.py runserver 0.0.0.0:'+self.port
        result = os.popen(cmd).read()
        for line in result.splitlines():
            print(line)




#     parser = argparse.ArgumentParser()
#     parser.add_argument('-p', '--listen_port', help='6379 is default port', default=6379, type=int)
#     parser.add_argument('-d', '--dest_port', help='6380 is default port', default=6380, type=int)
#     parser.add_argument('-ds', '--dest_port_list',nargs='*', default=[], help="list")
#     parser.add_argument('-l', '--display_level', help='0: all, 1: today, 2: active', default=2, type=int)
#     parser.add_argument('-s', '--save', help='save to file', action='store_true')
#     parser.add_argument('-q', '--quiet', help='quiet', action='store_true')
#     parser.add_argument('-m', '--posmis_match', help='posmismatch', default=False, type=bool)
#     args = parser.parse_args()
#     ana = TradingStatsAnalyzer(args.listen_port, args.dest_port,args.display_level, args.save, args.quiet,args.posmis_match)
# #     # ana.run()
# # while True:
# #         try:
# #             ana.run()
# #         except Exception as e:
# #             print(e)
        
# #         time.sleep(60)    

#     print(args.dest_port_list)
#     if len(args.dest_port_list)>0:
#         #dest_port_list save
#         #python3 lcc_stats.py -s -ds 6483 6380 6390 6393 6394 6395 6396
#         thread_list=[]
#         for port in args.dest_port_list:
#             ana = TradingStatsAnalyzer(args.listen_port, int(port),args.display_level, args.save, True,args.posmis_match)
#             ar = threading.Thread(target=anarun, args=(ana,))
#             thread_list.append(ar)
#         for t in thread_list:
#             t.start()
#             print('thread start')
#     else:
#         ana = TradingStatsAnalyzer(args.listen_port, args.dest_port,args.display_level, args.save, args.quiet, args.posmis_match)
#         while True:
#             try:
#                 ana.run()
#             except Exception as e:
#                 print(e)
            
#             time.sleep(60)
