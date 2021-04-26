from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import argparse
import playsound
import imutils
import time
import dlib
import cv2
import time

#from database import updateDatebase

def eyesAreClosed(breakTime):
    if breakTime == True:
        print("Your Eyes Are Closed")

def wakeUpAlarm(path):
    playsound.playsound(path)

def eyeAspectRatio(eye):
    vertOne = dist.euclidean(eye[1], eye[5])
    vertTwo = dist.euclidean(eye[2], eye[4])
    horzDistance = dist.euclidean(eye[0], eye[3])
    
    eyeAspectRatio = (vertOne + vertTwo) / (2.0 * horzDistance)
    
    return eyeAspectRatio

def loadFaceParameters(args):
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])
    
    return detector, predictor

def startEyeDetection(totalTime):
    startTime = time.perf_counter()
    runEyeDetection(startTime, totalTime)

def runEyeDetection(startTime, totalTime):
    #-----------------------Variable Decleration-----------------------#
    EYE_AR_THRESHOLD = 0.3
    EYE_AR_CONSEC_FRAMES = 48
    COUNTER = 0
    BREAK_ON = False
    BLINK_NUMBER = 0
    BLINK_CONSEC_FRAMES = 5
    NAPPING_FRAMES = 50
    NAPPING_NUMBER = 0

    #-----------------------Parsing Arguments-----------------------#
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default="D:\shape_predictor.dat" , help="path to facial landmark predictor")
    
    ap.add_argument("-w", "--webcam", type=int, default=0, help="index of webcam on system")

    ap.add_argument("-b", "--break", type=bool, default=True, help="Do You want a Break Message?")

    ap.add_argument("-a", "--alarm", type=str, default="D:\sound.wav" , help="index of Alarm.Wave")

    args = vars(ap.parse_args())

    #-----------------------Initializing Face Detetor and Landmark Predictor-----------------------#
    detector, predictor = loadFaceParameters(args)

    #-----------------------DLib eye Indicies-----------------------#
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


    #-----------------------Loading the Rectangels-----------------------#
    print("[INFO] starting video stream thread...")
    vs = VideoStream(src=args["webcam"]).start()
    time.sleep(1.0)

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width = 450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:

            #-----------------------Eye Outlining-----------------------#
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftAspectRatio = eyeAspectRatio(leftEye)
            rightAspectRatio = eyeAspectRatio(rightEye)

            bothAspectRatio = (leftAspectRatio + rightAspectRatio) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            outlineColor = (0, 255, 0)
            cv2.drawContours(frame, [leftEyeHull], -1, outlineColor, 1)
            cv2.drawContours(frame, [rightEyeHull], -1, outlineColor, 1)

            #-----------------------Checking if Eyes are Closed-----------------------#    
            if bothAspectRatio < EYE_AR_THRESHOLD:
                COUNTER += 1

                if COUNTER >= EYE_AR_CONSEC_FRAMES:

                    if not BREAK_ON:
                        BREAK_ON = True

                        if args["break"] != "":
                            t = Thread(target=eyesAreClosed, args=(args["break"],))
                            t.deamon = True
                            t.start()

                    textColor = (0, 0, 255)

                    if COUNTER >= NAPPING_FRAMES:
                        cv2.putText(frame, "NAPPING!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)
                        if args["alarm"] != "":
                            t = Thread(target=wakeUpAlarm, args=(args["alarm"],))
                            t.daemon = True
                            t.start()
            else:
                if COUNTER >= BLINK_CONSEC_FRAMES:
                    BLINK_NUMBER += 1
                if COUNTER >= NAPPING_FRAMES:
                    NAPPING_NUMBER += 1

                COUNTER = 0
                BREAK_ON = False

            textColor = (0, 0, 255)
            cv2.putText(frame, "EyeAR: {:.2f}".format(bothAspectRatio), (300,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)
            cv2.putText(frame, "Blink: {}".format(BLINK_NUMBER), (300, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, textColor, 2)

        #Show Frame
        cv2.imshow("Frame", frame)

        #-----------------------Exiting Program-----------------------#
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if time.perf_counter() - startTime >= totalTime:
            break

    #-----------------------Closing Everthing Once Stopped-----------------------#
    cv2.destroyAllWindows()
    vs.stop()

    #updateDatebase(BLINK_NUMBER, NAPPING_NUMBER)
    #return -1