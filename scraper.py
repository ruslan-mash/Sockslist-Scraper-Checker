# socks-scraper-checker
# import aiohttp
# import asyncio
import requests
import re
import time

start_time = time.time()

# Источники
spys_source = "https://spys.me/socks.txt"
proxifly_sources = ("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt",
                    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt")
txt_sources = (
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
)
pattern = r'(\d+\.\d+\.\d+\.\d+:\d+)'
header = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
proxies_list = []
validated_socks = []


# Извлекаем все прокси из списка URL-адресов источников прокси
# Extract proxies from all source URLs
def get_all_proxies():
    for url in txt_sources:
        try:
            proxies = requests.get(url=url, headers=header)
            proxy_list = proxies.text.splitlines()  # Split the response into individual lines
            proxy_list_filtered = re.findall(pattern, "\n".join(proxy_list))  # Join lines into a single string and apply regex

            proxies_list.extend(proxy_list_filtered)  # Add filtered proxies to the proxies_list

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching proxies from {url}: {e}")

# Call the function to get proxies
get_all_proxies()
founded_proxy=tuple(set(proxies_list))

#Print all the proxies collected
print("\nAll collected proxies:")
for proxy in founded_proxy:
    print(proxy)
print(f'найдено {len(founded_proxy)} прокси')


#
#
#
#
#
#
#
# tch_proxies_from_url(session, url) for url in proxy_sources]
#         results = await asyncio.gather(*tasks)
#
#         # Свести список списков прокси в один список прокси
#         all_proxies = list(set([proxy for sublist in results for proxy in sublist]))
#         print(f"Количество полученных прокси: {len(all_proxies)}")
#         print(f"Удалено {len([proxy for sublist in results for proxy in sublist]) - len(all_proxies)} дупликатов")
#         return all_proxies
#
#
# # Проверка каждого прокси из полученного списка, чтобы убедиться, что он работает
# async def get_working_socks(session, proxy):
#     try:
#         async with session.get(f'http://{proxy}', timeout=5) as resp:
#             if resp.status == 200:
#                 print(f"Прокси {proxy} работает.")
#                 working_socks.append(proxy)
#             else:
#
#
#
# async def get_all_proxies():
#     async with aiohttp.ClientSession() as session:
#         tasks = [fe
#                 print(f"Прокси {proxy} не работает. Статус: {resp.status}")
#     except Exception as e:
#         print(f"Ошибка при проверке прокси {proxy} : {e}")
#
#
# # Основная функция для получения всех прокси и проверки их работы
# async def main():
#     async with aiohttp.ClientSession() as session:
#         proxies = await get_all_proxies()  # Получение всех прокси из источников
#         tasks = [get_working_socks(session, proxy) for proxy in proxies]  # Проверка работает ли каждый прокси
#         await asyncio.gather(*tasks)
#
#
# # Запускаем цикл событий asyncio
# if __name__ == "__main__":
#     asyncio.run(main())
#
#     # Количество рабочих прокси
#     print(f'Найдено {len(working_socks)} рабочих прокси')
#     print('\n'.join(working_socks))

# Время выполнения операции
print("--- %s секунд затрачено на выполнение ---" % (time.time() - start_time))
