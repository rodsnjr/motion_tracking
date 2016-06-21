import cv2
import utils
import tracking


def build_boy(trackers):
    arms = []
    body = []
    legs = trackers[11:]
    trackers = trackers[:11]

    for tracker in trackers:
        if tracker.middle() > (260, 110):
            arms.append(tracker)
        elif tracker.middle() < (220, 250):
            body.append(tracker)

    variable = {'legs': legs, 'body': body, 'arms': arms}
    return variable


def open_video():
    return cv2.VideoCapture('videos/VideoBike.avi')


def find_trackers_frame1(cap):
    ret, frame = cap.read()
    # Usando flood fill
    trackers = utils.find_trackers_1(frame, frames_square_size=6)
    frame = draw_trackers(trackers, frame)
    return trackers, frame


def draw_with_joint(items, frame):
    for index, tracker in enumerate(items):
        if tracker.tracking:
            if index > 0:
                cv2.line(frame, items[index - 1].middle(), tracker.middle(), (255, 0, 0), 5)
            frame = cv2.circle(frame, tracker.middle(), 5, tracker.color(), 10)


def draw_trackers(trackers, frame, joints=False):
    if len(trackers) > 10 and joints:
        body = build_boy(trackers)
        draw_with_joint(body['arms'], frame)
        draw_with_joint(body['body'], frame)
        draw_with_joint(body['legs'], frame)
    else:
        for xy in trackers:
            if xy.tracking:
                if xy.closest is not None:
                    cv2.line(frame, xy.middle(), xy.closest.middle(), (255, 0, 0), 5)
                    cv2.line(frame, xy.closest.middle(), xy.closest.closest.middle(), (255, 0, 0), 5)
                frame = cv2.circle(frame, xy.middle(), 10, xy.color(), 5)
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
        new_trackers = tracking.find_trackers(trackers, frame)
        tracking.nearest_trackers(new_trackers)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame, new_trackers
    elif alg == 2:
        new_trackers = tracking.image_comparsion(trackers, frame)
        new_frame = draw_trackers(new_trackers, frame)
        return new_frame, new_trackers


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
                new_frame, trackers = track(trackers, frame, alg=1)
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

main()
