import requests
import re
import time
from fake_useragent import UserAgent
import json
from proxy_checking import ProxyChecker
from datetime import datetime
from django.http import HttpRequest




class ProxyValidator:
    def __init__(self):
        self.proxies_list = []  # Список найденных прокси из всех источников
        self.validated_socks = []  # Список валидированных прокси
        self.result_proxychecker = [] # Список проверенных повторно прокси
        self.start_time = time.time()
        self.ua = UserAgent()
        self.header = {'User-Agent': self.ua.random}

        # Источники прокси socks5 в формате json
        self.json_sources = (
            # "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            # "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=2&sort_by=lastChecked&sort_type=desc",
            # "https://proxylist.geonode.com/api/proxy-list?protocols=http&limit=500&page=3&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=2&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?anonymityLevel=elite&protocols=socks5&limit=500&page=3&sort_by=lastChecked&sort_type=desc",

        )

        # Источники прокси socks5 в формате txt
        self.txt_sources = (
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

        self.pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'

    def get_data_from_geonode(self):
        for url in self.json_sources:
            try:
                response = requests.get(url=url, headers=self.header)
            except requests.exceptions.RequestException as e:
                print(f"Ошибка получения прокси из {url}: {e}")
                continue
            if response.ok:
                data = response.json().get('data', [])
                for entry in data:
                    ip = entry.get('ip')
                    port = entry.get('port')
                    if ip and port:
                        self.proxies_list.append(f"{ip}:{port}")

    def get_data_from_socksus(self):
        url = "https://sockslist.us/Api?request=display&country=all&level=all&token=free"
        try:
            response = requests.get(url=url, headers=self.header)
            response.raise_for_status()  # Check if the request was successful
        except requests.exceptions.RequestException as e:
            print(f"Error fetching proxies from {url}: {e}")
            if response.ok:
                data = response.json()
                # Debugging: Print the data format to check its structure
                print("Response data from sockslist.us:", data)

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



    def get_data_from_txt(self):
        for url in self.txt_sources:
            try:
                response = requests.get(url=url, headers=self.header)
            except requests.exceptions.RequestException as e:
                print(f"Ошибка получения прокси из {url}: {e}")
                continue
            if response.ok:
                proxy_list = response.text.splitlines()
                proxy_list_filtered = re.findall(self.pattern, "\n".join(proxy_list))
                self.proxies_list.extend(proxy_list_filtered)

    def check_proxy(self, url, timeout=5):
        for count, proxy in enumerate(set(self.proxies_list), start=1):
            proxy_dict = {
                "http": proxy,
                "https": proxy,
            }

            try:
                response = requests.get(url=url, headers=self.header, proxies=proxy_dict, timeout=timeout)
                if response.ok:
                    self.validated_socks.append(proxy)
                    print(f"Прокси {proxy} валидный, статус: {response.status_code}")
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
                self.result_proxychecker.append(result)
            elapsed_time = time.time() - self.start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            print(
                f'Всего проверено {len(self.result_proxychecker)} из {len(self.validated_socks)}, прошло {hours} часов {minutes} минут {seconds} секунд')

        return self.result_proxychecker

    def save_results(self, result_proxychecker):
        today = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
        try:
            with open(f'result_proxychecker_{today}.json', 'w') as json_file:
                json.dump(result_proxychecker, json_file, indent=4)
            print(f"Результаты проверки записаны в файл result_proxychecker_{today}.json")
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")

    def run(self):
        self.get_data_from_geonode()
        self.get_data_from_socksus()
        self.get_data_from_txt()
        print(f'Найдено {len(set(self.proxies_list))} прокси')

        self.check_proxy('https://2ip.io/ru/privacy/')

        print(f'Валидировано через url {len(self.validated_socks)} прокси')

        result_proxychecker = self.check_proxy_with_checker()

        self.save_results(result_proxychecker)

        total_elapsed_time = time.time() - self.start_time
        total_hours = int(total_elapsed_time // 3600)
        total_minutes = int((total_elapsed_time % 3600) // 60)
        total_seconds = int(total_elapsed_time % 60)
        print(f"--- Всего затрачено {total_hours} часов {total_minutes} минут {total_seconds} секунд ---")


# Создание экземпляра класса и запуск процесса
proxy_validator = ProxyValidator()
proxy_validator.run()
