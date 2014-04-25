__author__ = 'nietaki'
import math

straight_line_radius = 100000000000


class TrackPiece(object):
    def __init__(self, json_piece, json_lanes):
        self.json_piece = json_piece  # the source json representation
        self.lanes = json_lanes
        self.is_straight = 'length' in json_piece

        # defaults
        self.bend_direction = 0
        self.angle = json_piece.get('angle', None)
        self.radius = json_piece.get('radius', straight_line_radius)

        self.switch = json_piece.get('switch', False)

        if self.is_straight:
            self.length = json_piece['length']
        else:
            # it's a bend!
            self.radius = json_piece['radius']
            self.bend_direction = math.copysign(1, self.angle)
            self.length = None  #shouldn't be used

    def true_radius(self, lane):
        if self.is_straight:
            return straight_line_radius

        distance_from_center = self.lanes[lane]['distanceFromCenter']

        true_radius = self.radius

        if self.bend_direction > 0:
            #right hand turn
            true_radius -= distance_from_center
        else:
            #left hand turn
            true_radius += distance_from_center
        return true_radius

    def true_piece_length(self, lane):
        if self.is_straight:
            return self.length
        proportion = abs(self.angle) / 360.0
        return proportion * 2 * math.pi * self.true_radius(lane)