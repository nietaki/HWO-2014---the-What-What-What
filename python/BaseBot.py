import json
import socket
import sys


class BaseBot(object):

    def __init__(self, sock, name, key):
        self.sock = sock
        self.name = name
        self.key = key

        #TODO update these and other values as we get input messages
        self.cur_throttle = 0.0
        self.last_tick = 0
        self.total_distance = 0.0
        self.velocity = 0.0

        self.dist_delta = 0.0
        self.track = None

    def msg(self, msg_type, data):
        self.send(json.dumps({"msgType": msg_type, "data": data}))

    def send(self, msg):
        self.sock.send(msg + "\n")

    def join(self):
        return self.msg("join", {"name": self.name,
                                 "key": self.key})

    def throttle(self, throttle):
        cur_throttle = throttle
        self.msg("throttle", throttle)

    def ping(self):
        self.msg("ping", {})

    def run(self):
        self.join()
        self.msg_loop()

    def on_join_base(self, data):
        self.join(data)

    def on_join(self, data):
        print("BaseBot says: Joined")

    def on_game_start_base(self, data):
        self.on_game_start( data)

    def on_game_start(self, data):
        print("BaseBot says: Race started")

    def on_car_positions_base(self, data):
        self.on_car_positions(data)

    def on_car_positions(self, data):
        print("BaseBot says: Car positions")

    def on_crash_base(self, data):
        self.on_crash(data)

    def on_crash(self, data):
        print("BaseBot says: Someone crashed")

    def on_game_end_base(self, data):
        self.on_game_end(data)

    def on_game_end(self, data):
        print("BaseBot says: Race ended")

    def on_error_base(self, data):
        self.on_error(data)

    def on_error(self, data):
        print("BaseBot says: Error: {0}".format(data))

    def msg_loop(self):
        msg_map = {
            'join': self.on_join,
            'gameStart': self.on_game_start_base,
            'carPositions': self.on_car_positions_base,
            'crash': self.on_crash_base,
            'gameEnd': self.on_game_end_base,
            'error': self.on_error_base,
        }
        socket_file = self.sock.makefile()
        line = socket_file.readline()
        while line:
            msg = json.loads(line)
            msg_type, data = msg['msgType'], msg['data']
            if msg_type in msg_map:
                msg_map[msg_type](data)
            else:
                print("Got {0}".format(msg_type))
                self.ping()
            line = socket_file.readline()