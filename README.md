# WavesOnAltimeters

В репозитории размещены наработанные скрипты по 
- обработке данных альтиметрии (TrackProcess)
- прогнозированию пролетов альтиметров (FlyForecast)

## Установка

Ничего сверхестественного.

```sh
git clone https://github.com/leeiozh/WavesOnAltimeters.git
cd WavesOnRadar
conda create -y --name alti_env python=3.10
conda install --force-reinstall -y -q --name alti_env -c conda-forge --file requirements.txt
conda activate alti_env
```

Если вы собираетесь использовать прогнозера пролетов, **обязательно** регулярно обновляйте данные об орбите спутников.

```sh
cd FlyForecast
python update_tle.py
```