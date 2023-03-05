import numpy as np
import datetime as dt
from src.drawers import *
from src.converters import *
from skyfield.api import load, wgs84
import matplotlib.pyplot as plt

plt.figure()

ts = load.timescale()
sats = load.tle_file('resourses/tle_data_new.txt')

names = ['CFOSAT', 'HAIYANG-2B', 'JASON-3', 'SARAL', 'SENTINEL-3A', 'SENTINEL-3B', 'CRYOSAT 2']

sat_names = {sat.name: sat for sat in sats}
sat_data = [sat_names[name] for name in names]

station_pos_ = np.loadtxt("chain_east.txt", delimiter=' ')


station_pos = np.zeros((station_pos_.shape[0], 2))
station_pos[:, 0] = -(station_pos_[:, 0] + station_pos_[:, 1] / 60)
station_pos[:, 1] = -(station_pos_[:, 2] + station_pos_[:, 3] / 60)

station_pos_ll = np.array([wgs84.latlon(ll[0], ll[1]) for ll in station_pos])

map = make_map()
draw_grid(map)
draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
                    track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
                    color1='white', color2='black')
colors = ['yellow', 'red', 'orange', 'green', 'blue', 'purple', 'pink']

height = np.array([519, 966, 1336, 781, 814, 804, 728])
alt = 90 - calc_alt(220, height) / np.pi * 180
print(alt)

for n in range(1, 2):

    time1 = ts.from_datetime(dt.datetime(2022, 12, 6, 0, 0, 0, tzinfo=UTC))
    time2 = ts.from_datetime(dt.datetime(2022, 12, 6, 23, 59, 0, tzinfo=UTC))

    res = [sat_data[i].find_events(station_pos_ll[n], time1, time2, altitude_degrees=alt[i]) for i in
           range(len(sat_data))]

    for i in range(len(names)):
        # print(names[i])
        if len(res[i][0]) > 0:
            print(names[i])
            for t in res[i][0]:
                # print(res[i])
                print(t.utc_datetime().date(), t.utc_datetime().time())
                ll = wgs84.latlon_of(sat_data[i].at(t))
                print(ll[0].degrees, ",", ll[1].degrees)
                print()

    for i in range(len(names)):
        if len(res[i]) > 0:
            for t in res[i][0]:
                ll = wgs84.latlon_of(sat_data[i].at(t))
                draw_point2(map, [ll[0].degrees, ll[1].degrees], color=colors[i])

for i in range(len(sat_names)):
    plt.scatter([0], [0], color=colors[i], label=names[i])
# plt.scatter([0], [0], color='red', label='Haiyang-2B')
# plt.scatter([0], [0], color='green', label='Saral')
# plt.scatter([0], [0], color='yellow', label='CfoSat')

plt.legend(loc='upper left')

plt.show()
