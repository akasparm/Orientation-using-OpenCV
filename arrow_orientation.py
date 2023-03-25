import numpy as np
import matplotlib.pyplot as plt
import imutils as im
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2 as cv
from datetime import datetime, date, time


def arrow_masking(bgr_img):

    size = bgr_img.shape
    hsv_img = cv.cvtColor(bgr_img, cv.COLOR_BGR2HSV)

    hsv_lower = (77, 129, 172)
    hsv_upper = (94, 255, 255)
    masked_img = cv.inRange(hsv_img, hsv_lower, hsv_upper)

    # cv.imshow("Masked Image", masked_img)

    return masked_img

def blurring(contoured_img):
    
    kernel_size = (11, 11)
    blurred_image = cv.blur(contoured_img, kernel_size) 
    cv.imshow("Blurred Image", blurred_image)

    return blurred_image


def left_right(x_list, y_list):

    not_repeated_val = 0
    y_copy = y_list.copy()
    for i in range(len(y_list)):
        if y_list[i] not in y_copy:
            not_repeated_val = x_list[i]
            break

    if not not_repeated_val:
        not_repeated_val = x_list[-1]

    if (not_repeated_val == max(x_list)):
        return "right"
    else:
        return "left"


def up_down(x_list, y_list):

    not_repeated_val = 0
    x_copy = x_list.copy()
    for i in range(len(x_list)):
        if x_list[i] not in x_copy:
            not_repeated_val = y_list[i]
            break

    if not not_repeated_val:
        not_repeated_val = y_list[-1]

    if (not_repeated_val == max(y_list)):
        return "down"
    else:
        return "up"

def corner_detection_orientation(blurred_img, bgr_img):

    orientation = ""
    
    corners = cv.goodFeaturesToTrack(blurred_img, 7, 0.07, 10)
    if corners is not None:
        corners = np.int0(corners)

        x_list = []
        y_list = []
        for i in corners:
            x,y = i.ravel()
            cv.circle(bgr_img, (x,y), 3, (0, 255, 0), -1)
            x_list.append(x)
            y_list.append(y)

        x_span = max(x_list) - min(x_list)
        y_span = max(y_list) - min(y_list)

        if y_span>x_span:
            orientation = up_down(x_list, y_list)
        else:
            orientation = left_right(x_list, y_list)

    return bgr_img, orientation



def main():    
    
    # initialize the Raspberry Pi camera
    camera = PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 25
    rawCapture = PiRGBArray(camera, size=(640,480))

    #allow the camera to warmup
    time.sleep(0.1)

    # define the code and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    out = cv.VideoWriter('q3_attempt4.avi', fourcc, 10, (640, 480))

    
    i = 0
    # keep looping
    for frame in camera.capture_continuous(rawCapture,format="bgr",use_video_port=False):
        
        start = datetime.now()
        
        # grab the current frame
        bgr_img = frame.array
        masked_img = arrow_masking(bgr_img)
        blurred_img = blurring(masked_img)
        bgr_img, orientation = corner_detection_orientation(blurred_img, bgr_img)
    
        # show the frame to our screen
        cv.putText(bgr_img, orientation, (100,100), cv.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 3, cv.LINE_AA)
        cv.imshow("Frame",bgr_img)
        key=cv.waitKey(1) & 0xFF

        # write frame to video file	
        out.write(bgr_img)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        end = datetime.now()
        delta = end - start

        # open .txt file to save data 
        f = open('hw4data.txt','a') 
        
        # print time to run through loop to the screen & save to file  
        outstring = str(delta) + '\n' 
        f.write(outstring) 

        print("Loop iteration number: ", i, delta)

        # press the 'q' key to stop the video stream
        if key == ord("q"):
            break

    cv.destroyAllWindows()

if __name__=="__main__":
    main()