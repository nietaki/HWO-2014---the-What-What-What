import json
import csv
import pickle
import socket
import sys
from Track import Track
from CarState import CarState

class BaseBot(object):
    car_name = None
    car_color = None

    """a dictionary of car color -> CarState objects"""
    cars = dict()

    """the Track object"""
    track = None

    csv_filename = "test3.csv"

    lines = []

    def __init__(self, sock, name, key):
        self.sock = sock
        self.name = name
        self.key = key


    ## message handlers and senders ##
    def msg(self, msg_type, data):
        self.send(json.dumps({"msgType": msg_type, "data": data}))

    def send(self, msg):
        self.sock.send(msg + "\n")

    def join(self):
        return self.msg("join", {"name": self.name,
                                 "key": self.key})

    def throttle(self, throttle):

        self.cars[self.car_color].set_throttle(throttle)

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

    def on_your_car(self, data):
        self.car_color = data['color']
        self.car_name = data['name']

    def on_game_init_base(self, data):
        race = data['race']
        self.track = Track(race['track'], race['raceSession'])

        with open('debug_output/{0}_track.pickle'.format(self.track.track_id), 'wb') as handle:
            pickle.dump(race['track'], handle)

        for car in race['cars']:
            car_object = CarState(self.track, car)
            self.cars[car_object.color] = car_object
        self.on_game_init(data)

    def on_game_init(self, data):
        print("BaseBot says: Race inited")

    def on_game_start_base(self, data):
        self.on_game_start(data)

    def on_game_start(self, data):
        print("BaseBot says: Race started")

    def on_car_positions_base(self, data, new_tick):

        for car_data in data:
            color = car_data['id']['color']
            self.cars[color].on_car_position(car_data, new_tick)

        #FIXME this below is pretty ugly
        if self.csv_filename:
            self.lines.append(self.my_car().csv_row())

        self.on_car_positions(data)

    def on_car_positions(self, data):
        print("BaseBot says: Car positions")

    def on_crash_base(self, data):
        self.on_crash(data)

    def on_crash(self, data):
        print("BaseBot says: Someone crashed")

    def on_game_end_base(self, data):
        with open('debug_output/' + self.csv_filename, 'wb') as f:
            writer = csv.DictWriter(f, self.my_car().csv_keys())
            writer.writeheader()
            writer.writerows(self.lines)

        print("closing csv")

        self.on_game_end(data)

    def on_game_end(self, data):
        print("BaseBot says: Race ended")

    def on_error_base(self, data):
        self.on_error(data)

    def on_error(self, data):
        print("BaseBot says: Error: {0}".format(data))

    ## other helpers/accessors ##

    def my_car(self):
        return self.cars[self.car_color]

    ## and the LOOP ##
    def msg_loop(self):
        msg_map = {
            'join': self.on_join,
            'yourCar': self.on_your_car,
            'gameInit': self.on_game_init_base,
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
            if msg_type == 'carPositions':
                msg_map[msg_type](data, msg.get('gameTick', 0))
            elif msg_type in msg_map:
                msg_map[msg_type](data)
            else:
                print("Got unexpected {0}".format(msg_type))
                self.ping()
            line = socket_file.readline()