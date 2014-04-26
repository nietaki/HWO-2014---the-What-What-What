__author__ = 'nietaki'

import math
import warnings
from TrackPiece import TrackPiece, straight_line_radius


class Track(object):
    def __init__(self, track, race_session):
        self.track = track
        self.race_session = race_session
        self.track_id = self.track['id']
        self.track_pieces_deprecated = self.track['pieces']
        self.lanes = self.track['lanes']
        self.track_pieces = map(lambda pc: TrackPiece(pc, self.lanes), self.track_pieces_deprecated)
        self.track_piece_count = len(self.track_pieces_deprecated)
        # piece id -> macro piece id
        self.macro_piece_map = dict()
        # macro_id -> first normal id
        self.reverse_piece_map = dict()
        self.compute_macro_pieces()

    def compute_macro_pieces(self):
        self.macro_piece_map[0] = 0
        self.reverse_piece_map[0] = 0
        last_macro_index = 0
        for index in range(1, self.track_piece_count):
            if not self.track_pieces[index].same_as(self.track_pieces[index - 1]):
                last_macro_index += 1
                self.reverse_piece_map[last_macro_index] = index
            self.macro_piece_map[index] = last_macro_index
        print(self.macro_piece_map)

    def radius(self, piece_index):
        return self.track_pieces[piece_index].radius

    def piece_straight(self, piece_index):
        return self.track_pieces[piece_index].is_straight

    def bend_direction(self, piece_index):
        return self.track_pieces[piece_index].bend_direction

    def true_radius(self, piece_index, lane):
        return self.track_pieces[piece_index].true_radius(lane)

    def true_piece_length(self, piece_index, lane):
        return self.track_pieces[piece_index].true_length(lane)

    def distance_diff(self, piece_index_1, in_piece_distance_1, piece_index_2, in_piece_distance_2, lane):
        if piece_index_1 == piece_index_2:
            return in_piece_distance_2 - in_piece_distance_1
        else:
            return self.true_piece_length(piece_index_1, lane) - in_piece_distance_1 + in_piece_distance_2

    #starting_index doesn't get taken into account
    def next_bend_id(self, starting_index, less_than_radius=straight_line_radius):
        starting_index %= self.track_piece_count
        index = (starting_index + 1) % self.track_piece_count
        while True:
            radius = self.radius(index)

            if radius < less_than_radius:
                return index

            if index == starting_index:
                return None
            index = (index + 1) % self.track_piece_count

    def distance_until_index(self, starting_index, in_piece_position, target_index, lane=0):
        if target_index is None:
            return None

        starting_index %= self.track_piece_count
        target_index %= self.track_piece_count

        if starting_index == target_index:
            return 0.0

        dist = self.true_piece_length(starting_index, lane) - in_piece_position

        index = (starting_index + 1) % self.track_piece_count
        while index != target_index:
            dist += self.true_piece_length(index, lane)
            index = (index + 1) % self.track_piece_count
        return dist
