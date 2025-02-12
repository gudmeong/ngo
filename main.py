import os, sys, aiohttp, asyncio
from datetime import datetime
from colorama import Fore, Style

hitam = Fore.LIGHTBLACK_EX
kuning = Fore.LIGHTYELLOW_EX
merah = Fore.LIGHTRED_EX
biru = Fore.LIGHTBLUE_EX
hijau = Fore.LIGHTGREEN_EX
reset = Style.RESET_ALL
putih = Fore.LIGHTWHITE_EX

HOST = "".join([chr(_ - 5) for _ in [115, 116, 105, 106, 108, 116, 51, 102, 110]])


def log(msg):
    now = datetime.now().isoformat(" ").split(".")[0]
    print(f"{hitam}[{now}]{reset} {msg}{reset}")


async def ping(proxy=None, token=None):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "connection": "keep-alive",
        "content-type": "application/json",
        "host": HOST,
        "origin": "chrome-extension://jbmdcnidiaknboflpljihfnbonjgegah",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }
    ip_url = "https://api.bigdatacloud.net/data/client-ip"
    ping_url = f"https://{HOST}/api/user/nodes/ping"
    async with aiohttp.ClientSession(headers=headers, proxy=proxy) as session:
        res = await session.get(ip_url)
        jres = await res.json()
        ip = jres.get("ipString")
        log(f"{putih}ip client : {hijau}{ip}")
        while True:
            try:
                res = await session.post(url=ping_url, json={"type": "extension"})
                open("http.log", "a").write(await res.text() + "\n")
                if res.status != 201:
                    log(
                        f"{kuning}failed get respon ({putih}{ip}{kuning}), http status : {res.status}"
                    )
                    await countdowna(60)
                    continue
                jres = await res.json()
                message = jres.get("message")
                if "Node added successfully" in message:
                    log(f"{hijau}Successfully added nodes from {putih}{ip}")
                elif "Ping successful" in message:
                    log(f"{hijau}Sending pings from {putih}{ip}")
                await countdowna(60)
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                log(f"{kuning}error : {e}")


async def countdowna(t):
    for i in range(t, 0, -1):
        print(f"[-] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[\\] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[|] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[/] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[-] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[\\] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[|] waiting {i} seconds ", flush=True, end="\r")
        await asyncio.sleep(0.125)
        print(f"[/] waiting {i} seconds ", flush=True, end="\r")


async def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"""
{biru}┏┓┳┓┏┓  ┏┓    •      
{biru}┗┓┃┃┗┓  ┃┃┏┓┏┓┓┏┓┏╋  
{biru}┗┛┻┛┗┛  ┣┛┛ ┗┛┃┗ ┗┗  
{biru}              ┛      
{putih}> N O D E G O . A I 
{putih}> to perform PING !
{putih}> t.me/sdsproject
"""
    )
    proxies = open("proxies.txt").read().splitlines()
    token = open("token.txt").read()
    print(f"{hijau}total proxy : {putih}{len(proxies)}")
    if len(proxies) <= 0:
        proxies = [None]
    if len(token) <= 100:
        print(
            f"{kuning}Please fill in the token.txt file with the account access token.{reset}"
        )
        sys.exit()
    print()
    tasks = [asyncio.create_task(ping(proxy=proxy, token=token)) for proxy in proxies]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
