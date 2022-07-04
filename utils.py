import requests
import os
from itertools import cycle

Proxies = [line.rstrip("\n") for line in open("data/proxies.txt", "r")]
ProxyPool = cycle(Proxies)

def GetProxy() -> str:
    Proxy = next(ProxyPool)
    if len(Proxy.split(":")) == 4:
        split = Proxy.split(":")
        Proxy = "{}:{}@{}:{}".format(
            split[2], split[3], split[0], split[1]
        )

    return "http://{}".format(Proxy)

def GenProxy():
    with open("data/proxies.txt", "wb") as file:
        response = requests.get(
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all"
        ).content
        file.write(response)
        file.close()
