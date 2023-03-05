import readers
import checkers
import drawers
import converters
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skyfield.api import load, wgs84

WIN_TIME = 7200  # окно по времени в секундах
WIN_ANGLE = 2.5  # окно по координате в градусах

fig, axs = plt.subplots(1, 1, figsize=(14, 7), facecolor='w', edgecolor='k')

# чтение треков
df = pd.read_csv('../station_coords.csv', delimiter=',')
track_ship = readers.read_track_radar('../station_coords.csv')
sat_names = ['j3', 'cfo', 'al', 'h2b', 'c2', 's3a', 's3b']
sat_labels = ['Jason-3', 'CFOSAT', 'SARAL', 'HaiYang-2B', 'CryoSat-2', 'Sentinel-3A', 'Sentinel-3B']
sat_data = readers.read_sat_data('10', sat_names)

print("tracks uploaded successfully")

# отрисовка карты
station_pos_ll = np.array([wgs84.latlon(ll[0], ll[1]) for ll in track_ship[:, 1:3]])
map = drawers.make_map()
drawers.draw_grid(map)
drawers.draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
                    track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
                    color1='white', color2='black')
colors = ['orange', 'blue', 'yellow', 'green', 'red', 'purple', 'pink']

# отрисовка легенды
for l in range(len(sat_names)):
    xpt, ypt = map(sat_data[0][1][0], sat_data[0][0][0])
    map.scatter(xpt, ypt, color=colors[l], label=sat_labels[l])
# plt.legend(loc="center right", prop={'size': 10}, framealpha=1)


for t in range(len(track_ship[:, 0])):  # цикл по времени
    color_num = -1

    for sat_dat in sat_data:  # цикл по спутникам
        sat_dat = np.array(sat_dat)
        color_num += 1
        sat_near_ship, flag = checkers.get_area_coords(sat_dat, checkers.check_nearest_data(sat_dat, track_ship[t, 0]), WIN_TIME)
        sat_track = []
        time = []

        lat_sat = []
        lon_sat = []
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[0])
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[1])
        if flag:

            lat_lon_min = [0, 0]
            dist_min = WIN_ANGLE
            p_min = 0

            for p in range(len(sat_near_ship[0])):  # цикл по точкам в куске траектории, находящемся в окне по времени

                lat_lon = sat_near_ship[1:3, p]
                near, dist = checkers.is_near_sat(lat_lon, track_ship[t, 1:3], WIN_ANGLE)

                if near:
                    alpha = min(1 - np.abs(sat_near_ship[0, p] - (track_ship[t, 0])) / WIN_TIME, 0.8)
                    alpha = max(1 - np.abs(sat_near_ship[0, p] - (track_ship[t, 0])) / WIN_TIME, 0.2)
                    drawers.draw_point(map, lat_lon, colors[color_num], alpha)

                    if dist < dist_min:
                        lat_lon_min = lat_lon
                        dist_min = dist
                        p_min = p
                    lat_sat.append(lat_lon[0])
                    lon_sat.append(lat_lon[1])

            if p_min != 0:

                # print(lat_lon_min)

                sat_track.append(np.array([dist_min, sat_near_ship[3][p_min]]))
                time.append(1 / 60 * np.abs(sat_near_ship[0, p_min] - (track_ship[t, 0])))

                # plt.annotate(str(int(track_ship[:, 0][t])), xy=(track_ship[t, 2], track_ship[t, 1]), xycoords="data", xytext=(30, 0),
                #              textcoords='offset points', ha="left", va="center", fontsize=10, bbox=dict(boxstyle="round", facecolor="w",
                #       edgecolor="0.5", alpha=0.5))

                # plt.plot([-360 + lat_lon_min[1], track_ship[t, 2]], [lat_lon_min[0], track_ship[t, 1]], color=colors[color_num], alpha=alpha)

        if len(sat_track) > 0:
            # print(track_ship[t, 1], track_ship[t, 2], color_num, alpha, lat_sat, lon_sat)
            # print(sat_track)
            # print(int(track_ship[:, 0][t]), sat_labels[color_num], converters.sec_to_utc(sat_near_ship[0, p_min]),
            #       sat_track, time)
            # print(str(df["name"].loc[t]) + "," + str(sat_labels[color_num]))
            print(str(df["name"].loc[t]), str(sat_labels[color_num]), sat_track[:], time)

plt.savefig('ai63_radar_pasta.png', dpi=700, transparent=True)
plt.show()
