import json
import socket
import sys
from NoobBot import NoobBot
from investigation import *
from heuristics import *

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
        #bot = KeimolaAccelerator(s, name, key)
        #bot = GradualAccelerator(s, name, key)
        #bot = SwitchAndConstVelocity(s, name, key)
        #bot.run()

        #bot = ConstVelocity(s, name, key)
        #bot.target_velocity = 5.0
        #bot.velocity_increase = 0.25
        #bot.run("germany")
        #gen = (x * 0.1 for x in range(36, 45, 3))
        #for speed in gen:
        #    print(speed)
        #    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #    s.connect((host, int(port)))
        #    #bot = ConstThrottle(s, "" + name + str(throttle), key)
        #    #bot.const_throttle = throttle
        #    bot = SwitchAndConstVelocity(s, "" + name + str(speed), key)
        #    bot.target_velocity = speed
        #    bot.velocity_increase = 0.1
        #    bot.run("germany")

        #bot = PhysicsTester(s, name, key)
        #bot = PhysicsBisector(s, name, key)
        bot = Cruiser(s, name, key)
        #bot = AdvancedBisector(s, name, key)
        #bot = ConstVelocity(s, name, key)
        #bot.target_velocity = 5.9
        #bot.velocity_increase = 0.3
        ##bot.run("germany")
        #bot.run('keimola', 4)
        bot.run('france')

        #bot = ThresholdSpeedSearcher(s, name, key)
        #bot.cruising_speed = 2.5
        #bot.targeted_radius = 60
        #bot.already_switched = True
        #bot.run("germany")


