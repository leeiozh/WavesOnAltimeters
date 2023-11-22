from skyfield.api import load, wgs84
import geopandas as gpd
import fiona
import sys

sys.path.append(__file__[:-23] + "src")
from src.drawers import *
from src.converters import *


# ПЕРЕМЕННЫЕ НИЖЕ НЕОБХОДИМО ПОДОГНАТЬ ПОД СВОИ ЗАДАЧИ
START_TIME = dt.datetime(2023, 9, 15, 15, 0, 0, tzinfo=dt.timezone.utc)  # время старта расчета
TRACK_FILE = "track/asv55.kml"
SCHEDULE_FILE = "schedule_asv55.xlsx"
SPEED = 6  # предполагаемая скорость в узлах
END_TIME = 40  # количество суток расчета
MAX_DISTANCE = 200  # максимальное расстояние по поверхности между треком судна и спутника в километрах

plt.figure()
# для отрисовки карты нужно указать крайние наносимые координаты
map = make_map(left=-20, right=30, up=60, down=30)  # для европы и средиземья
# map = make_map(left=-70, right=-50, up=-50, down=-70) # для антарктики
# для отрисовки сетки нужно указать ее шаг
draw_grid(map, lat_step=5, lon_step=5)

# ДАЛЬШЕ НИЧЕГО ТРОГАТЬ НЕ НУЖНО!! ДАЛЬШЕ НИЧЕГО ТРОГАТЬ НЕ НУЖНО!! ДАЛЬШЕ НИЧЕГО ТРОГАТЬ НЕ НУЖНО !!
# подгрузка данных о спутниках из файла
sats = load.tle_file('tle/tle_data.txt')
names = ['CFOSAT', 'HAIYANG-2B', 'JASON-3', 'SARAL', 'SENTINEL-3A', 'SENTINEL-3B', 'SENTINEL-6', 'CRYOSAT 2']
sat_names = {sat.name: sat for sat in sats}
sat_data = [sat_names[name] for name in names]

KML_OR_TXT = (TRACK_FILE[-3:] == 'kml')  # флаг, юзать данные из KML (долгосрочный прогноз) или TXT (на пару дней)

if KML_OR_TXT:
    # загрузка координат из KML, который генерирует OpenCPN
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    geo_df = gpd.read_file(TRACK_FILE, driver='KML')
    track_df = pd.DataFrame(geo_df)["geometry"]
    station_pos_ll = np.array([wgs84.latlon(track_df[i].y, track_df[i].x) for i in range(track_df.shape[0] - 1)])
    track_time = calc_time(track_df, START_TIME, speed=SPEED)
    draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
                track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
                color1='white', color2='black', track_time=track_time)

else:
    # загрузка координат из txt, который мы забили руками
    df = pd.read_csv(TRACK_FILE, sep=" ")
    station_pos = np.zeros((df.shape[0], 2))
    station_pos[:, 0] = np.sign(df["lat_deg"].to_numpy()) * (
            np.abs(df["lat_deg"].to_numpy()) + df["lat_min"].to_numpy() / 60)
    station_pos[:, 1] = np.sign(df["lon_deg"].to_numpy()) * (
            np.abs(df["lon_deg"].to_numpy()) + df["lon_min"].to_numpy() / 60)
    station_pos_ll = np.array([wgs84.latlon(ll[0], ll[1]) for ll in station_pos])

    # отрисовка станций
    draw_coords(map, track_lat=[ll.latitude.degrees for ll in station_pos_ll],
                track_lon=[ll.longitude.degrees for ll in station_pos_ll], track_buoy=np.ones(len(station_pos_ll)),
                color1='white', color2='black')  # , track_time=track_time
colors = ['yellow', 'red', 'orange', 'green', 'blue', 'purple', 'pink', 'grey']
color_rgd = ['FFFF00', 'FF0000', 'FF8000', '009900', '0080FF', '7F00FF', 'FFCCFF', 'C0C0C0']

height = np.array([519, 966, 1336, 781, 814, 804, 1336, 728])  # height of altimeters orbits
alt = 90 - calc_alt(MAX_DISTANCE, height) / np.pi * 180

res_list = []

for n in range(station_pos_ll.shape[0] - 1):  # цикл по станциям

    ts = load.timescale()
    res_list.append([])

    if not KML_OR_TXT:
        time1 = dt.datetime.strptime(df["date_time"][n], '%Y-%m-%d_%H-%M')
        time1 = time1.replace(tzinfo=dt.timezone.utc)
        time1 = ts.from_datetime(time1)
        time2 = dt.datetime.strptime(df["date_time"][n + 1], '%Y-%m-%d_%H-%M')
        time2 = time2.replace(tzinfo=dt.timezone.utc)
        time2 = ts.from_datetime(time2)
    else:
        time1 = ts.from_datetime(track_time[n])
        time2 = ts.from_datetime(track_time[n + 1])

    for i in range(len(names)):  # цикл по спутникам

        res_sat = sat_data[i].find_events(station_pos_ll[n], time1, time2, altitude_degrees=alt[i])

        if len(res_sat[0]) > 0:
            print(names[i])
            for t in res_sat[0]:
                ll = wgs84.latlon_of(sat_data[i].at(t))
                if len(res_sat[0]) == 3 and t == res_sat[0][1]:
                    dist_km = dist.geodesic((ll[0].degrees, ll[1].degrees), (
                        station_pos_ll[n].latitude.degrees, station_pos_ll[n].longitude.degrees)).km

                    res_list[n].append(
                        {'sat_name': names[i], 'date': t.utc_datetime().date().strftime("%Y-%m-%d"),
                         'time': t.utc_datetime().time().strftime("%H:%M"),
                         'dist': dist_km, 'color': color_rgd[i]})

                    # вывод в консоль времени и координат ближайшей к треку точки пролета
                    print(t.utc_datetime().date(), t.utc_datetime().time().strftime("%H:%M"))
                    print("sat_coords", ll[0].degrees, ",", ll[1].degrees, "; min dist", dist_km, "km")
                    print()

                # отрисовка на карте трех точек: начало и конец попадания спутника в указанный радиус,
                # между ними кульминация
                draw_point(map, [ll[0].degrees, ll[1].degrees], color=colors[i], alpha=1., flag=False)

    res_list[n] = sorted(res_list[n], key=lambda x: x['time'])

if KML_OR_TXT:
    res_sheet = prepare_sheet(START_TIME, END_TIME)
    print(res_list)
    convert_list(SCHEDULE_FILE, res_sheet, res_list)

# отрисовка легенды
for i in range(len(sat_names)):
    plt.scatter([0], [0], color=colors[i], label=names[i])

plt.legend(loc='best', fontsize="6")
plt.savefig('pics/' + TRACK_FILE[6:-4] + '.png', bbox_inches='tight', dpi=1000)
plt.show()
