__author__ = 'nietaki'

class CarState(object):
    """stores all the state of a car (position, velocity and others), ours or theirs. Most of the info comes from the server
    messages, the throttle comes from the bot"""

    def __init__(self, track_object, game_init_car_fragment):
        """
        :type track_object: Track
        """
        self.name = game_init_car_fragment['id']['name']
        self.color = game_init_car_fragment['id']['color']
        self.dimensions = game_init_car_fragment['dimensions']
        self.track = track_object

        self.throttle = 0.0

        #basic stats
        self.tick = 0

        self.track_piece_index = 0
        self.in_piece_distance = 0.0
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

        self.angle_velocity = 0.0
        self.angle_acceleration= 0.0

        self.crashed = False

    def crash(self):
        self.crashed = True

    def spawn(self):
        self.crashed = False

    def set_throttle(self, throttle):
        self.throttle = throttle

    def relative_angle(self):
        """ relative meaning it always goes >0 on bends """
        return self.track.bend_direction(self.track_piece_index) * self.slip_angle

    def lane(self):
        return self.end_lane_index

    def is_switching(self):
        return self.start_lane_index != self.end_lane_index

    def current_track_piece(self):
        return self.track.track_pieces[self.track_piece_index]

    def on_car_position(self, car_data, new_tick, my_car):
        #FIXME this is a mess
        new_slip_angle = car_data['angle']
        new_angle_velocity = new_slip_angle - self.slip_angle

        self.angle_acceleration = new_angle_velocity - self.angle_velocity
        self.angle_velocity = new_angle_velocity

        self.slip_angle = new_slip_angle
        self.piece_position = car_data['piecePosition']
        self.tick = new_tick

        self.start_lane_index = self.piece_position['lane']['startLaneIndex']
        self.end_lane_index = self.piece_position['lane']['endLaneIndex']

        new_track_piece_index = self.piece_position['pieceIndex']
        new_in_piece_distance = self.piece_position['inPieceDistance']

        #FIXME this won't work correctly when switching on bends - the track lengths vary
        new_velocity = self.track.distance_diff(self.track_piece_index, self.in_piece_distance,
                                                       new_track_piece_index,
                                                       new_in_piece_distance, self.lane())
        self.acceleration = (new_velocity - self.velocity)

        if not self.velocity and new_velocity:


        self.velocity = new_velocity

        self.track_piece_index = new_track_piece_index
        self.in_piece_distance = new_in_piece_distance

        #print("tick: {0}, tick_delta: {1},distance_delta: {2}, velocity: {3}, acceleration: {4}".
        #      format(self.tick,
        #             self.tick_delta,
        #             self.distance_delta,
        #             self.velocity,
        #             self.acceleration))

