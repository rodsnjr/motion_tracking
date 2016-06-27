import utils
from distances import *


def find_trackers(trackers, next_frame, square=0):
    # create the tracker from current position
    # using the flood fill technique
    def create_tracker(pos, current_tracker):
        positions = utils.tracker_positions(exposed_frame, pos)
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking)
        if not n_tracker .noise():
            if square > 0:
                pixels = utils.get_square(next_frame, n_tracker.middle(), square)
                n_tracker.pixels = pixels
            new_trackers.append(n_tracker)

    new_trackers = []
    # Tira a terceira dimensão, deixando
    # apenas as intensidades no frame
    exposed_frame = utils.expose_trackers(next_frame)

    for index, tracker in enumerate(trackers):
        xy = tracker.middle()
        if exposed_frame[xy[1]][xy[0]] == 255:
            create_tracker(xy, tracker)
        else:
            for xy in tracker.positions:
                if exposed_frame[xy[1]][xy[0]] == 255:
                    create_tracker(xy, tracker)
                    break

    sorted(new_trackers)
    return new_trackers


def nearest_point(trackers, next_frame):
    """
    :param trackers: the trackers list obtained from the previous frame
    :param next_frame: the next actual frame
    :return: a new tracker list containing the trackers from this frame
    """

    new_trackers = find_trackers(trackers, next_frame)

    for new_tracker in new_trackers:
        old_dist = 1000
        current_tracker = -1
        for tracker in trackers:
            distance = euclidean_dist(tracker.middle(), new_tracker.middle())
            if distance < old_dist:
                old_dist = distance
                current_tracker = tracker.index

        if current_tracker > -1:
            new_tracker.index = current_tracker

    return new_trackers


def image_comparison(trackers, next_frame, default_size=6):
    """
    1- Para cada novo marcador fazer a comparação da soma de diferenças absolutas
    2- O menor SAD deverá ser o mesmo marcador A
    """

    new_trackers = find_trackers(trackers, next_frame, default_size)

    for new_tracker in new_trackers:
        lowest_sad = 1000000000
        current_tracker = -1
        for old_tracker in trackers:
            sad_value = utils.sad(old_tracker.pixels, new_tracker.pixels)
            if sad_value < lowest_sad:
                current_tracker = old_tracker.index
                lowest_sad = sad_value

        if current_tracker > -1:
            new_tracker.index = current_tracker

    return new_trackers


def model_based(trackers, next_frame):
    """
    :param trackers:
    :param next_frame:
    :return:
    """

    vectors = utils.trackers_vectors(trackers)
    new_trackers = find_trackers(trackers, next_frame)
    new_vectors = utils.trackers_vectors(new_trackers)

    for vector in vectors:
        minor_dif = 1000
        closest_vector = None
        for new_vector in new_vectors:
            dif = abs(new_vector.size - vector.size)
            if dif < minor_dif:
                closest_vector = new_vector
                minor_dif = dif
        if closest_vector is not None:
            vector.start.index = closest_vector.start.index
            vector.direction.index = closest_vector.direction.index

    return new_trackers
