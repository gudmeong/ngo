import os, sys, aiohttp, asyncio, json
from datetime import datetime, timezone
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


async def checkin(proxy=None, token=None):
    me_url = "https://nodego.ai/api/user/me"
    checkin_url = "https://nodego.ai/api/user/checkin"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "connection": "keep-alive",
        "content-type": "application/json",
        "host": HOST,
        "origin": "https://app.nodego.ai",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }
    async with aiohttp.ClientSession(headers=headers, proxy=proxy) as session:
        while True:
            try:
                res = await session.get(url=me_url)
                if res.status != 200:
                    log(f"{kuning}failed get account data !")
                    await countdowna(30)
                    continue
                text_res = await res.text()
                json_res = json.loads(text_res)
                metadata = json_res.get("metadata", {})
                last_checkin = metadata.get("lastCheckinAt", "not_found")
                if last_checkin == "not_found":
                    log(f"{kuning}failed get last checkin !")
                    continue
                if last_checkin is not None:
                    last_checkin = last_checkin.split("T")[0]
                now = datetime.now(tz=timezone.utc)
                today = now.isoformat().split("T")[0]
                if last_checkin != today:
                    res = await session.post(url=checkin_url)
                    text_res = await res.text()
                    if res.status != 201:
                        log(f"{kuning}failed check in today {putih}{today}")
                        continue
                    log(f"{hijau}success check in today {putih}{today}")
                    continue
                log(f"{kuning}already check in today {putih}{today}")
                await asyncio.sleep(86400)
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                log(f"{kuning}error : {e}")


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
    ip_url = "https://directory.cookieyes.com/api/v1/ip"
    ping_url = f"https://{HOST}/api/user/nodes/ping"
    async with aiohttp.ClientSession(
        headers={
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        },
        proxy=proxy,
    ) as session:
        while True:
            try:
                res = await session.get(ip_url)
                text_res = await res.text()
                jres = json.loads(text_res)
                ip = jres.get("ip")
                country = jres.get("country")
                log(f"{putih}ip client : {hijau}{ip} {putih}country : {hijau}{country}")
                break
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                log(f"{kuning}error : {e}")
    async with aiohttp.ClientSession(headers=headers, proxy=proxy) as session:
        while True:
            try:
                res = await session.post(url=ping_url, json={"type": "extension"})
                open("http.log", "a").write(await res.text() + "\n")
                if res.status != 201 and res.status != 200:
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
                    log(f"{hijau}Sending ping from {putih}{ip}")
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
    token = token.splitlines()[0]
    tasks = [asyncio.create_task(ping(proxy=proxy, token=token)) for proxy in proxies]
    tasks.append(asyncio.create_task(checkin(proxy=proxies[0], token=token)))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
