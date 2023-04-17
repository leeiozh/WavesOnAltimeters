# WavesOnAltimeters

В репозитории размещены наработанные скрипты по 
- обработке данных альтиметрии (TrackProcess)
- прогнозированию пролетов альтиметров (FlyForecast)

## Установка

Ничего сверхестественного.

```sh
git clone https://github.com/leeiozh/WavesOnAltimeters.git
cd WavesOnAltimeters
conda create -y --name alti_env python=3.10
conda install --force-reinstall -y -q --name alti_env -c conda-forge --file requirements.txt
conda activate alti_env
```

Альтернативно без conda:
```sh
pip install -r requirements.txt
```

## Использование

Если вы собираетесь использовать прогнозера пролетов, **обязательно** регулярно обновляйте данные об орбите спутников.

```sh
cd FlyForecast
python update_tle.py
```

Если вы собираетесь обрабатывать данные рейсов, необходимо выкачать данные с альтиметров. Например, для АИ63 они размещены по адресу https://disk.yandex.ru/d/zS_iJN8qjlr2bA . Остальные вырезки данных могу предоставить по отдельному запросу.

Путь к подобной папке необходимо указывать внутри переменной 
```python
sat_data = read_sat_data('/your_path/AI63_SatelliteData/', sat_names)
```

В свою очередь данные о положении и времени измерений необходимо задавать по образу и подобию файлов из папки TrackProcess/track