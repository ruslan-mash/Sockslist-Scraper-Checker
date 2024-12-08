# Получаем SOCKS5 прокси из интернет-списков, проверяем через запрос на url,
# записываем валидированные результаты ip:port в файл txt

import requests
import re
import time
from fake_useragent import UserAgent

start_time = time.time()

# Источники прокси socks5 в формате txt из Интернета
txt_sources = (
    "https://spys.me/socks.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
)
# Паттерн для фильтрации по ip:port из источника
pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'

# Заголовок для маскировки под браузер (генерация случайного User-Agent за каждый запрос)
ua=UserAgent()
header={'User-Agent': ua.random}

proxies_list = []  # список найденных прокси
validated_socks = []  # список валидированнных прокси


# Извлекаем все прокси из списка URL-адресов источников прокси

def get_all_proxies():
    for url in txt_sources:
        try:
            proxies = requests.get(url=url, headers=header)  # получаем список ip:port из источника
            proxy_list = proxies.text.splitlines()  # разделяем ответ на строки
            proxy_list_filtered = re.findall(pattern, "\n".join(
                proxy_list))  # Объединяем строки списка в единую строку для применения паттерна поиска и применяем паттерн поиска

            proxies_list.extend(proxy_list_filtered)  # добавляем отфильтрованные данные в proxies_list

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching proxies from {url}: {e}")


# Вызов функции для получения прокси
get_all_proxies()

founded_proxy = tuple(set(proxies_list))  # кортеж найденных прокси с удаленными дубликатами

# Принт промежуточная проверка результатов
print(f'Найдено {len(founded_proxy)} прокси')
print(f'Ранее удалено {len(proxies_list) - len(founded_proxy)} дубликатов')


# Проверка найденных прокси на работоспособность через url
def check_proxy(url, check_proxy_count=0):
    for proxy in founded_proxy:
        proxy_dict = {
            'http': f'socks5://{proxy}',  # Рассматриваем все прокси как socks5
            'https': f'socks5://{proxy}'
        }
        check_proxy_count += 1  # считалка потом удалить
        print(
            f' Проверяется {proxy_dict}, всего проверено {check_proxy_count} из {len(founded_proxy)}, прошло  {(time.time() - start_time) // 3600} часов {(time.time() - start_time) // 60} минут {(time.time() - start_time) % 60} секунд')  # потом удалить
        try:
            resp = requests.get(url=url, headers=header, proxies=proxy_dict, timeout=3.02)
            if resp.status_code == 200:
                validated_socks.append(proxy)
                print(f"Proxy {proxy} is valid, status code: {resp.status_code}")  # принт о прохождении потом удалить
        except requests.exceptions.RequestException as e:
            continue


# Вызов функции для проверки прокси через url
check_proxy('https://reqres.in/api/users/2')

# принты проверки выполнения
print(f'Валидировано {len(validated_socks)} прокси')  # потом удалить

# Запись валидированных прокси в файл
with open('socks5_proxies.txt', 'w') as file:
    for proxy in validated_socks:
        file.write(f"{proxy}\n")

print("Валидированные прокси записаны в файл socks5_proxies.txt")  # потом удалить

# Общие затраты времени #потом удалить
total_elapsed_time = time.time() - start_time
total_hours = int(total_elapsed_time // 3600)
total_minutes = int((total_elapsed_time % 3600) // 60)
total_seconds = int(total_elapsed_time % 60)
print(f"--- Всего затрачено {total_hours} часов {total_minutes} минут {total_seconds} секунд ---")
