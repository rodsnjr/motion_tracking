import cv2
import utils as utils


def open_video():
    return cv2.VideoCapture('videos/VideoBike.avi')


def find_trackers_frame1(cap):
    ret, frame = cap.read()
    # Usando flood fill
    trackers = utils.find_trackers_1(frame)
    frame = draw_trackers(trackers, frame)
    return trackers, frame


def nearest_points(trackers, next_frame):
    new_trackers = []
    # Tira a terceira dimensão, deixando apenas as intensidades no frame
    next_frame = next_frame[:, :, 1]
    next_frame[next_frame > 230] = 255
    for tracker in trackers:
        xy = tracker.middle()
        if next_frame[xy[1]][xy[0]] > 255:
            tracker_position = utils.tracker_positions(next_frame, xy)
            new_tracker = utils.Tracker(tracker_position, tracker.index)
            new_trackers.append(new_tracker)
        else:
            for xy in tracker.positions:
                if next_frame[xy[1]][xy[0]] == 255:
                    tracker_position = utils.tracker_positions(next_frame, xy)
                    new_tracker = utils.Tracker(tracker_position, tracker.index)
                    new_trackers.append(new_tracker)
                    break
    return new_trackers


def draw_trackers(trackers, frame):
    for index, xy in enumerate(trackers):
        if index > 0:
            cv2.line(frame, trackers[index - 1].middle(), xy.middle(), (255, 0, 0), 5)
        frame = cv2.circle(frame, xy.middle(), 10, xy.color(), 5)
    return frame


def main():
    cap = open_video()
    trackers, frame1 = find_trackers_frame1(cap)
    cv2.imshow('frame', frame1)

    while cap.isOpened():
        # Keep reading the frames
        ret, frame = cap.read()
        trackers = nearest_points(trackers, frame)
        new_frame = draw_trackers(trackers, frame)
        cv2.imshow('frame', new_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


main()