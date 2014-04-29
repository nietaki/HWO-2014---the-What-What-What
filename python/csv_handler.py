__author__ = 'nietaki'
import physics

def csv_row(car):
    row = dict()
    row["tick"] = car.tick
    row["car_id"] = car.name
    row["map_id"] = car.track.track_id
    row["car_turbo_multiplier"] = physics.cur_turbo_multiplier
    row["throttle"] = car.throttle
    row["can_switch"] = int(car.track.track_pieces_deprecated[car.track_piece_index].get('switch', False))
    row["lane_start"] = car.start_lane_index
    row["lane_end"] = car.end_lane_index
    row["bend_direction"] = car.track.bend_direction(car.track_piece_index)
    row["relative_angle"] = car.relative_angle()
    row["slip_angle"] = car.slip_angle
    row["angle_velocity"] = car.angle_velocity
    row["angle_acceleration"] = car.angle_acceleration
    row["M"] = physics.M(car)
    row["piece_index"] = car.track_piece_index
    row["lane_radius"] = car.track.true_radius(car.track_piece_index, car.end_lane_index)
    row["in_piece_distance"] = car.in_piece_distance
    row["velocity"] = car.velocity
    row["acceleration"] = car.acceleration
    row["is_crashed"] = int(car.crashed)
    return row

def csv_keys(car):
    return ["tick",
            "car_id",
            "map_id",
            "car_turbo_multiplier",
            "throttle",
            "velocity",
            "acceleration",
            "lane_radius",
            "relative_angle",
            "slip_angle",
            "angle_velocity",
            "angle_acceleration",
            "M",
            "can_switch",
            "lane_start",
            "lane_end",
            "bend_direction",
            "piece_index",
            "in_piece_distance",
            "is_crashed"]