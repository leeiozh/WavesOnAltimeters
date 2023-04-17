import requests

data = open('tle/tle_data.txt', 'w')

with open('tle/tle_sites.txt', 'r') as file:
    res = []
    for line in file:
        f = requests.get(line)
        data.write(f.text)
        data.write('\n')
        print(f.text[:13], 'successfully update')

data.close()

