import time
from proxy_checking import ProxyChecker
import json

start_time = time.time()
socks5_proxies = []

# Чтение валидированных прокси из файла
with open('socks5_proxies.txt', 'r') as file:
    read_validated_socks = file.readlines()
    for proxy in read_validated_socks:
        socks5_proxies.append(proxy.strip())

# Инициализация ProxyChecker
checker = ProxyChecker()
result_proxychecker = []


# Проверка прокси через ProxyChecker и запись результатов
def check_proxy_with_checker():
    for proxy in socks5_proxies:
        result = checker.check_proxy(proxy)
        if result.get("status") == 1:
            result_proxychecker.append(result)
        # Вывод текущего времени выполнения и количество проверенных прокси #потом удалить
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        print(
            f'Всего проверено {len(result_proxychecker)} из {len(socks5_proxies)}, прошло {hours} часов {minutes} минут {seconds} секунд') #потом удалить


# Вызов функции для проверки прокси
check_proxy_with_checker()

# Запись результатов в JSON файл
with open('result_proxychecker.json', 'w') as json_file:
    json.dump(result_proxychecker, json_file, indent=4)  # indent=4 делает JSON более читабельным

print(f"Результаты проверки записаны в файл result_proxychecker.json") #потом удалить

# Общие затраты времени #потом удалить
total_elapsed_time = time.time() - start_time
total_hours = int(total_elapsed_time // 3600)
total_minutes = int((total_elapsed_time % 3600) // 60)
total_seconds = int(total_elapsed_time % 60)
print(f"--- Всего затрачено {total_hours} часов {total_minutes} минут {total_seconds} секунд ---")
