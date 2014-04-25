__author__ = 'nietaki'

import math
import warnings
from TrackPiece import TrackPiece, straight_line_radius


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


class Track(object):

    def __init__(self, track, race_session):
        self.track = track
        self.race_session = race_session
        self.track_id = self.track['id']
        self.track_pieces_deprecated = self.track['pieces']
        self.lanes = self.track['lanes']
        self.track_pieces = map(lambda pc: TrackPiece(pc, self.lanes), self.track_pieces_deprecated)
        self.track_piece_count = len(self.track_pieces_deprecated)

    @deprecated
    def radius(self, piece_index):
        return self.track_pieces[piece_index].radius

    @deprecated
    def piece_straight(self, piece_index):
        return self.track_pieces[piece_index].is_straight

    @deprecated
    def bend_direction(self, piece_index):
        return self.track_pieces[piece_index].bend_direction

    @deprecated
    def true_radius(self, piece_index, lane):
        return self.track_pieces[piece_index].true_radius(lane)

    @deprecated
    def true_piece_length(self, piece_index, lane):
        return self.track_pieces[piece_index].true_piece_length(lane)

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
