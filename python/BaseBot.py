import json
import csv
from datetime import *
import os
import socket
import sys
from Track import Track
from CarState import CarState


class BaseBot(object):
    def __init__(self, sock, name, key):
        self.car_name = None
        self.car_color = None

        """a dictionary of car color -> CarState objects"""
        self.cars = dict()

        """the Track object"""
        self.track = None

        self.lines = []

        self.sock = sock
        self.name = name
        self.key = key
        date_string = datetime.now().strftime("%y%m%d_%H%M")
        self.csv_filename = "" + name + "_" + date_string + ".csv"


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

    """ this **always** has to respond to the server, with at least a ping *** """
    def on_car_positions(self, data):
        # On the test server, C.I and qualifying rounds, the bot must reply to the server on each game tick. The server
        # advances the game in ticks and waits for a reply from all bots at each tick. If your bot fails to respond
        # within a certain period the server will send you an error message and disqualify you. If there's nothing your
        # bot wants to "say", you can send a "ping" message described below. The server also processes only one message
        # / bot /tick, so there's no point sending more.
        self.ping()
        print("BaseBot says: Car positions")

    def on_crash_base(self, data):
        #FIXME this could be augmented with the game tick to make sure it is precise
        self.cars[data['color']].crash()
        self.on_crash(data)

    def on_crash(self, data):
        print("BaseBot says: Someone crashed")

    def on_spawn_base(self, data):
        self.cars[data['color']].spawn()
        self.on_spawn(data)

    def on_spawn(self, data):
        print("BaseBot says: Someone spawned")

    def on_dnf_base(self, data):
        self.on_dnf(data)

    def on_dnf(self, data):
        color = data['car']['color']
        name = data['car']['name']
        reason = data['reason']
        print("BaseBot says {0}, wearing {1} DNF: {2}".format(name, color, reason))

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
        """:rtype: CarState"""
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
            'spawn': self.on_spawn_base,
            'dnf': self.on_dnf_base,
            'gameEnd': self.on_game_end_base,
            'error': self.on_error_base,
        }
        socket_file = self.sock.makefile()
        line = socket_file.readline()
        while line:
            msg = json.loads(line)
            msg_type, data = msg['msgType'], msg['data']

            if msg_type == 'gameInit':
                track_name = data['race']['track']['id']

                #let me dump me some track, but just once
                filename = 'tracks/{0}.json'.format(track_name)
                if not os.path.exists(filename):
                    with open('tracks/' + track_name + '.json', 'w') as handle:
                        handle.write(line)

            if msg_type == 'carPositions':
                msg_map[msg_type](data, msg.get('gameTick', 0))
            elif msg_type in msg_map:
                msg_map[msg_type](data)
            else:
                print("Got unexpected {0}".format(msg_type))
                self.ping()
            line = socket_file.readline()