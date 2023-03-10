import datetime as dt
import numpy as np
from pandas._libs.tslibs.timezones import UTC


def calc_alt(length, height):
    """
    calculate an angle above the horizon
    :param length: distance on Earth (radius of spot)
    :param height: height of orbit above the Earth
    :return: angle
    """
    phi = length / 6371
    s = 6371 * np.sin(phi)
    alph = np.arctan2(s, 6371 * (1 - np.cos(phi)) + height)
    return phi + alph


def utc_to_sec(utc: str, noyear=True, year=2022) -> float:
    """
    Конвертер из utc в секунды с J2000 для даты вида hh-mm-ss-yyyy-mm-dd
    :param utc: время в utc
    :param noyear: для укороченных названий
    :param year: для укороченных названий
    :return: время в секундах с J2000
    """
    if utc[2] != '-' and utc[2] != ':' and utc[2] != '.':
        if noyear:
            return (dt.datetime(int(utc[0:4]), int(utc[5:7]), int(utc[8:10]), int(utc[11:13]), int(utc[14:16]),
                                0) - dt.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()
        else:
            return (dt.datetime(year, int(utc[5:7]), int(utc[8:10]), int(utc[11:13]), int(utc[14:16]),
                                0) - dt.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()
    else:
        if len(utc) > 16:
            return (dt.datetime(int(utc[6:10]), int(utc[3:5]), int(utc[:2]), int(utc[11:13]), int(utc[14:16]),
                                int(utc[17:19])) - dt.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()
        else:
            return (dt.datetime(int(utc[6:10]), int(utc[3:5]), int(utc[:2]), int(utc[11:13]), int(utc[14:16]),
                                0) - dt.datetime(2000, 1, 1, 0, 0, 0)).total_seconds()


def sec_to_utc(sec: float) -> dt.datetime:
    """
    Конвертер из секунд с J2000 в utc
    :param sec: время в секундах с J2000
    :return:  время в utc
    """
    return dt.datetime(2000, 1, 1, 0, 0, 0) + dt.timedelta(seconds=sec)


def to_deg(inp) -> float:
    arr = inp.split()
    if len(arr) > 1:
        return int(arr[0]) + float(arr[1]) / 60
    else:
        return float(arr[0])


def r_to_latlon(r) -> (np.ndarray, np.ndarray):
    norm = np.linalg.norm(r)
    lat = np.arccos(r[2] / norm) / np.pi * 180
    lon = np.arctan2(r[1], r[0]) / np.pi * 180
    return lat, lon


def time_to_sf(time: np.ndarray) -> list:
    res = np.ndarray(time.shape, dtype=dt.datetime)
    for i in range(len(res)):
        res[i] = dt.datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC) + dt.timedelta(seconds=time[i])
    return res.tolist()
