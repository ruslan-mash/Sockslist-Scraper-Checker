# socks-scraper-checker
# import aiohttp
# import asyncio
import requests
import re
import time

start_time = time.time()

# Источники прокси socks 4,5 в формате txt из Интернета
txt_sources = (
    "https://spys.me/socks.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    # "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    # "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    # "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    # "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
)
# Паттерн для фильтрации по ip:port из источника
pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'
# Заголовок для маскировки под браузер
header = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

proxies_list = []  # список найденных прокси
validated_socks = []  # список валидированнных прокси


# Извлекаем все прокси из списка URL-адресов источников прокси

def get_all_proxies():
    for url in txt_sources:
        try:
            proxies = requests.get(url=url, headers=header)  # получаем текст из конкретного источника
            proxy_list = proxies.text.splitlines()  # разделяем ответ на строки
            proxy_list_filtered = re.findall(pattern, "\n".join(
                proxy_list))  # Объединяем строки списка в единую строку для применения паттерна поиска и применяем паттерн поиска

            proxies_list.extend(proxy_list_filtered)  # добавляем отфильтрованные данные в proxies_list

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching proxies from {url}: {e}")


# Вызов функции для получения прокси
get_all_proxies()
founded_proxy = tuple(set(proxies_list))  # удаляем дубликаты

# Принт промежуточная проверка результатов
print(f'Найдено {len(founded_proxy)} прокси')
print(f'Ранее удалено {len(proxies_list) - len(founded_proxy)} дубликатов')


# Проверка найденных прокси на работоспособность
def check_proxy():
    for proxy in founded_proxy:  # составляем словарик для проверки прокси и передачи в requests, если прокси с портом 1080 то это socks4, иначе socks5
        for proxy in founded_proxy:
            proxy_dict = {
                'http': f'socks5://{proxy}',  # Рассматриваем все прокси как socks5
                'https': f'socks5://{proxy}'
            }

        try:
            resp = requests.get(url='https://www.google.com', headers=header, proxies=proxy_dict, timeout=5)
            print(proxy_dict, resp.status_code)
            if resp.status_code == 200:
                validated_socks.append(proxy)
        except requests.exceptions.RequestException:
            pass

# Вызов функции для проверки прокси
check_proxy()

# Принт промежуточная проверка результатов
print(f'Валидировано {len(validated_socks)} прокси')

# Время выполнения операции
print("--- %s секунд затрачено на выполнение ---" % (time.time() - start_time))
