import requests

# чтение файла с ссылками на данные
data = open('tle/tle_data.txt', 'w')

with open('tle/tle_sites.txt', 'r') as file:
    res = []
    for line in file:  # цикл по стутникам
        # запись в файл
        f = requests.get(line)
        data.write(f.text)
        data.write('\n')
        print(f.text[:13], 'successfully update')

data.close()
