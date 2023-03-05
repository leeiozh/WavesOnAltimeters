import readers
import checkers
import drawers
import converters
import matplotlib.pyplot as plt
import numpy as np
from skyfield.api import load, wgs84

WIN_TIME = 7200  # окно по времени в секундах
WIN_ANGLE = 2.5  # окно по координате в градусах

fig, axs = plt.subplots(1, 1, figsize=(7, 7), facecolor='w', edgecolor='k')

# чтение треков
track_ship = readers.read_track('../true_coords.csv')
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
colors = ['orange', 'red', 'blue', 'purple', 'green', 'yellow', 'pink']

# отрисовка легенды
for l in range(len(sat_names)):
    xpt, ypt = map(sat_data[0][1][0], sat_data[0][0][0])
    map.scatter(xpt, ypt, color=colors[l], label=sat_labels[l])
plt.legend(loc="center right", prop={'size': 10}, framealpha=1)


for t in range(len(track_ship[:, 3])):  # цикл по времени
    color_num = -1

    for sat_dat in sat_data:  # цикл по спутникам
        sat_dat = np.array(sat_dat)
        color_num += 1
        sat_near_ship, flag = checkers.get_area_coords(sat_dat, checkers.check_nearest_data_mean(sat_dat, track_ship[t, 3],
                                                                                      track_ship[t, 4]), WIN_TIME)
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[0])
        # plt.plot(np.arange(len(sat_near_ship[0])), sat_near_ship[1])
        sat_track = []
        time = []
        lat_sat = []
        lon_sat = []

        if flag:
            lat_lon_min = [0, 0]
            dist_min = WIN_ANGLE
            p_min = 0

            for p in range(len(sat_near_ship[0])):  # цикл по точкам в куске траектории, находящемся в окне по времени

                lat_lon = sat_near_ship[1:3, p]
                near, dist = checkers.is_near_sat(lat_lon, track_ship[t, 1:3], WIN_ANGLE)

                if near:
                    alpha = min(1 - np.abs(sat_near_ship[0, p] - (track_ship[t, 3] + track_ship[t, 4]) / 2) / WIN_TIME, 0.8)
                    alpha = max(1 - np.abs(sat_near_ship[0, p] - (track_ship[t, 3] + track_ship[t, 4]) / 2) / WIN_TIME, 0.2)
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
                time.append(1 / 60 * np.abs(sat_near_ship[0, p_min] - (track_ship[t, 3] + track_ship[t, 4]) / 2))

                # plt.annotate(str(int(track_ship[:, 0][t])), xy=(track_ship[t, 2], track_ship[t, 1]), xycoords="data", xytext=(30, 0),
                #              textcoords='offset points', ha="left", va="center", fontsize=10, bbox=dict(boxstyle="round", facecolor="w",
                #       edgecolor="0.5", alpha=0.5))

                plt.plot([-360 + lat_lon_min[1], track_ship[t, 2]], [lat_lon_min[0], track_ship[t, 1]], color=colors[color_num], alpha=alpha)

        if len(sat_track) > 0:
            # print(sat_track)
            print(int(track_ship[:, 0][t]), sat_labels[color_num], converters.sec_to_utc(sat_near_ship[0, p_min]),
                  sat_track, time)
            # print(track_ship[t, 1], track_ship[t, 2], color_num, alpha, lat_sat, lon_sat)
            # print(str(int(track_ship[:, 0][t])), str(sat_labels[color_num]), sat_track[:], time)

plt.savefig('ai63_map_buoy.png', dpi=700, transparent=True)
plt.show()

# /home/leeiozh/ocean/SatelliteForecast/venve/bin/python /home/leeiozh/ocean/SatelliteForecast/proc.py
# tracks uploaded successfully
# h2b 4338 2022-10-07 17:11:00 2.2406640797163133 0.4569953957448844 0.49115248393750877
# h2b 4340 2022-10-08 17:49:00 1.5336422083120425 0.46540557844318675 0.6947107080148806
# j3 4342 2022-10-09 15:54:00 1.6911331593282766 0.11573705150018379 0.3831259055748617
# h2b 4342 2022-10-09 15:54:00 2.0892062606339894 0.09240817487505427 0.024243789898344036
# al 4343 2022-10-10 07:11:00 1.5923012040357838 0.28644683320916564 0.5936477880517842
# cfo 4344 2022-10-10 17:24:00 1.844667268715504 0.2829063295686128 0.43385466001943523
# h2b 4345 2022-10-11 06:44:00 1.3036266453765333 0.4533290610664889 0.8807824861145397
# c2 4351 2022-10-14 07:31:00 1.6690920015455764 0.107528387370221 0.2475404030959857
# cfo 4352 2022-10-14 17:50:00 2.2897516282347343 0.469665478391317 0.40338071205011006
# al 4352 2022-10-14 17:50:00 1.9084895615199842 0.22495435306163414 0.004623789855042464
# al 4353 2022-10-15 07:09:00 2.172005731823356 0.2839616633215443 0.17789491623046644
# h2b 4355 2022-10-16 05:22:00 1.339301227018097 0.050720222269609185 0.7042865243278398
# h2b 4356 2022-10-16 16:54:00 2.095029262193154 1.1063429281419097 0.8859531250094111
# cfo 4358 2022-10-19 17:50:00 2.1127442250832638 0.6005638068812603 0.4435322861924364
# h2b 4364 2022-10-21 15:48:00 2.3548129100105224 0.23288634031964528 0.19388966860877907
