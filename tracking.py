import utils
from distances import *


def find_trackers(trackers, next_frame):
    # create the tracker from current position
    # using the flood fill technique
    def create_tracker(pos, current_tracker, distance):
        positions = utils.tracker_positions(next_frame, pos)
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking)
        n_tracker.distance = distance
        if not n_tracker .noise():
            new_trackers.append(n_tracker)
            return True
        return False

    new_trackers = []
    # Tira a terceira dimensão, deixando
    # apenas as intensidades no frame
    next_frame = utils.expose_trackers(next_frame)

    size = len(trackers)

    for index, tracker in enumerate(trackers):
        xy = tracker.middle()
        if next_frame[xy[1]][xy[0]] == 255:
            distance = 0
            if index+1 < size:
                distance = euclidean_dist(xy, trackers[index+1].middle())
            create_tracker(xy, tracker, distance)
        else:
            for xy in tracker.positions:
                if next_frame[xy[1]][xy[0]] == 255:
                    distance = 0
                    if index + 1 < size:
                        distance = euclidean_dist(xy, trackers[index + 1].middle())
                    create_tracker(xy, tracker, distance)
                    break

    sorted(new_trackers)
    return new_trackers


def nearest_point(trackers, next_frame):
    import numpy as np
    """
    :param trackers: the trackers list obtained from the previous frame
    :param next_frame: the next actual frame
    :return: a new tracker list containing the trackers from this frame
    """

    def create_tracker(current_tracker, start_position):
        square, positions = utils.get_square_positions(next_frame, start_position, 6)
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking, square)
        if not n_tracker.noise():
            new_trackers.append(n_tracker)

    exposed_frame = utils.expose_trackers(next_frame)

    trackers_positions = np.transpose(np.nonzero(exposed_frame))

    new_trackers = []
    for tracker in trackers:
        lowest_distance = 10000
        for position in trackers_positions:
            eq_tuple = (position[1], position[0])
            new_distance = euclidean_dist(tracker.middle(), eq_tuple)
            if new_distance < lowest_distance:
                lowest_distance = new_distance
                tracker_position = eq_tuple
        # now i know that here is the tracker same
        # that i'm looking for
        create_tracker(tracker, tracker_position)

    return new_trackers


# might assume that each tracker has its own pixels as a square
# else set the oldFrame parameter
def image_comparison(trackers, next_frame, default_size=6):
    """
    1- Para cada marcador fazer a comparação da soma de diferenças absolutas

    2- A partir do square(array quadrado em volta do ponto) atual de cada marcador
       checar o sad nas quatro mediações(acima, abaixo, na esquerda e na direita)

    3- O maior SAD deverá ser onde está a nova posição do marcador
    """
    # Create tracker
    def create_tracker(current_tracker, square, positions):
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking, square)
        if not n_tracker.noise():
            new_trackers.append(n_tracker)

    def recursive_search(sxy, current_tracker, size):
        square, positions = utils.get_square_positions(next_frame, sxy, size)
        if len(positions) > 0:
            return create_tracker(current_tracker, square, positions)
        if size < 30:
            recursive_search(sxy, current_tracker, size+1)

    def get_sad(position):
        square, positions = utils.get_square_positions(next_frame, position, default_size)
        sad = utils.sad(square, tracker.pixels)
        return sad, square, positions

    new_trackers = []

    for tracker in trackers:
        xy = tracker.middle()
        xy_top = (xy[0], xy[1] + 1)
        xy_bot = (xy[0], xy[1] - 1)
        xy_left = (xy[0] - 1, xy[1])
        xy_right = (xy[0] + 1, xy[1])

        middle, sq, pos = get_sad(xy)
        top, sq_top, top_positions = get_sad(xy_top)
        bot, sq_bot, bot_positions = get_sad(xy_bot)
        left, sq_left, left_positions = get_sad(xy_left)
        right, sq_right, right_positions = get_sad(xy_right)

        if middle < top and middle < bot and middle < left and middle < right:
            if len(pos) > 0:
                create_tracker(tracker, sq, pos)
            else:
                recursive_search(xy, tracker, default_size + 1)
        elif top < bot and top < left and top < right:
            if len(top_positions) > 0:
                create_tracker(tracker, sq_top, top_positions)
            else:
                recursive_search(xy_top, tracker, default_size+1)
        elif bot < left and bot < right:
            if len(bot_positions) > 0:
                create_tracker(tracker, sq_bot, bot_positions)
            else:
                recursive_search(xy_bot, tracker, default_size+1)
        elif left < right:
            if len(left_positions) > 0:
                create_tracker(tracker, sq_left, left_positions)
            else:
                recursive_search(xy_left,tracker, default_size+1)
        else:
            if len(right_positions) > 0:
                create_tracker(tracker, sq_right, right_positions)
            else:
                recursive_search(xy_right, tracker, default_size+1)

    sorted(new_trackers)
    return new_trackers


def model_based(vectors, next_frame):
    """
    Apontar um vetor de um ponto a outro, utilizar esse vetor para medir a distância esperada entre os marcadores

    Como eu tenho a medida de distância, e o vetor eu posso utilizar o vetor apontado do ponto que o marcador 0 está,
    para encontrar os demais marcadores, então eu só preciso utilizar algo simples pra encontrar o "marcador 0".

    A ideia pode ser encontrar a partir dos pontos do "marcador 0" o mesmo (como já era feito em outro metodo),
    e a partir do vetor do marcador 0 já grifado no frame anterior eu posso encontrar os outros
    :param vectors:
    :param next_frame:
    :return:
    """

    new_vectors = []

    exposed_frame = utils.expose_trackers(next_frame)

    for index, vector in enumerate(vectors):
        tracker1pos, tracker2pos = utils.find_trackers_vector(vector, exposed_frame)
        vector = utils.create_vector(tracker1pos, tracker2pos)
        if vector is not None:
            new_vectors.append(vector)

    return new_vectors
