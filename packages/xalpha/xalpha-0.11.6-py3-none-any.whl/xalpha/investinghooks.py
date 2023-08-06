import logging
from uuid import uuid4
import pandas as pd

from xalpha.cons import rget, rget_json, _float
from xalpha.universal import lru_cache_time
from xalpha.universal import set_handler

logger = logging.getLogger(__name__)


meta_dict = {
    "commodities/brent-oil": (8833, "USD"),
    "commodities/crude-oil": (8849, "USD"),
    "commodities/gold": (8830, "USD"),
    "etfs/barclays-1-3-year-treasury-bond-mx": (1036845, "USD"),
    "etfs/direxion-daily-jr-gld-mnrs-bull-3x": (941457, "USD"),
    "etfs/etfs-brent-crude": (38324, "USD"),
    "etfs/etfs-crude-oil": (38335, "USD"),
    "etfs/etfs-leveraged-crude-oil": (38444, "USD"),
    "etfs/etfs-physical-swiss-gold-shares": (40655, "USD"),
    "etfs/ishares-comex-gold-trust": (38181, "USD"),
    "etfs/ishares-dj-us-energy-sector-fund": (40673, "USD"),
    "etfs/ishares-ftse-a50-china": (959572, "HKD"),
    "etfs/ishares-msci-global-gold-miners-be": (44703, "USD"),
    "etfs/ishares-s-p-global-energy": (520, "USD"),
    "etfs/ishares-s-p-gsci-commod": (515, "USD"),
    "etfs/market-vectors-junior-gold-miners": (40682, "USD"),
    "etfs/next-funds-nomura-crude-oil-long": (953293, "JPY"),
    "etfs/powershares-db-agriculture-fund": (40684, "USD"),
    "etfs/powershares-db-base-metals-fund": (44715, "USD"),
    "etfs/powershares-db-commodity-index": (14178, "USD"),
    "etfs/powershares-db-oil-fund": (44792, "USD"),
    "etfs/powershares-db-usd-index-bullish": (37471, "USD"),
    "etfs/proshares-ultra-dj-ubs-crude-oil": (14218, "USD"),
    "etfs/proshares-ultra-gold": (40687, "USD"),
    "etfs/simplex-wti": (953362, "JPY"),
    "etfs/spdr-energy-select-sector-fund": (40657, "USD"),
    "etfs/spdr-gold-minishares": (1088680, "USD"),
    "etfs/spdr-gold-trust": (9227, "USD"),
    "etfs/spdr-s-p-oil--gas-explor---product": (38284, "USD"),
    "etfs/sprott-physical-gold-trust": (40693, "USD"),
    "etfs/ubs-cmci-oil-sf-usd": (995771, "CHF"),
    "etfs/united-states-12-month-oil": (44793, "USD"),
    "etfs/united-states-brent-oil-fund-lp": (44634, "USD"),
    "etfs/united-states-oil-fund": (44794, "USD"),
    "indices/dj-us-select-oil-exploration-prod": (954528, "USD"),
    "indices/india-50-futures": (8985, "INR"),
    "indices/japan-ni225": (178, "JPY"),
    "indices/germany-30": (172, "EUR"),
    "indices/germany-30-futures": (8826, "EUR"),
    "indices/nq-100": (20, "USD"),
    "indices/nq-100-futures": (8874, "USD"),
    "etfs/wisdomtree-india-earnings-fund": (44932, "USD"),
    "currencies/inr-cny": (1865, "USD"),
    "indices/s-p-cnx-nifty": (17940, "INR"),
    "indices/india-50-futures": (8985, "INR"),
    "etfs/lyxor-msci-india": (47586, "EUR"),
    "etfs/ishares-msci-india": (44929, "USD"),
    "etfs/s-p-india-nifty-fifty": (45473, "USD"),
    "etfs/ishares-msci-india-ucits-usd-acc": (1140513, "AUD"),
    "etfs/ishares-msci-india-small-cap": (44930, "USD"),
    "etfs/ishares-core-sp-bse-sensex-india": (994200, "HKD"),
    "etfs/powershares-india-portfolio": (44931, "USD"),
    "indices/switzerland-20": (176, "CHF"),
    "etfs/vanguard-energy": (45405, "USD"),
    "etfs/amundi-etf-msci-india": (38808, "USD"),
    "etfs/egshares-india-consumer": (44926, "USD"),
    "indices/us-spx-500": (166, "USD"),
    "etfs/cbnd": (1159656, "USD"),
    "etfs/vanguard-total-bond-market": (45423, "USD"),
}

