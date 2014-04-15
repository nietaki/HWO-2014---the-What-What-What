import json
import socket
import sys
from BaseBot import BaseBot

class NoobBot(BaseBot):
    def on_join(self, data):
        print("Joined")
        self.ping()

    def on_game_start(self, data):
        print("Race started")
        self.ping()

    def on_car_positions(self, data):
        #print("Car positions")
        self.throttle(0.5)

    def on_crash(self, data):
        print("Someone crashed")
        self.ping()

    def on_game_end(self, data):
        print("Race ended")
        self.ping()

    def on_error(self, data):
        print("Error: {0}".format(data))
        self.ping()

