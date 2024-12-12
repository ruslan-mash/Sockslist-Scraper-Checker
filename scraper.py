import requests
import re
import time
from fake_useragent import UserAgent
import json
from proxy_checking import ProxyChecker
from datetime import datetime
from django.http import HttpRequest

proxies_list = []  # Список найденных прокси из всех источников
validated_socks = []  # Список валидированных прокси
checked_socks = []  # Список проверенных повторно прокси
start_time = time.time()
header = {'User-Agent': UserAgent().random}

# Источники прокси socks5 в формате json
geonode_sources = (
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=1&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=2&sort_by=lastChecked&sort_type=desc",
    "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=3&sort_by=lastChecked&sort_type=desc",

)

# Источники прокси socks5 в формате txt
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


class ProxyValidator():
    def __init__(self, proxies_list, validated_socks, checked_socks, start_time, header, geonode_sources, txt_sources):
        self.proxies_list = proxies_list  # Список найденных прокси из всех источников
        self.validated_socks = validated_socks  # Список валидированных прокси
        self.checked_socks = checked_socks  # Список проверенных повторно прокси
        self.start_time = start_time
        self.header = header
        self.geonode_sources = geonode_sources
        self.txt_sources = txt_sources

    def get_data_from_geonode(self):
        base_url = "https://proxylist.geonode.com/api/proxy-list?protocols=socks4%2Csocks5&limit=500"
        try:
            response = requests.get(f"{base_url}&page=1&sort_by=lastChecked&sort_type=desc", headers=self.header)
            response.raise_for_status()
            total = response.json().get('total', 0)
            print(f"Total proxies available: {total}")

            total_pages = (total // 500) + 1
            for number_page in range(1, total_pages + 1):
                page_url = f"{base_url}&page={number_page}&sort_by=lastChecked&sort_type=desc"
                try:
                    response = requests.get(page_url, headers=self.header)
                    response.raise_for_status()
                    data = response.json().get('data', [])
                    for entry in data:
                        ip = entry.get('ip')
                        port = entry.get('port')
                        if ip and port:
                            self.proxies_list.append(f"{ip}:{port}")
                    print(f"Page {number_page} processed. Total proxies collected: {len(self.proxies_list)}")
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка получения прокси из {page_url}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения информации из {base_url}: {e}")


    def get_data_from_socksus(self):
        url = "https://sockslist.us/Api?request=display&country=all&level=all&token=free"
        try:
            response = requests.get(url=url, headers=self.header)
            response.raise_for_status()
            data = response.json()
            # Debugging: Print the data format to check its structure
            # print("Response data from sockslist.us:", data)
            # Assuming data is a list of dictionaries, we process it
            if isinstance(data, list):
                for entry in data:
                    # Check if entry is a dictionary before accessing 'ip' and 'port'
                    if isinstance(entry, dict):
                        ip = entry.get('ip')
                        port = entry.get('port')
                        if ip and port:
                            self.proxies_list.append(f"{ip}:{port}")
                    else:
                        print(f"Skipping invalid entry: {entry}")
            else:
                print("Expected list format, but received:", type(data))
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения прокси из {url}: {e}")


    def get_data_from_txt(self):
        pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'
        for url in self.txt_sources:
            try:
                response = requests.get(url=url, headers=self.header)
            except requests.exceptions.RequestException as e:
                print(f"Ошибка получения прокси из {url}: {e}")
                continue
            if response.ok:
                proxy_list = response.text.splitlines()
                proxy_list_filtered = re.findall(pattern, "\n".join(proxy_list))
                self.proxies_list.extend(proxy_list_filtered)

    def check_proxy(self, url, timeout=5):
        for count, proxy in enumerate(set(self.proxies_list), start=1):
            proxy_dict = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            # Try SOCKS5 first, then SOCKS4 if SOCKS5 fails
            try:
                response = requests.get(url=url, headers=self.header, proxies=proxy_dict, timeout=timeout)
                if response.ok:
                    self.validated_socks.append(proxy)
                    print(f"Прокси {proxy} валидный через SOCKS5, статус: {response.status_code}")
                continue
            except requests.exceptions.RequestException:
                # Switch to SOCKS4
                proxy_dict = {
                    'http': f'socks4://{proxy}',
                    'https': f'socks4://{proxy}'
                }
                try:
                    response = requests.get(url=url, headers=self.header, proxies=proxy_dict, timeout=timeout)
                    if response.ok:
                        self.validated_socks.append(proxy)
                        print(f"Прокси {proxy} валидный через SOCKS4, статус: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Ошибка проверки прокси {proxy}: {e}")

    def check_proxy_with_checker(self):
        checker = ProxyChecker()

        for proxy in self.validated_socks:
            result = checker.check_proxy(proxy)
            if result.get("status") == True:
                ip, port = proxy.split(':')
                result['ip'] = ip
                result['port'] = port
                result['date'] = datetime.today().date().strftime('%Y-%m-%d')  # Преобразование даты в строку
                result['time'] = datetime.today().time().strftime('%H:%M:%S')  # Преобразование времени в строку
                self.checked_socks.append(result)
            elapsed_time = time.time() - self.start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            print(
                f'Всего проверено {len(self.checked_socks)} из {len(self.validated_socks)}, прошло {hours} часов {minutes} минут {seconds} секунд')

        return self.checked_socks

    def save_results(self, checked_socks):
        today = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        try:
            with open(f'checked_socks_{today}.json', 'w') as json_file:
                json.dump(checked_socks, json_file, indent=4)
            print(f"Результаты проверки записаны в файл checked_socks{today}.json")
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")

    def run(self):
        self.get_data_from_geonode()
        self.get_data_from_socksus()
        self.get_data_from_txt()
        print(f'Найдено {len(set(self.proxies_list))} прокси')

        self.check_proxy('https://cloudflare.com')

        print(f'Валидировано через url {len(self.validated_socks)} прокси')

        checked_socks = self.check_proxy_with_checker()

        self.save_results(checked_socks)

        total_elapsed_time = time.time() - self.start_time
        total_hours = int(total_elapsed_time // 3600)
        total_minutes = int((total_elapsed_time % 3600) // 60)
        total_seconds = int(total_elapsed_time % 60)
        print(f"--- Всего затрачено {total_hours} часов {total_minutes} минут {total_seconds} секунд ---")


# Создание экземпляра класса и запуск процесса
proxy_validator = ProxyValidator(proxies_list, validated_socks, checked_socks, start_time, header, geonode_sources, txt_sources)
proxy_validator.run()
