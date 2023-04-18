from mpl_toolkits.basemap import Basemap
import numpy as np


def make_map(left, right, up, down) -> Basemap:
    """
    Отрисовывает карту
    :return: карта
    """

    m = Basemap(resolution='l', projection='cyl', llcrnrlon=left, llcrnrlat=down, urcrnrlon=right, urcrnrlat=up)
    m.drawcoastlines()
    m.fillcontinents()
    return m


def draw_grid(m: Basemap, lat_step, lon_step):
    """
    Отрисовывает сетку на карте
    :param m: карта
    """
    m.drawmeridians(np.arange(-180, 180., lon_step), labels=[True, False, False, True], zorder=1, color='grey')
    m.drawparallels(np.arange(-90, 90, lat_step), labels=[True, False, True, False], zorder=1, color='grey')


def draw_coords(m: Basemap, track_lat: list, track_lon: list, track_buoy: np.ndarray, color1: str,
                color2: str):
    """
    Отрисовывает трек на карте
    :param m: карта
    :param track_lat: широты трека
    :param track_lon: долготы трека
    :param track_buoy: флаг буя трека
    :param color1: цвет трека без буя
    :param color2: цвет трека с буем
    """
    xpt, ypt = m(track_lon * track_buoy, track_lat * track_buoy)
    m.scatter(xpt, ypt, color=color2, label='Radar station', zorder=10)
    xpt, ypt = m(track_lon, track_lat)
    m.scatter(xpt, ypt, color=color1, label='Satellite mission:', alpha=0.)


def draw_point(m: Basemap, lat_lon: list, color: str, alpha, flag=True):
    """
    Отрисовывает одну точку на карте
    :param m: карта
    :param lat_lon: [широта, долгота] точки
    :param color: цвет
    :param alpha: прозрачность
    """
    if flag:
        xpt, ypt = m(-360 + lat_lon[1], lat_lon[0])
    else:
        xpt, ypt = m(lat_lon[1], lat_lon[0])
    m.scatter(xpt, ypt, color=color, alpha=alpha, s=10)
