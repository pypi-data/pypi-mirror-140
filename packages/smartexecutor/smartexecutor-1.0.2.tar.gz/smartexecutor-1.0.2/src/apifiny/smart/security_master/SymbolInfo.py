import pandas as pd
import ccxt
import math

def get_symbol_info_okex(symbol):
    client = ccxt.okex()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()

    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] in ['spot', 'swap']:
                try:
                    ticker = markets[sym]['id'].replace('/', '').replace('-', '') + '.O'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(abs(math.log10(markets[sym]['precision']['price'])))
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(abs(math.log10(markets[sym]['precision']['amount'])))
                    symbol_info[ticker]['multiple'] = markets[sym]['contractSize'] if markets[sym]['contractSize'] else 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.O']



def get_symbol_info_huobi(symbol):
    client = ccxt.huobi()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()

    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] == 'spot':
                try:
                    ticker = sym.replace('/', '').replace('-', '') + '.H'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(abs(math.log10(markets[sym]['precision']['price'])))
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(abs(math.log10(markets[sym]['precision']['amount'])))
                    symbol_info[ticker]['multiple'] = markets[sym]['contractSize'] if markets[sym][
                        'contractSize'] else 1.0
                except Exception as err:
                    print(sym, err)

            elif markets[sym]['type'] == 'swap':
                try:
                    ticker = sym.replace('/', '').replace('-', '') + 'SWAP.H'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(abs(math.log10(markets[sym]['precision']['price'])))
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(abs(math.log10(markets[sym]['precision']['amount'])))
                    symbol_info[ticker]['multiple'] = markets[sym]['contractSize'] if markets[sym][
                        'contractSize'] else 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.H']



def get_symbol_info_binance(symbol):
    client = ccxt.binance()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()

    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] in ['spot', 'swap']:
                try:
                    ticker = markets[sym]['id'].replace('/', '').replace('-', '') + '.A'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(markets[sym]['precision']['price'])
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(markets[sym]['precision']['amount'])
                    symbol_info[ticker]['multiple'] = markets[sym]['contractSize'] if markets[sym][
                        'contractSize'] else 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.A']



def get_symbol_info_kucoin(symbol):
    client = ccxt.kucoin()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()

    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] in ['spot', 'swap']:
                try:
                    ticker = markets[sym]['id'].replace('/', '').replace('-', '') + '.KUCOIN'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(markets[sym]['precision']['price'])
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(markets[sym]['precision']['amount'])
                    symbol_info[ticker]['multiple'] = 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.KUCOIN']


def get_symbol_info_okcoin(symbol):
    client = ccxt.okcoin()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()

    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] in ['spot', 'swap']:
                try:
                    ticker = markets[sym]['id'].replace('/', '').replace('-', '') + '.OKCOIN'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(abs(math.log10(markets[sym]['precision']['price'])))
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(abs(math.log10(markets[sym]['precision']['amount'])))
                    symbol_info[ticker]['multiple'] = 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.OKCOIN']


def get_symbol_info_bittrex(symbol):
    client = ccxt.bittrex()
    markets = client.load_markets()
    symbol_list = client.symbols
    symbol_info = dict()
    for sym in symbol_list:
        if sym in markets:
            if markets[sym]['type'] in ['spot', 'swap']:
                try:
                    ticker = markets[sym]['id'].replace('/', '').replace('-', '') + '.BITTREX'
                    symbol_info[ticker] = dict()
                    symbol_info[ticker]['ticksize'] = float(markets[sym]['limits']['price']['min'])
                    symbol_info[ticker]['lotsize'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['price_precision'] = float(abs(math.log10(markets[sym]['precision']['price'])))
                    symbol_info[ticker]['min_order_size'] = float(markets[sym]['limits']['amount']['min'])
                    symbol_info[ticker]['qty_precision'] = float(abs(math.log10(markets[sym]['precision']['amount'])))
                    symbol_info[ticker]['multiple'] = 1.0
                except Exception as err:
                    print(sym, err)
    # df = pd.DataFrame.from_dict(symbol_info, orient='index', dtype='float')
    # df.reset_index(inplace=True)
    # df.rename(columns={'index': 'symbol'}, inplace=True)
    return symbol_info[symbol+'.BITTREX']

def get_symbol_info(exch, symbol):
    if exch == 'OKEX' or exch == 'O':
        return get_symbol_info_okex(symbol)
    elif exch == 'HUOBI' or exch == 'H':
        return get_symbol_info_huobi(symbol)
    elif exch == 'BINANCE' or exch == 'A':
        return get_symbol_info_binance(symbol)
    elif exch == 'KUCOIN':
        return get_symbol_info_kucoin(symbol)
    elif exch == 'OKCOIN':
        return get_symbol_info_okcoin(symbol)
    elif exch == 'BITTREX':
        return get_symbol_info_bittrex(symbol)
    else:
        print(f"{exch} is not supported yet")
        return None


def create_symbol_info_cfg(symbols):
    symbol_info_dict = dict()
    for symbol in symbols:
        sym, exch = symbol.split('.')
        symbol_info_dict[symbol] = get_symbol_info(exch, sym)
    return symbol_info_dict



if __name__ == "__main__":
    get_symbol_info('H', 'BTCUSDT')
