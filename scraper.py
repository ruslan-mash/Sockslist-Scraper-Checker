# Получаем SOCKS5 прокси из интернет-списков, проверяем через запрос на url,
# записываем валидированные результаты ip:port в файл txt

import requests
import re
import time
from fake_useragent import UserAgent
import json
from proxy_checking import ProxyChecker
from datetime import datetime

start_time = time.time()

proxies_list = []  # список найденных прокси из всех источников
validated_socks = []  # список валидированнных прокси

# Заголовок для маскировки под браузер (генерация случайного User-Agent за каждый запрос)
ua = UserAgent()
header = {'User-Agent': ua.random}

# Источники прокси socks5 в формате json из Интернета
json_sources = (
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=1&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=2&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=3&sort_by=lastChecked&sort_type=desc",
)


# Функция для получения данных из JSON источников
def get_data_from_json():
    for url in json_sources:
        try:
            response = requests.get(url=url, headers=header)  # получаем json из источника
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения прокси из {url}: {e}")
            continue

        if response.ok:
            data = response.json().get('data', [])
            for entry in data:
                ip = entry.get('ip')
                port = entry.get('port')
                if ip and port:
                    proxies_list.append(f"{ip}:{port}")


# Получение данных из источника json
get_data_from_json()

# Источники прокси socks5 в формате txt из Интернета
txt_sources = (
    "https://spys.me/socks.txt",
    "https://www.proxy-list.download/api/v1/get?type=socks5&anon=elite",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt",
    "https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt",
)
# Паттерн для фильтрации по ip:port из источника
pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'


# Извлекаем все прокси из списка URL-адресов источников прокси

def get_data_from_txt():
    for url in txt_sources:
        try:
            responce = requests.get(url=url, headers=header)  # получаем список ip:port из источника
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения прокси из {url}: {e}")
            continue

        if responce.ok:
            proxy_list = responce.text.splitlines()  # разделяем ответ на строки
            proxy_list_filtered = re.findall(pattern, "\n".join(
                proxy_list))  # Объединяем строки списка в единую строку для применения паттерна поиска и применяем паттерн поиска
            proxies_list.extend(proxy_list_filtered)  # добавляем отфильтрованные данные в proxies_list


# Вызов функции для получения прокси из txt
get_data_from_txt()

founded_proxy = set(proxies_list)  # массив найденных прокси с удаленными дубликатами

# Принт промежуточная проверка результатов
print(f'Найдено {len(founded_proxy)} прокси')
print(f'Ранее удалено {len(proxies_list) - len(founded_proxy)} дубликатов')


# Проверка найденных прокси на работоспособность через url
def check_proxy(url, timeout=5):
    for count, proxy in enumerate(founded_proxy, start=1):
        proxy_dict = {
            'http': f'socks5://{proxy}',
            'https': f'socks5://{proxy}'
        }
        print(
            f' Проверяется {proxy}, всего проверено {count} из {len(founded_proxy)}, прошло  {(time.time() - start_time) // 3600} часов {(time.time() - start_time) % 3600 // 60} минут {(time.time() - start_time) % 60} секунд')  # потом удалить

        try:
            responce = requests.get(url=url, headers=header, proxies=proxy_dict, timeout=timeout)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка проверки прокси  {proxy}: {e}")
        continue
        if responce.ok:
            validated_socks.append(proxy)
            print(f"Прокси {proxy} валидный, статус: {responce.status_code}")  # принт о прохождении потом удалить


# Вызов функции для проверки прокси через url
check_proxy('https://google.com')

# принты проверки выполнения
print(f'Валидировано через url {len(validated_socks)} прокси')  # потом удалить

# Дополнительная проверка валидированных прокси, получение дополнительной информации,

# Инициализация ProxyChecker
checker = ProxyChecker()
result_proxychecker = []

# Проверка прокси через ProxyChecker и запись результатов
def check_proxy_with_checker():
    for proxy in validated_socks:
        result = checker.check_proxy(proxy)
        if result.get("status") == 1:
            ip, port = proxy.split(':')
            result['ip'] = ip
            result['port'] = port
            result['date'] = datetime.today().date()  # Получение текущей даты
            result['time'] = datetime.today().time()  # Получение текущего времени
            result_proxychecker.append(result)
        # Вывод текущего времени выполнения и количество проверенных прокси #потом удалить
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        print(
            f'Всего проверено {len(result_proxychecker)} из {len(validated_socks)}, прошло {hours} часов {minutes} минут {seconds} секунд')  # потом удалить


# Вызов функции для проверки прокси
check_proxy_with_checker()

# Запись результатов в JSON файл c датой проверки
today = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
with open(f'result_proxychecker_{today}.json', 'w') as json_file:
    json.dump(result_proxychecker, json_file, indent=4)


print(f"Результаты проверки записаны в файл result_proxychecker_{datetime.today()}.json")  # принт потом удалить

# Общие затраты времени #потом удалить
total_elapsed_time = time.time() - start_time
total_hours = int(total_elapsed_time // 3600)
total_minutes = int((total_elapsed_time % 3600) // 60)
total_seconds = int(total_elapsed_time % 60)
print(f"--- Всего затрачено {total_hours} часов {total_minutes} минут {total_seconds} секунд ---")
