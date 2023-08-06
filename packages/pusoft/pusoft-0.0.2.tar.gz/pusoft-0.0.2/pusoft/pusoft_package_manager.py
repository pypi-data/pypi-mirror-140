import time,socket,urllib,urllib.request
from colorama import init, Fore, Back, Style

init()
init(autoreset=True)
socket.setdefaulttimeout(20)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
}

def cmd():
    print(Fore.MAGENTA + Back.CYAN + "*PUSOFT>>>欢迎使用 PUSOFT包管理器！")
    print(Fore.WHITE + Back.MAGENTA + "*霓>>>缔造起吾与这三千世界的连结吧！")
    try:
        url = "https://github.com/pumkin1001/pusoft"
        req = urllib.request.Request(url,headers=headers)
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8')
        response.close()
        print(Fore.MAGENTA + Back.CYAN + "*PUSOFT>>>连接至 GitHub 镜像仓库成功！")
        print(Fore.WHITE + Back.MAGENTA + "*霓>>>缔造起吾与这三千世界的连结吧！")
        name = input(Fore.WHITE + Back.MAGENTA + "*霓>>>来吧，迷惘的人啊，告诉我你需要的『Package』吧：")
    except:
        print(Fore.MAGENTA + Back.CYAN + "*PUSOFT>>>连接至 GitHub 镜像仓库失败！")
        print(Fore.WHITE + Back.MAGENTA + "*霓>>>唔，这世界也容不下本皇女吗？")

cmd()