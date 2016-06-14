import cv2
import utils
import tracking

def open_video():
    return cv2.VideoCapture('videos/VideoBike.avi')


def find_trackers_frame1(cap):
    ret, frame = cap.read()
    # Usando flood fill
    trackers = utils.find_trackers_1(frame)
    frame = draw_trackers(trackers, frame)
    return trackers, frame


def draw_trackers(trackers, frame):
    for index, xy in enumerate(trackers):
        if xy.tracking:
            if index > 0:
                cv2.line(frame, trackers[index - 1].middle(), xy.middle(), (255, 0, 0), 5)
            frame = cv2.circle(frame, xy.middle(), 10, xy.color(), 5)
    return frame


def key_events(key, frame, trackers):
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
        new_trackers = tracking.nearest_points(trackers, frame)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame


def main():
    cap = open_video()
    trackers, frame1 = find_trackers_frame1(cap)
    cv2.imshow('frame', frame1)

    stop = False
    index = 0

    while cap.isOpened():
        # Keep reading the frames
        if not stop:
            ret, frame = cap.read()
            if ret:
                new_frame = track(trackers, frame)
                cv2.imshow('frame', new_frame)
                index += 1

        event = key_events(cv2.waitKey(1), new_frame, trackers)

        if event == -1:
            break
        elif event == 2:
            stop = not stop
        elif event == 3:
            index -= 3 if index > 0 else 0
            cap.set(index, 0)

    cap.release()
    cv2.destroyAllWindows()


main()