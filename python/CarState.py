__author__ = 'nietaki'

import csv


"""stores all the state of a car (position, velocity and others), ours or theirs. Most of the info comes from the server
messages, the throttle comes from the bot"""
class CarState(object):


    def __init__(self, track_object, game_init_car_fragment):
        self.name = game_init_car_fragment['id']['name']
        self.color = game_init_car_fragment['id']['color']
        self.dimensions = game_init_car_fragment['dimensions']
        self.track = track_object

        self.throttle = 0.0

        #basic stats
        self.tick = 0
        self.tick_delta = 1

        self.track_piece_index = 0
        self.in_piece_distance = 0.0
        self.distance_delta = 0.0
        self.start_lane_index = 0
        self.end_lane_index = 0

        self.velocity = 0.0

        """basically velocity delta"""
        self.acceleration = 0.0

        #from gameInit
        self.lanes = None
        self.car_dimensions = None
        self.race_session = None

        #from carPositions
        self.piece_position = None
        self.slip_angle = 0.0

    def set_throttle(self, throttle):
        self.throttle = throttle

    def lane(self):
        return self.end_lane_index

    def on_car_position(self, car_data, new_tick):
        self.slip_angle = car_data['angle']
        self.piece_position = car_data['piecePosition']
        self.tick_delta = new_tick - self.tick
        self.tick = new_tick

        self.start_lane_index = self.piece_position['lane']['startLaneIndex']
        self.end_lane_index = self.piece_position['lane']['endLaneIndex']

        new_track_piece_index = self.piece_position['pieceIndex']
        new_in_piece_distance = self.piece_position['inPieceDistance']
        #we don't want division by 0
        if self.tick_delta > 0:
            #FIXME this won't work correctly when switching on bends - the track lengths vary
            self.distance_delta = self.track.distance_diff(self.track_piece_index, self.in_piece_distance,
                                                           new_track_piece_index,
                                                           new_in_piece_distance, self.lane())
            new_velocity = self.distance_delta / self.tick_delta
            self.acceleration = (new_velocity - self.velocity) / self.tick_delta
            self.velocity = new_velocity

        self.track_piece_index = new_track_piece_index
        self.in_piece_distance = new_in_piece_distance

        #print("tick: {0}, tick_delta: {1},distance_delta: {2}, velocity: {3}, acceleration: {4}".
        #      format(self.tick,
        #             self.tick_delta,
        #             self.distance_delta,
        #             self.velocity,
        #             self.acceleration))

    def csv_row(self):
        row = dict()
        row["tick"] = self.tick
        row["car_id"] = self.name
        row["map_id"] = self.track.track_id
        row["throttle"] = self.throttle
        row["lane_start"] = self.start_lane_index
        row["lane_end"] = self.end_lane_index
        row["slip_angle"] = self.slip_angle
        row["piece_index"] = self.track_piece_index
        row["lane_radius"] = self.track.true_radius(self.track_piece_index, self.end_lane_index)
        row["in_piece_distance"] = self.in_piece_distance
        row["distance_delta"] = self.distance_delta
        row["velocity"] = self.velocity
        row["acceleration"] = self.acceleration
        row["is_crashed"] = "FIXME"
        return row

    def csv_keys(self):
        return ["tick",
                "car_id",
                "map_id",
                "throttle",
                "distance_delta",
                "velocity",
                "acceleration",
                "lane_radius",
                "slip_angle",
                "lane_start",
                "lane_end",
                "piece_index",
                "in_piece_distance",
                "is_crashed"]
