import json
import socket
import sys


class BaseBot(object):
    #TODO update these and other values as we get input messages
    cur_throttle = 0.0
    #basic stats
    tick = 0
    tick_delta = 1

    total_distance = 0.0
    distance_delta = 0.0

    speed = 0.0

    """basically speed delta"""
    acceleration = 0.0

    #from gameInit
    track_id = None
    track_pieces = None
    lanes = None
    car_dimensions = None
    race_session = None

    #from carPositions
    #TODO add other car positions later
    piece_position = None
    slip_angle = 0.0

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

    def on_game_init_base(self, data):
        race = data['race']
        track= race['track']
        self.track_id = track['id']
        self.track_pieces = track['pieces']
        self.lanes = track['lanes']
        self.car_dimensions = race['cars'][0]['dimensions']
        self.race_session = race['raceSession']
        self.on_game_init(data)

    def on_game_init(self, data):
        print("BaseBot says: Race inited")

    def on_game_start_base(self, data):
        self.on_game_start( data)

    def on_game_start(self, data):
        print("BaseBot says: Race started")

    def on_car_positions_base(self, data, new_tick):
        #TODO change this to work with multiple cars, preferably in a separate class, CarStats or sth
        self.slip_angle = data[0]['angle']
        self.piece_position = data[0]['piecePosition']

        self.tick_delta = new_tick - self.tick
        self.tick = new_tick

        #we don't want division by 0
        if self.tick_delta > 0:
            new_distance = self.distance(self.piece_position['lap'], self.piece_position['pieceIndex'],
                                         self.piece_position['inPieceDistance'])
            self.distance_delta = new_distance - self.total_distance
            self.total_distance = new_distance

            new_speed = self.distance_delta/self.tick_delta
            self.acceleration = (new_speed - self.speed)/self.tick_delta
            self.speed = new_speed

        print("tick: {0}, tick_delta: {1},distance_delta: {2}, speed: {3}, acceleration: {4}".format(self.tick,
                                                                                               self.tick_delta,
                                                                                               self.distance_delta,
                                                                                               self.speed,
                                                                                               self.acceleration))
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

    ## other helpers/accessors ##

    #"""returns an array of piece lengths"""
    #def piece_lengths(self):
    #    return map(lambda pc: pc['length'], self.track_pieces)

    #"""this should be a lazy val, but it's not scala and we're not going to be effective ;)"""
    #def total_track_length(self):
    #    return sum(self.piece_lengths())

    #def distance(self, lap_count, piece_index, piece_offset):
    #    return self.total_track_length() * lap_count + \
    #        sum(self.piece_lengths()[:piece_index]) + \
    #        piece_offset

    def truePieceLength(self, piece_index, lane):
        current_piece = self.track_pieces[piece_index]
        if 'length' in current_piece:
            #straight
            return current_piece['length']
        else:
            #bend
            angle = current_piece['angle']

            proportion = abs(angle) / 360.0
            distance_from_center = self.lanes[lane]['distanceFromCenter']
            true_radius = current_piece['radius']
            if(angle > 0):
                #right hand turn
                true_radius -= distance_from_center
            else:
                #left hand turn
                true_radius += distance_from_center
            return proportion * 2 * 3.14159 * true_radius


    ## and the LOOP ##
    def msg_loop(self):
        msg_map = {
            'join': self.on_join,
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