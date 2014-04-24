__author__ = 'nietaki'
import math


class TrackPiece(object):
    def __init__(self, json_piece, json_lanes):
        self.json_piece = json_piece  # the source json representation
        self.json_lanes = json_lanes
        self.is_straight = 'length' in json_piece

        # defaults
        self.bend_direction = 0
        self.angle = json_piece.get('angle', None)
        self.radius = json_piece.get('radius', 100000000000)

        self.switch = json_piece.get('switch', False)

        if self.is_straight:
            self.length = json_piece['length']
        else:
            # it's a bend!
            self.radius = json_piece['radius']
            self.bend_direction = math.copysign(1, self.angle)
            self.length =  None #shouldn't be used