iheaders = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Accept-Language": "zh-cn",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "User-Agent": "Investing.China/0.0.3 CFNetwork/1121.2.2 Darwin/19.3.0",
    "ccode": "CN",
    "ccode_time": "1584408267.393406",
    "x-app-ver": "117",
    "x-meta-ver": "14",
    "x-os": "ios",
    "x-uuid": str(uuid4()),
}


def is_investing_url(code):
    if (
        len(code[1:].split("/")) == 2
        and len(code.split("/")[-1]) > 6
        and len(code.split("/")[0].split("-")) == 1
    ):
        return True
    if code in ["commodities/gold", "etfs/cbnd", "indices/nq-100"]:
        return True
    return False


def get_investing_id_v2(suburl):
    if suburl in meta_dict:
        return meta_dict[suburl][0]
    logger.warning("url not in predefined investing id pair list")
    raise Exception(
        "%s not in predefined investing id pair list" % suburl
    )  # add search logic later


def get_investing_daily_v2(suburl, start, end):
    # start %Y%m%d
    if not isinstance(suburl, int):
        suburl = get_investing_id_v2(suburl)
    date_to = end[6:8] + end[4:6] + end[0:4]
    date_from = start[6:8] + start[4:6] + start[0:4]
    params = {
        "time_utc_offset": 0,
        "lang_ID": 6,  # 1 英文，6 中文
        "pair_ID": suburl,
        "screen_ID": 63,
        "interval": "day",
        "skinID": 2,
        "date_to": date_to,
        "date_from": date_from,
    }
    r = rget_json(
        "https://cnappapi.investing.com/get_screen.php", params=params, headers=iheaders
    )
    df = pd.DataFrame(r["data"][0]["screen_data"]["data"])
    df["date"] = df["date"].apply(lambda s: pd.Timestamp(s, unit="s"))
    df["close"] = df["price"]
    df["close"] = df["close"].apply(lambda s: _float(s))
    df = df.drop(["color", "price", "vol", "perc_chg"], axis=1)
    return df.iloc[::-1]


def daily_wrapper(code, start, end, **kws):
    if is_investing_url(code):
        return get_investing_daily_v2(code, start, end)


set_handler(method="daily", f=daily_wrapper)


@lru_cache_time(120)
def get_investing_rt_v2(suburl):
    if not isinstance(suburl, int):
        suburl = get_investing_id_v2(suburl)
    params = {
        "time_utc_offset": 28800,
        "lang_ID": 6,
        "pair_ID": suburl,
        "screen_ID": 22,
        "v2": 1,
    }

    r = rget_json(
        "https://cnappapi.investing.com/get_screen.php", params=params, headers=iheaders
    )
    d = {}
    d["current"] = _float(
        r["data"][0]["screen_data"]["pairs_data"][0]["info_header"]["last"]
    )  # current
    d["currency"] = r["data"][0]["screen_data"]["pairs_data"][0]["info_header"][
        "currency_in"
    ]
    if suburl in [8833, 8849]:
        d["rollover"] = r["data"][0]["screen_data"]["pairs_data"][0]["overview_table"][
            6
        ]["val"].replace("-", "/")
        d["lastrollover"] = None
    return d  # no lastrollover


def rt_wrapper(code, **kws):
    if is_investing_url(code):
        return get_investing_rt_v2(code)


set_handler(method="rt", f=rt_wrapper)


@lru_cache_time(120)
def get_investing_bar_v2(suburl):
    # get_bar(code, prev=168, interval="3600")  ## 获取小时线

    if not isinstance(suburl, int):
        suburl = get_investing_id_v2(suburl)
    params = {
        "time_utc_offset": 0,
        "lang_ID": 6,  # 1 英文，6 中文
        "pair_ID": suburl,
        "range": "1m",
    }

    r = rget_json(
        "https://cnappapi.investing.com/chart_range.php",
        params=params,
        headers=iheaders,
    )
    df = pd.DataFrame(r["candles"], columns=["date", "close"])
    df["date"] = df["date"].apply(
        lambda s: pd.Timestamp(s / 1000, unit="s") + pd.Timedelta("8h")
    )  # any time zone issue?
    return df


def bar_wrapper(code, **kws):
    if is_investing_url(code):
        return get_investing_bar_v2(code)


set_handler(method="bar", f=bar_wrapper)
