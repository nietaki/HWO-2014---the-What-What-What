import math

__author__ = 'nietaki'


class Track(object):

    def __init__(self, track, race_session):
        self.track = track
        self.race_session = race_session
        self.track_id = self.track['id']
        self.track_pieces = self.track['pieces']
        self.lanes = self.track['lanes']
        self.track_piece_count = len(self.track_pieces)

    def radius(self, piece_index):
        current_piece = self.track_pieces[piece_index]
        if 'length' in current_piece:
            #straight
            return float('inf')
        return current_piece['radius']

    def piece_straight(self, piece_index):
        return 'length' in self.track_pieces[piece_index]

    def bend_direction(self, piece_index):
        """
        :returns 0 for straight, -1 for left, +1 for right
        """
        current_piece = self.track_pieces[piece_index]
        if self.piece_straight(piece_index):
            return 0
        if current_piece['angle'] > 0:
            return 1
        else:
            return -1

    def true_radius(self, piece_index, lane):
        current_piece = self.track_pieces[piece_index]

        distance_from_center = self.lanes[lane]['distanceFromCenter']
        true_radius = self.radius(piece_index)
        if true_radius == float('inf'):
            return true_radius #FIXME this is ugly

        angle = current_piece['angle']
        if angle > 0:
            #right hand turn
            true_radius -= distance_from_center
        else:
            #left hand turn
            true_radius += distance_from_center
        return true_radius

    def true_piece_length(self, piece_index, lane):
        current_piece = self.track_pieces[piece_index]
        if 'length' in current_piece:
            #straight
            return current_piece['length']
        else:
            #bend
            angle = current_piece['angle']
            proportion = abs(angle) / 360.0
            return proportion * 2 * math.pi * self.true_radius(piece_index, lane)

    def distance_diff(self, piece_index_1, in_piece_distance_1, piece_index_2, in_piece_distance_2, lane):
        if piece_index_1 == piece_index_2:
            return in_piece_distance_2 - in_piece_distance_1
        else:
            return self.true_piece_length(piece_index_1, lane) - in_piece_distance_1 + in_piece_distance_2

    #starting_index doesn't get taken into account
    def next_bend_id(self, starting_index, less_than_radius=float('inf')):
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
