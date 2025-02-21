import os, sys, aiohttp, asyncio, json, logging
from datetime import datetime, timezone
from pytz import utc, timezone as zones

HOST = "".join([chr(_ - 5) for _ in [115, 116, 105, 106, 108, 116, 51, 102, 110]])

TOKEN = os.getenv("TOKEN", "")
PROXY = os.getenv("PROXY", "")

logger = logging.getLogger(__name__)

def custom_time(*args):
    utc_time = datetime.utcnow()
    local_time = utc_time.replace(tzinfo=utc).astimezone(zones("Asia/Jakarta"))
    return local_time.timetuple()


def setup_logger():
    format_log = "[%(levelname)s] - [%(asctime)s - %(name)s - %(message)s] -> [%(module)s:%(lineno)d]"
    logging.basicConfig(format=format_log, level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")
    logging.Formatter.converter = custom_time


async def checkin(proxy=None, token=None):
    me_url = f"https://{HOST}/api/user/me"
    checkin_url = f"https://{HOST}/api/user/checkin"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {token}",
        "connection": "keep-alive",
        "content-type": "application/json",
        "host": HOST,
        "origin": f"https://app.{HOST}",
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
                    logger.warning("failed get account data!")
                    await countdowna(30)
                    continue
                text_res = await res.text()
                json_res = json.loads(text_res)
                metadata = json_res.get("metadata", {})
                last_checkin = metadata.get("lastCheckinAt", "not_found")
                if last_checkin == "not_found":
                    logger.warning("failed get last checkin! Return json:")
                    logger.info(json.dumps(json_res, indent=2))
                    continue
                if last_checkin is not None:
                    last_checkin = last_checkin.split("T")[0]
                now = datetime.now(tz=timezone.utc)
                today = now.isoformat().split("T")[0]
                if last_checkin != today:
                    res = await session.post(url=checkin_url)
                    text_res = await res.text()
                    if res.status != 201:
                        logger.error(f"failed check in today ( {today} )")
                        logger.info(json.dumps(json.loads(text_res), indent=2))
                        continue
                    logger.info(f"success check in today ( {today} )")
                    continue
                logger.info(f"already check in today ( {today} )")
                await asyncio.sleep(86400)
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                logger.error(f"ERROR: {e}")


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
                logger.info(f"ip client : {ip} country : {country}")
                break
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                logger.error(f"ERROR: {e}")
    async with aiohttp.ClientSession(headers=headers, proxy=proxy) as session:
        while True:
            try:
                res = await session.post(url=ping_url, json={"type": "extension"})
                open("http.log", "a").write(await res.text() + "\n")
                if res.status not in [201, 200]:
                    logger.warning(
                        f"failed get respon ( {ip} ), http status : {res.status}"
                    )
                    await countdowna(60)
                    continue
                jres = await res.json()
                message = jres.get("message")
                if "Node added successfully" in message:
                    logger.info(f"Successfully added nodes from ( {ip} )")
                elif "Ping successful" in message:
                    logger.info(f"Sending ping from ( {ip} )")
                await countdowna(60)
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                logger.info(f"ERROR: {e}")


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
    setup_logger()
    print(
        f"""
┏┓┳┓┏┓  ┏┓    •      
┗┓┃┃┗┓  ┃┃┏┓┏┓┓┏┓┏╋  
┗┛┻┛┗┛  ┣┛┛ ┗┛┃┗ ┗┗  
              ┛      
> N O D E G O . A I 
> to perform PING !
> t.me/sdsproject
"""
    )
    proxies = PROXY.splitlines()
    token = TOKEN
    if not TOKEN:
        logger.info("Token not exists! Exiting.....")
        sys.exit(1)
    logger.info(f"total proxy : {len(proxies)}")
    if len(proxies) <= 0:
        proxies = [None]
    if len(token) <= 100:
        logger.warning(
            f"Please fill in the token.txt file with the account access token"
        )
        sys.exit(1)
    
    token = token.splitlines()[0]
    tasks = [asyncio.create_task(ping(proxy=proxy, token=token)) for proxy in proxies]
    tasks.append(asyncio.create_task(checkin(proxy=proxies[0], token=token)))
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)
