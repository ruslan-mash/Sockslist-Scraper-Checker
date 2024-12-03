#socks-scraper
import aiohttp
import asyncio
import time

start_time = time.time()

proxy_sources = [
    # "https://www.proxy-list.download/api/v1/get?type=socks5",
    # "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    # "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt" #поправить лист,
    # "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt" #поправить лист,
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    # "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
    # "https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt",
    # "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    # "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt",
    "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt",
]

# # "https://www.proxy-list.download/api/v1/get?type=socks4" #0,
#   "https://www.proxy-list.download/api/v1/get?type=socks5" #1,
#   "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt" #1,
#   # "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt" #поправить лист,
#   # "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt" #поправить лист,
#   "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt" #12,
#   "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt" #10
#   "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt" #18,
#   # "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/socks5.txt" #0,
#   "https://sunny9577.github.io/proxy-scraper/generated/socks5_proxies.txt" #1,
#   "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt" #1,
#   "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks4.txt" #11,
#   "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Socks5.txt" #10,


working_socks = []


# Получить прокси с каждого URL в списке proxy_sources
async def fetch_proxies_from_url(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                proxies = await response.text()
                proxy_list = proxies.splitlines()  # Split the text by newlines to get individual proxies
                print(f"Получено {len(proxy_list)} прокси из {url}")
                return proxy_list
            else:
                print(f"Не получилось получить прокси из {url}. Статус: {response.status}")
                return []
    except Exception as e:
        print(f"Ошибка получения прокси из {url}: {e}")
        return []


# Проверка каждого прокси из полученного списка, чтобы убедиться, что он работает
async def get_working_socks(session, proxy):
    try:
        async with session.get(f'http://{proxy}', timeout=5) as resp:
            if resp.status == 200:
                print(f"Прокси {proxy} работает.")
                working_socks.append(proxy)
            else:
                print(f"Прокси {proxy} не работает. Статус: {resp.status}")
    except Exception as e:
        print(f"Ошибка при проверке прокси {proxy} : {e}")


# Извлекаем все прокси из списка URL-адресов источников прокси
async def get_all_proxies():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_proxies_from_url(session, url) for url in proxy_sources]
        results = await asyncio.gather(*tasks)

        # Свести список списков прокси в один список прокси
        all_proxies = [proxy for sublist in results for proxy in sublist]
        print(f"Количество полученных прокси: {len(all_proxies)}")
        return all_proxies


# Основная функция для получения всех прокси и проверки их работы
async def main():
    async with aiohttp.ClientSession() as session:
        proxies = await get_all_proxies()  # Get all proxies from sources
        tasks = [get_working_socks(session, proxy) for proxy in proxies]  # Check if each proxy works
        await asyncio.gather(*tasks)


# Запускаем цикл событий asyncio
if __name__ == "__main__":
    asyncio.run(main())

    # Количество рабочих прокси
    print(f'Найдено {len(working_socks)} рабочих прокси')
    print('\n'.join(working_socks))

    # Время выполнения операции
    print("--- %s секунд затрачено на поиск ---" % (time.time() - start_time))
