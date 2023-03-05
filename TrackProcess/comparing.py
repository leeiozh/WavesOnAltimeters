import readers
import checkers
import drawers
import converters
import matplotlib.pyplot as plt
import numpy as np
from skyfield.api import load, wgs84

WIN_TIME = 7200  # окно по времени в секундах
WIN_ANGLE = 2.5  # окно по координате в градусах

fig, axs = plt.subplots(1, 2, figsize=(20, 10), facecolor='w', edgecolor='k')
fig.subplots_adjust(hspace=.3, wspace=.3)

axs = axs.ravel()

# чтение треков
track_ship = readers.read_track_height('../proc_only_height.csv')

sat_names = ['j3', 'cfo', 'al', 'h2b', 'c2']  # 's3a', 's3b',
sat_labels = ['Jason-3', 'CFOSAT', 'SARAL', 'HaiYang-2B', 'CryoSat-2']  # 'Sentinel-3A', 'Sentinel-3B',
sat_data = readers.read_sat_data('10', sat_names)

print("tracks uploaded successfully")
#
# # отрисовка карты
# station_pos_ll = np.array([wgs84.latlon(ll[0], ll[1]) for ll in track_ship[:, 1:3]])
# map = drawers.make_map()
# drawers.draw_grid(map)
# drawers.draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
#                     track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
#                     color1='white', color2='black')
colors = ['orange', 'red', 'blue', 'purple', 'green'] #'yellow', 'pink',
#
# отрисовка легенды
for l in range(len(sat_names)):
    plt.scatter([-1], [-1], color=colors[l], label=sat_labels[l])
plt.legend(prop={'size': 10})


for t in range(len(track_ship[:, 2])):  # цикл по времени
    color_num = -1

    for sat_dat in sat_data:  # цикл по спутникам
        sat_dat = np.array(sat_dat)
        color_num += 1
        sat_near_ship = checkers.get_area_coords(sat_dat, checkers.check_nearest_data(sat_dat, track_ship[t, 2]),
                                                 WIN_TIME)
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[0])
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[1])
        sat_track = []
        time = []

        lat_lon_min = [0, 0]
        dist_min = WIN_ANGLE
        p_min = 0

        for p in range(len(sat_near_ship[0])):  # цикл по точкам в куске траектории, находящемся в окне по времени

            lat_lon = sat_near_ship[1:3, p]
            near, dist = checkers.is_near_sat(lat_lon, track_ship[t, 3:5], WIN_ANGLE)

            if near:
                alpha = max(1 - np.abs(sat_near_ship[0, p] - track_ship[t, 2]) / WIN_TIME / 2, 0.3)
                # drawers.draw_point(map, lat_lon, colors[color_num], alpha)

                if dist < dist_min:
                    lat_lon_min = lat_lon
                    dist_min = dist
                    p_min = p

        if p_min != 0:
            # print(lat_lon_min)

            sat_track.append(np.array([dist_min, sat_near_ship[3][p_min]]))
            time.append(1 / 60 * np.abs(sat_near_ship[0, p_min] - track_ship[t, 2]))

            # plt.annotate(str(int(track_ship[:, 0][t])), xy=(track_ship[t, 2], track_ship[t, 1]), xycoords="data",
            #              xytext=(30, 0),
            #              textcoords='offset points', ha="left", va="center", fontsize=11,
            #              bbox=dict(boxstyle="round", facecolor="w",
            #                        edgecolor="0.5", alpha=0.5))
            #
            # plt.plot([-360 + lat_lon_min[1], track_ship[t, 2]], [lat_lon_min[0], track_ship[t, 1]],
            #          color=colors[color_num], alpha=alpha)

        if len(sat_track) > 0:
            # print(sat_track)
            print(sat_names[color_num], converters.sec_to_utc(sat_near_ship[0, p_min]), sat_track[0][0], time[0], sat_track[0][1], track_ship[t, -1])
            axs[0].scatter([track_ship[t, -1]], [sat_track[0][1]], color=colors[color_num], alpha=alpha)
            axs[1].scatter([track_ship[t, -4]], [sat_track[0][1]], color=colors[color_num], alpha=alpha)

left = 0.5
right = 4.5

for i in range(2):

    axs[i].plot([left, right], [left, right], color='black')
    axs[i].set_xlim(left, right)
    axs[i].set_ylim(left, right)
    axs[i].grid(linestyle=':')
    axs[i].set_ylabel('satellite')

axs[0].set_xlabel('buoy')
axs[1].set_xlabel('average observer')

plt.savefig('ai63_comparing.png', dpi=1000)
plt.show()
