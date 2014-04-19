import json
import socket
import sys
from BaseBot import BaseBot

class NoobBot(BaseBot):
    def on_join(self, data, tick):
        print("Joined")
        self.ping()

    def on_game_start(self, data, tick):
        print("Race started")
        self.ping()

    def on_car_positions(self, data, tick):
        #print("Car positions")
        self.throttle(0.5)

    def on_crash(self, data, tick):
        print("Someone crashed")
        self.ping()

    def on_game_end(self, data, tick):
        print("Race ended")
        self.ping()

    def on_error(self, data, tick):
        print("Error: {0}".format(data))
        self.ping()

