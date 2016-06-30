import cv2
import utils
import tracking


def open_video():
    return cv2.VideoCapture('videos/VideoBike.avi')


def find_trackers_frame1(cap):
    ret, frame = cap.read()
    # Usando flood fill
    trackers = utils.find_trackers_1(frame, frames_square_size=15)
    frame = draw_trackers(trackers, frame)
    return trackers, frame


def draw_trackers(trackers, frame):
    size = len(trackers)
    for index, xy in enumerate(trackers):
        if xy.tracking:
            if index + 1 < size:
                frame = cv2.line(frame, xy.middle(), trackers[index+1].middle(), (255, 0, 0), 2)
            frame = cv2.circle(frame, xy.middle(), 10, xy.color(), 5)

    return frame


def draw_trackers_vectors(vectors, frame):
    for index, vector in enumerate(vectors):
        if vector.tracking:
            frame = cv2.line(frame, vector.start, vector.direction, (255, 0, 0), 2)
            frame = cv2.circle(frame, vector.start, 10, utils.color(index), 5)
            frame = cv2.circle(frame, vector.direction, 10, utils.color(index + 1), 5)
    return frame


def key_events(key, trackers):
    def disable_trackers(index):
        for value in trackers:
            value.stop_tracking()
        trackers[index].start_tracking()

    def enable_trackers():
        for value in trackers:
            value.start_tracking()

    # exit
    if key & 0xFF == ord('q'):
        return -1
    elif key & 0xFF == ord('1'):
        disable_trackers(0)
    elif key & 0xFF == ord('2'):
        disable_trackers(1)
    elif key & 0xFF == ord('3'):
        disable_trackers(2)
    elif key & 0xFF == ord('4'):
        disable_trackers(3)
    elif key & 0xFF == ord('5'):
        disable_trackers(4)
    elif key & 0xFF == ord('6'):
        disable_trackers(5)
    elif key & 0xFF == ord('7'):
        disable_trackers(6)
    elif key & 0xFF == ord('8'):
        disable_trackers(7)
    elif key & 0xFF == ord('9'):
        disable_trackers(8)
    elif key & 0xFF == ord('0'):
        enable_trackers()
    elif key & 0xFF == ord(' '):
        return 2
    elif key & 0xFF == ord('a'):
        return 3
    elif key & 0xFF == ord('d'):
        return 4

    return 1


def track(trackers, frame, alg=1):
    if alg == 1:
        if type(trackers[0]) is utils.Vector:
            trackers = utils.find_trackers_1(frame, frames_square_size=15)

        new_trackers = tracking.simple_nearest_point(trackers, frame)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame, new_trackers
    elif alg == 2:
        if type(trackers[0]) is utils.Vector:
            trackers = utils.find_trackers_1(frame, frames_square_size=15)

        new_trackers = tracking.image_comparison(trackers, frame)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame, new_trackers
    elif alg == 3:
        if type(trackers[0]) is utils.Vector:
            new_trackers_vectors = tracking.model_based(trackers, frame)
        else:
            new_trackers = tracking.simple_nearest_point(trackers, frame)
            new_trackers_vectors = utils.trackers_vectors(new_trackers)

        new_frame = draw_trackers_vectors(new_trackers_vectors, frame)
        return new_frame, new_trackers_vectors
    elif alg == 4:
        if type(trackers[0]) is utils.Vector:
            trackers = utils.find_trackers_1(frame, frames_square_size=15)

        new_trackers = tracking.euclidean_nearest_point(trackers, frame)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame, new_trackers


def frame_1(record=False):

    cap = open_video()
    trackers, frame1 = find_trackers_frame1(cap)

    if record:
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    while cap.isOpened():
        cv2.imshow('frame', frame1)
        key = cv2.waitKey(1)

        if record:
            out.write(frame1)

        if key_events(key, trackers) == -1:
            break

        elif key & 0xFF == ord('w'):
            ret, frame = cap.read()
            frame1, trackers = track(trackers, frame, alg=1)

        elif key & 0xFF == ord('e'):
            ret, frame = cap.read()
            frame1, trackers = track(trackers, frame, alg=2)

        elif key & 0xFF == ord('r'):
            ret, frame = cap.read()
            frame1, trackers = track(trackers, frame, alg=3)

        elif key & 0xFF == ord('b'):
            ret, frame = cap.read()
            frame1, trackers = track(trackers, frame, alg=4)

        elif key & 0xFF == ord('z'):
            ret, frame = cap.read()
            frame1 = utils.expose_trackers(frame)

    cap.release()
    cv2.destroyAllWindows()
    if record:
        out.release()


def main():
    cap = open_video()
    trackers, frame1 = find_trackers_frame1(cap)
    # cv2.imshow('frame', frame1)

    stop = False
    index = 0

    while cap.isOpened():
        # Keep reading the frames
        if not stop:
            ret, frame = cap.read()
            if ret:
                new_frame, trackers = track(trackers, frame, alg=2)
                cv2.imshow('frame', new_frame)
                index += 1
            else:
                break

        event = key_events(cv2.waitKey(1), trackers)

        if event == -1:
            break
        elif event == 2:
            stop = not stop
        elif event == 3:
            index -= 3 if index > 0 else 0
            cap.set(index, 0)

    cap.release()
    cv2.destroyAllWindows()

frame_1()
