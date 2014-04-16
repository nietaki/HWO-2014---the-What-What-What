import math

__author__ = 'nietaki'

class Track(object):
    track = None
    race_session = None

    def __init__(self, track, race_session):
        self.track = track
        self.race_session = race_session
        self.track_id = self.track['id']
        self.track_pieces = self.track['pieces']
        self.lanes = self.track['lanes']

    def true_piece_length(self, piece_index, lane):
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
            return proportion * 2 * math.pi * true_radius

    def distance_diff(self, piece_index_1, in_piece_distance_1, piece_index_2, in_piece_distance_2, lane):
        if piece_index_1 == piece_index_2:
            return in_piece_distance_2 - in_piece_distance_1
        else:
            return self.true_piece_length(piece_index_1, lane) - in_piece_distance_1 + in_piece_distance_2