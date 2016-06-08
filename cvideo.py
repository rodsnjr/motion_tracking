import cv2
import utils as utils

cap = cv2.VideoCapture('VideoBike.avi')



"""
ret, frame = cap.read()
white_spaces = find_trackers(frame)

for xy in white_spaces:
    frame = cv2.circle(frame, xy, 10, (255, 0, 255), 1)

cv2.imshow('frame', frame)

while cv2.waitKey(1) & 0xFF != ord('q'):
    cv2.imshow('frame', frame)

"""

while cap.isOpened():
    # Keep reading the frames
    ret, frame = cap.read()

    if ret:
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # segmentation, thresh = cv2.threshold(frame, 10, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        white_spaces = utils.find_trackers(frame)

        for xy in white_spaces:
           frame = cv2.circle(frame, xy, 10, (255, 0, 255), 1)

        cv2.imshow('frame', frame)
    else:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()