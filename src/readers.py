import netCDF4 as nc
import glob
import sys

import pandas as pd

sys.path.append("/home/leeiozh/ocean/WavesOnAltimeters/src")
from converters import *

TRACK_TYPE = np.ndarray(shape=(5,), dtype=float)


def read_track_height(file: str):
    data = pd.read_csv(file, delimiter=",")
    data["Широта"] = data["Широта"].apply(to_deg)
    data["Долгота"] = data["Долгота"].apply(to_deg)
    data["дата"] = data["дата"].apply(utc_to_sec)

    return data.to_numpy()


def read_track(file: str, station=False) -> TRACK_TYPE:
    """
    чтение данных о треке судна
    :param file: путь к файлу
    :param station: true если дрейфовая станция и в файле есть время старта и окончания работ,
    false если ходовая станция, время берется из названия файла
    :return: данные из файла с переведенным временем
    """
    data = pd.read_csv(file, delimiter=",")
    if station:
        data["name"] = data["name"].apply(utc_to_sec)
    else:
        data["time_start"] = data["time_start"].apply(utc_to_sec)
        data["time_end"] = data["time_end"].apply(utc_to_sec)

    return data.to_numpy()


def read_track_radar2(file: str) -> TRACK_TYPE:
    """
    чтение данных о треке судна
    :param file: путь к файлу
    :return: данные из файла с переведенным временем
    """
    data = pd.read_csv(file, delimiter=",")
    data["name"] = data["name"].apply(utc_to_sec)
    tmp = data[['name', 'lat_radar', 'lon_radar']].to_numpy()

    return tmp


def read_track_radar_ai64(file) -> TRACK_TYPE:
    data = pd.read_csv(file, delimiter=';')
    data["datetime"] = data["datetime"].apply(dt_to_sec)
    tmp = data[['datetime', 'lat', 'lon']].to_numpy()
    return tmp


def read_track_radar_rae69(file) -> TRACK_TYPE:
    data = pd.read_csv(file, delimiter=';')
    data["time_start"] = data["time_start"].apply(dt_to_sec)
    data["lat"] = data["lat"].apply(opcpn_to_deg)
    data["lon"] = data["lon"].apply(opcpn_to_deg)
    tmp = data[['time_start', 'lat', 'lon']].to_numpy()
    return tmp


def read_sat_data(path: str, names: list) -> np.ndarray:
    """
    Чтение данных со спутника
    :param path: путь к папке с данными (не разделенные на месяцы)
    :param names: имена спутников (совпадают с именем папки)
    :return: массив массивов данных
    """
    res = np.ndarray(shape=(len(names), 4), dtype=np.ndarray)
    for i in range(len(names)):
        files = glob.glob(path + "*" + names[i] + '*.nc')
        files.sort()

        res[i, 0] = np.array(nc.Dataset(files[0]).variables['time'][:])
        res[i, 1] = np.array(nc.Dataset(files[0]).variables['latitude'][:])
        res[i, 2] = np.array(nc.Dataset(files[0]).variables['longitude'][:])
        res[i, 3] = np.array(nc.Dataset(files[0]).variables['VAVH'][:])

        for j in range(0, len(files)):
            ds = nc.Dataset(files[j])
            res[i, 0] = np.append(res[i, 0], np.array(ds.variables['time'][:]))
            res[i, 1] = np.append(res[i, 1], np.array(ds.variables['latitude'][:]))
            res[i, 2] = np.append(res[i, 2], np.array(ds.variables['longitude'][:]))
            res[i, 3] = np.append(res[i, 3], np.array(ds.variables['VAVH'][:]))
    return res
