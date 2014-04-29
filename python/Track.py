__author__ = 'nietaki'

import math
import warnings
from TrackPiece import TrackPiece, straight_line_radius


class Track(object):
    def __init__(self, track):
        self.track = track
        self.track_id = self.track['id']
        self.track_pieces_deprecated = self.track['pieces']
        self.lanes = self.track['lanes']
        self.track_pieces = map(lambda pc: TrackPiece(pc, self.lanes), self.track_pieces_deprecated)
        self.track_piece_count = len(self.track_pieces_deprecated)

        self.index_of_the_beginning_of_the_longest_straight_piece = None  # yes, exactly. Because I can

        # piece id -> macro piece id
        self.macro_piece_map = dict()
        # macro_id -> first normal id
        self.reverse_macro_map = dict()
        self.compute_macro_pieces()
        self.compute_longest_straight()

    def compute_macro_pieces(self):
        self.macro_piece_map[0] = 0
        self.reverse_macro_map[0] = 0
        last_macro_index = 0
        for index in range(1, self.track_piece_count):
            if not self.track_pieces[index].same_as(self.track_pieces[index - 1]):
                last_macro_index += 1
                self.reverse_macro_map[last_macro_index] = index
            self.macro_piece_map[index] = last_macro_index

        # now we might need to join the last and the first macro pieces
        if self.track_pieces[self.reverse_macro_map[0]].same_as(self.track_pieces[self.reverse_macro_map[last_macro_index]]):
            print("first and last macro are the same")
            fixed_id = self.reverse_macro_map[last_macro_index]
            while fixed_id != 0:
                self.macro_piece_map[fixed_id] = 0
                fixed_id = (fixed_id + 1) % self.track_piece_count
            self.reverse_macro_map[0] = self.reverse_macro_map[last_macro_index]
            self.reverse_macro_map.pop(last_macro_index)

        print(self.macro_piece_map)

    def compute_longest_straight(self):
        origin_id = 0

        # I want to start with a bend
        while self.track_pieces[origin_id].is_straight:
            origin_id += 1

        cur_id = (origin_id + 1) % self.track_piece_count
        best_id = None
        best_length = 0.0

        current_starting_id = None
        current_length = 0.0
        while cur_id != origin_id:
            cur_piece = self.track_pieces[cur_id]
            if not cur_piece.is_straight:
                current_starting_id = None
                current_length = 0.0
            else:
                # it's a straight
                if current_starting_id is None:
                    current_starting_id = cur_id
                current_length += cur_piece.length

                if current_length > best_length:
                    best_length = current_length
                    best_id = current_starting_id

            cur_id = (cur_id + 1) % self.track_piece_count

        self.index_of_the_beginning_of_the_longest_straight_piece = best_id
        print("the longest straight begins on piece {0}!".format(best_id))
        return best_id





    def radius(self, piece_index):
        return self.track_pieces[piece_index].radius

    def next_index(self, input_track_piece_index):
        return (input_track_piece_index + 1) % self.track_piece_count

    def next_piece(self, input_track_piece_index):
        return self.track_pieces[self.next_index(input_track_piece_index)]

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

    def is_distance_less_than(self, piece_id_1, in_piece_distance_1, piece_id_2, in_piece_distance_2, lane, distance_limit):
        if piece_id_1 == piece_id_2:
            if in_piece_distance_1 <= in_piece_distance_2:
                return (in_piece_distance_2 - in_piece_distance_1) < distance_limit
            else:
                # first is ahead
                return False
        else:
            piece_id_1 != piece_id_2
            dist = self.track_pieces[piece_id_1].true_length(lane) - in_piece_distance_1
            cur_id = self.next_index(piece_id_1)
            while cur_id != piece_id_2:
                dist += self.track_pieces[cur_id].true_length(lane)
                if dist > distance_limit:
                    return False
                cur_id = self.next_index(cur_id)

            dist += in_piece_distance_2
            return dist < distance_limit

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
