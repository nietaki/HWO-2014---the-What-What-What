import json
import socket
import sys
from NoobBot import NoobBot
from investigation import *


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: ./run host port botname botkey")
    else:
        host, port, name, key = sys.argv[1:5]
        print("Connecting with parameters:")
        print("host={0}, port={1}, bot name={2}, key={3}".format(*sys.argv[1:5]))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        #bot = NoobBot(s, name, key)
        #bot = KeimolaBreaker(s, name, key)
        bot = KeimolaAccelerator(s, name, key)
        bot.run()
