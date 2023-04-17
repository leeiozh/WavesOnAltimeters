from skyfield.api import load, wgs84
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import fiona
import sys

sys.path.insert(0, '../src')
from src.drawers import *
from src.converters import *

# подгрузка данных о спутниках из файла
sats = load.tle_file('tle/tle_data.txt')
names = ['CFOSAT', 'HAIYANG-2B', 'JASON-3', 'SARAL', 'SENTINEL-3A', 'SENTINEL-3B', 'SENTINEL-6', 'CRYOSAT 2']
sat_names = {sat.name: sat for sat in sats}
sat_data = [sat_names[name] for name in names]

# загрузка координат из KML, который генерирует OpenCPN
fiona.drvsupport.supported_drivers['KML'] = 'rw'
geo_df = gpd.read_file('track/test_seva.kml', driver='KML')
track_df = pd.DataFrame(geo_df)["geometry"]
station_pos_ll = np.array([wgs84.latlon(track_df[i].y, track_df[i].x) for i in range(track_df.shape[0] - 1)])

# загрузка координат из txt, который мы забили руками
# station_pos_ = np.loadtxt("chain_east.txt", delimiter=' ')
# station_pos = np.zeros((station_pos_.shape[0], 2))
# station_pos[:, 0] = -(station_pos_[:, 0] + station_pos_[:, 1] / 60)
# station_pos[:, 1] = -(station_pos_[:, 2] + station_pos_[:, 3] / 60)
#
# station_pos_ll = np.array([wgs84.latlon(ll[0], ll[1]) for ll in station_pos])

# указываем время старта
start_time = dt.datetime(2023, 4, 27, 0, 0, 0, tzinfo=dt.timezone.utc)

# последним аргументом указываем предполагаемую скорость в УЗЛАХ
track_time = calc_time(track_df, start_time, speed=9)

# *** drawing map ***
plt.figure()

# для отрисовки карты нужно указать крайние наносимые координаты
map = make_map(left=-20, right=50, up=63, down=32)

# для отрисовки сетки нужно указать ее шаг
draw_grid(map, lat_step=5, lon_step=10)

# отрисовка станций
draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
            track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
            color1='white', color2='black')
colors = ['yellow', 'red', 'orange', 'green', 'blue', 'purple', 'pink', 'grey']

height = np.array([519, 966, 1336, 781, 814, 804, 1336, 728])  # height of altimeters orbits
alt = 90 - calc_alt(220, height) / np.pi * 180  # there 220 is max permitted distance between altimeter and vessel

for n in range(track_time.shape[0] - 1):

    ts = load.timescale()

    # если нужен расчет на завтра -- просто меняем дату в двух строках ниже
    # time1 = ts.from_datetime(dt.datetime(2022, 12, 6, 0, 0, 0, tzinfo=dt.timezone.utc))
    # time2 = ts.from_datetime(dt.datetime(2022, 12, 6, 23, 59, 0, tzinfo=dt.timezone.utc))
    # res = [sat_data[i].find_events(station_pos_ll[n], time1, time2, altitude_degrees=alt[i]) for i in
    #        range(len(sat_data))]

    res = [
        sat_data[i].find_events(station_pos_ll[n], ts.from_datetime(track_time[n]), ts.from_datetime(track_time[n + 1]),
                                altitude_degrees=alt[i]) for i in range(len(sat_data))]

    for i in range(len(names)):
        if len(res[i][0]) > 0:
            print(names[i])
            for t in res[i][0]:
                ll = wgs84.latlon_of(sat_data[i].at(t))
                if len(res[i][0]) == 3 and t == res[i][0][1]:
                    # вывод в консоль времени и координат ближайшей к треку точки пролета
                    print(t.utc_datetime().date(), t.utc_datetime().time())
                    print(ll[0].degrees, ",", ll[1].degrees)
                    print()
                # отрисовка на карте трех точек: начало и конец попадания спутника в указанный радиус,
                # между ними ближайшая к треку точка
                draw_point(map, [ll[0].degrees, ll[1].degrees], color=colors[i], alpha=1., flag=False)

# отрисовка легенды
for i in range(len(sat_names)):
    plt.scatter([0], [0], color=colors[i], label=names[i])

plt.legend(loc='upper right', fontsize="7")
plt.savefig('pics/seva_test.png', bbox_inches='tight', dpi=1000)
plt.show()
