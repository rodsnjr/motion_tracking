import utils


def find_trackers(trackers, next_frame):
    # create the tracker from current position
    # using the flood fill technique
    def create_tracker(pos, current_tracker):
        positions = utils.tracker_positions(next_frame, pos)
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking)
        if not n_tracker .noise():
            new_trackers.append(n_tracker)
            return True
        return False

    new_trackers = []
    # Tira a terceira dimensão, deixando
    # apenas as intensidades no frame
    next_frame = utils.expose_trackers(next_frame)

    for tracker in trackers:
        xy = tracker.middle()
        if next_frame[xy[1]][xy[0]] == 255:
            create_tracker(xy, tracker)
        else:
            for xy in tracker.positions:
                if next_frame[xy[1]][xy[0]] == 255:
                    create_tracker(xy, tracker)

    sorted(new_trackers)
    return new_trackers


def nearest_trackers(trackers):
    import distances

    for tracker in trackers:
        lowest_distance = 111919191
        closest_tracker = None

        for tracker1 in trackers:
            if tracker1 is not tracker:
                new_dist = distances.euclidean_dist(tracker.middle(), tracker1.middle())
                if new_dist < lowest_distance:
                    lowest_distance = new_dist
                    closest_tracker = tracker1

        tracker.closest = closest_tracker


# might assume that each tracker has its own pixels as a square
# else set the oldFrame parameter
def image_comparsion(trackers, next_frame, oldFrame=None, default_size=6):
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
        sad = utils.sad(tracker.pixels, square)
        return sad, square, positions

    new_trackers = []

    for tracker in trackers:
        xy = tracker.middle()
        xy_top = (xy[0], xy[1] + 2)
        xy_bot = (xy[0], xy[1] - 2)
        xy_left = (xy[0] - 2, xy[1])
        xy_right = (xy[0] + 2, xy[1])

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
                recursive_search(xy_top,tracker, default_size+1)
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
