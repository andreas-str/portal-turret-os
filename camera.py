import time
import threading
import utils
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np

# Threading control
thread_video_running = False
thread_detection_running = False
# Camera controls
cameraDevice = None
latest_frame = None
# Tracking controls
motion_detection_active = False
motion_detected = False
target_tracking_active = False
target_tracked = False
target_locked = False
tracking_angle = 0

def video_thread():
    global cameraDevice
    global latest_frame
    global thread_video_running
    cameraDevice = PiCamera()
    cameraDevice.resolution = (480, 368)
    cameraDevice.framerate = 15
    cameraDevice.rotation = 180
    time.sleep(2)

    rawCapture = PiRGBArray(cameraDevice, size=(480, 368))
    stream = cameraDevice.capture_continuous(rawCapture, format="bgr", use_video_port=True)
    for f in stream:
        latest_frame = f.array
        rawCapture.truncate(0)
        if thread_video_running == False:
            stream.close()
            rawCapture.close()
            cameraDevice.close()
            return 

def detection_thread():
    global latest_frame
    global motion_detected
    global target_locked
    global tracking_angle
    old_frame = None
    tracking_location_buffer = [0, 0, 0]
    threshold = 20
    sensitivity = 80000
    tracking_accuracy = 15
    object_detector = cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=5, detectShadows = False)
    #object_detector = cv2.bgsegm.createBackgroundSubtractorMOG()
    while thread_video_running:
        old_frame = latest_frame
        time.sleep(0.07)
        if motion_detection_active:
            pixel_color = 1 # red=0 green=1 blue=2
            pixel_changes = (np.absolute(old_frame[...,pixel_color]-latest_frame[...,pixel_color])>threshold).sum()
            if pixel_changes > sensitivity:
                motion_detected = True
                print("Found Motion threshold=%s  sensitivity=%s changes=%s" % ( threshold, sensitivity, pixel_changes ))
                
        elif target_tracking_active:
            gray = cv2.cvtColor(latest_frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            thresh = object_detector.apply(gray)
            contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if len(contours)>0:
                cv2.drawContours(gray, contours, -1, (0,255,0), 5)
                # find the biggest countour (c) by the area
                c = max(contours, key = cv2.contourArea)
                x,y,w,h = cv2.boundingRect(c)
                #print("x " + str(x) + " y " + str(y) + " w " + str(w) + " h " + str(h))
                angle = utils.map(float(x+(float(w)/2.0)), 0, 480, 0, 200)
                # draw the biggest contour (c) in green
                cv2.rectangle(gray,(x,y),(x+w,y+h),(255,0,0),2)
                # Display the resulting frame

                tracking_location_buffer.append(angle)
                tracking_location_buffer.pop(0)
                print(str(tracking_location_buffer))
                if (max(tracking_location_buffer) - min(tracking_location_buffer)) < tracking_accuracy and target_locked == False:
                    cv2.imwrite("/home/turret/test_thres.jpg", thresh)
                    tracking_angle = int((tracking_location_buffer[0]+tracking_location_buffer[1]+tracking_location_buffer[2])/3)
                    target_locked = True
                    print(str(tracking_location_buffer) + str(int(tracking_angle)))
                    cv2.imwrite("/home/turret/test_cont.jpg", gray)

def start_video_thread():
    global thread_video_running
    global picam2
    if thread_video_running == True:
        return 1
    if thread_video_running == False:
        thread_video_running = True
        thread1 = threading.Thread(target=video_thread, daemon=True)
        thread1.start()
        print ("Video Thread Initialized...")
        return 0
    return 1

def start_detection_thread():
    global thread_detection_running
    if thread_detection_running == True:
        return 1
    if thread_detection_running == False:
        thread_detection_running = True
        thread2 = threading.Thread(target=detection_thread, daemon=True)
        thread2.start()
        print ("Detection Thread Initialized...")
        return 0
    return 1

def stop_video_thread():
    global thread_video_running
    if thread_video_running == True:
        thread_video_running = False
    return 0

def stop_detection_thread():
    global thread_detection_running
    if thread_detection_running == True:
        thread_detection_running = False
    return 0

def detecting_movement_controller(status):
    global motion_detection_active
    motion_detection_active = status

def detected_movement():
    global motion_detected
    if motion_detected == True:
        motion_detected = False
        return True
    return False

def tracking_controller(status):
    global target_tracking_active
    target_tracking_active = status
    
def tracking_finished():
    global target_locked
    if target_locked == True:
        target_locked = False

def tracking_status():
    # 1 = target found and locked
    #-1 = target not found
    if target_locked == True:
        return 1, tracking_angle
    else:
        return -1, 0