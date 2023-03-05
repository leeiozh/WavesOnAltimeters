import numpy as np


def check_nearest_data(sat: np.ndarray, sec: float) -> (int, float):
    """
    Находит ближайшую по времени точку данных со спутника
    :param sat: данные со спутника
    :param sec: время снятия измерений
    :return: индекс ближайшей по времени точки и ее разницу во времени
    """

    return np.argmin(abs(sat[0] - sec)), np.min(abs(sat[0] - sec))


def check_nearest_data_mean(sat: np.ndarray, sec_start: float, sec_end: float) -> (int, float):
    """
    Находит ближайшую по времени точку данных со спутника
    :param sat: данные со спутника
    :param sec_start: время начала измерений
    :param sec_end: время конца измерений
    :return: индекс ближайшей по времени точки и ее разницу во времени
    """

    time_mean = 0.5 * (sec_start + sec_end)

    return np.argmin(abs(sat[0] - time_mean)), np.min(abs(sat[0] - time_mean))


def get_area_coords(sat: np.ndarray, fmin: (int, float), num: int) -> (np.ndarray, np.ndarray, np.ndarray):
    """
    Возвращает кусок траектории спутника в окрестности точки, ближайшей по времени с заданным окном по времени
    :param sat: данные со спутника
    :param fmin: (индекс ближайшей по времени точки, разница во времени)
    :param num: окно по данным
    :return: [широта спутника в указанном окне, долгота спутника в указанном окне]
    """
    if fmin[1] > num:
        return 0, 0
    start = max(0, fmin[0] - num)
    end = min(fmin[0] + num + 1, len(sat[1]))
    return np.array([sat[i][start:end] for i in range(4)]), 1


def is_near_sat(sat_area: np.ndarray, track: np.ndarray, deg: float) -> (bool, float):
    """
    Проверяет, находится ли спутник в окрестности положения судна
    :param sat_area: кусок траектории спутника
    :param track: координаты судна
    :param deg: окно по координатам в градусах
    :return: попадает ли кусок траектории спутника в окно трека судна
    """
    if track[1] < 0:  # перевод долготы трека в долготу спутника
        tmp_track = [track[0], track[1] + 360]
        dist = np.abs(np.linalg.norm(sat_area - tmp_track))
        if dist < deg:
            return True, dist
        else:
            return False, dist
    else:
        dist = np.abs(np.linalg.norm(sat_area - track[:2]))
        if np.abs(np.linalg.norm(sat_area - track[:2])) < deg:
            return True, dist
        else:
            return False, dist
