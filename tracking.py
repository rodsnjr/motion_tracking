import utils


def nearest_points(trackers, next_frame):
    # create the tracker from current position
    # using the flood fill technique
    def create_tracker(pos, current_tracker):
        positions = utils.tracker_positions(next_frame, pos)
        n_tracker = utils.Tracker(positions, current_tracker.index, current_tracker.tracking)
        if not n_tracker .noise():
            new_trackers.append(n_tracker)
            return True
        return False

    def square_search(xy, current_tracker):
        threshold = len(current_tracker.positions) // 2
        i = 1

        x = xy[0]
        y = xy[1]

        while i < threshold:
            if next_frame[y][x - i] == 255:
                return x - i, y
            if next_frame[y][x + i] == 255:
                return x + i, y
            elif next_frame[y - i][x + i] == 255:
                return x + i, y - i
            elif next_frame[y + i][x + i] == 255:
                return x + i, y + i
            elif next_frame[y - i][x - i] == 255:
                return x - i, y - i
            elif next_frame[y + i][x - i] == 255:
                return x - i, y + i
            elif next_frame[y + i][x] == 255:
                return x, y + i
            elif next_frame[y - i][x] == 255:
                return x, y - i
            i += 1

        return False

    new_trackers = []
    # Tira a terceira dimensão, deixando
    # apenas as intensidades no frame
    next_frame = utils.expose_trackers(next_frame)
    # Três estratégias, primeiramente busca a partir do meio
    # dos marcadores do frame antigo
    for tracker in trackers:
        xy = tracker.middle()
        if next_frame[xy[1]][xy[0]] == 255:
            create_tracker(xy, tracker)
        # Caso não encontrar procura todos os pontos do marcador antigo ...
        else:
            found = False
            for xy in tracker.positions:
                if next_frame[xy[1]][xy[0]] == 255:
                    if create_tracker(xy, tracker):
                        found = True
                        break
            # Caso não encontrar procurar os pontos próximos
            """if not found:
                threshold = len(tracker.positions) // 2
                xy = tracker.middle()
                # Procura nas quatro direções
                bot = square_search((xy[1] - threshold, xy[0]), tracker)
                if bot:
                    if create_tracker(bot, tracker):
                        break

                top = square_search((xy[1] + threshold, xy[0]), tracker)
                if top:
                    if create_tracker(top, tracker):
                        break

                left = square_search((xy[1], xy[0] - threshold), tracker)
                if left:
                    if create_tracker(left, tracker):
                        break

                right = square_search((xy[1], xy[0] + threshold), tracker)
                if right:
                    if create_tracker(right, tracker):
                        break
            """
    sorted(new_trackers)
    return new_trackers


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

        if len(positions) > 0 or size > 30:
            return create_tracker(current_tracker, square, positions)

        recursive_search(sxy, current_tracker, size+1)



    def get_sad(position):
        square, positions = utils.get_square_positions(next_frame, position, default_size)
        sad = utils.sad(tracker.pixels, square)
        return sad, square, positions

    new_trackers = []

    for tracker in trackers:
        xy = tracker.middle()
        xy_top = (xy[0], xy[1] + 4)
        xy_bot = (xy[0], xy[1] - 4)
        xy_left = (xy[0] - 4, xy[1])
        xy_right = (xy[0] + 4, xy[1])

        top, sq_top, top_positions = get_sad(xy_top)
        bot, sq_bot, bot_positions = get_sad(xy_bot)
        left, sq_left, left_positions = get_sad(xy_left)
        right, sq_right, right_positions = get_sad(xy_right)

        if top < bot and top < left and top < right:
            if len(top_positions) > 0:
                create_tracker(tracker, sq_top, top_positions)
            else:
                recursive_search(xy_top,tracker, default_size+1)
        elif bot < top and bot < left and bot < right:
            if len(bot_positions) > 0:
                create_tracker(tracker, sq_bot, bot_positions)
            else:
                recursive_search(xy_bot, tracker, default_size+1)
        elif left < top and left < bot and left < right:
            if len(left_positions) > 0:
                create_tracker(tracker, sq_left, left_positions)
            else:
                recursive_search(xy_left,tracker, default_size+1)
        elif right < top and right < bot and right < left:
            if len(right_positions) > 0:
                create_tracker(tracker, sq_right, right_positions)
            else:
                recursive_search(xy_right, tracker, default_size+1)

    sorted(new_trackers)
    return new_trackers
