#!/usr/bin/env python
#-----------------------------------------------------------------------
import numpy as np
import cv2
import imutils
import yaml
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from subprocess import call
fn_yaml = r"widemid.yml"
with open(fn_yaml, 'r') as stream:
    parking_data = yaml.load(stream)
def set_layout(frame_out):
    #print(parking_data)
    for ind, park in enumerate(parking_data):
        points = np.array([park['points']])
        cv2.drawContours(frame_out, [points], contourIdx=-1,
                         color=(0,0,255), thickness=2)            
        moments = cv2.moments(points)        
        centroid = (int(moments['m10']/moments['m00'])-3, int(moments['m01']/moments['m00'])+3)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        cv2.putText(frame_out, str(park['id']), (centroid[0]+1, centroid[1]-1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        cv2.putText(frame_out, str(park['id']), (centroid[0]-1, centroid[1]+1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
        cv2.putText(frame_out, str(park['id']), centroid, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
    return frame_out
def convert_mp4(vid_name):
    command = "MP4Box -add "+vid_name+":fps=24"+" "+vid_name[:len(vid_name)-5:]+".mp4"
    # Execute our command
    call([command], shell=True)
    command = "rm "+vid_name
    call([command], shell=True)
    # Video converted.
    print("Saved Video and converted.")
state = 1
count_file = 0
camera = PiCamera()
camera.resolution = (640, 360)
camera.framerate = 24
camera.hflip = True
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(640, 360))
fourcc = cv2.cv.CV_FOURCC(*'XVID')
# allow the camera to warmup
time.sleep(0.1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    image_setup = set_layout(image.copy())
    # show the frame
    cv2.imshow("Frame", image_setup)
    vid_name = "output"+str(count_file)+".h264"
    key = cv2.waitKey(1) & 0xFF
    if state == 2:
        if key == ord("v"):
            print("View Mode")
            camera.stop_recording()
            convert_mp4(vid_name)
            count_file = count_file+1
            state = 1
    if key == ord('w'):
        state = 2
        print("Write Mode")
        camera.start_recording(vid_name)
    if key == ord('q'):
        if state == 2:
            camera.stop_recording()
            convert_mp4(vid_name)
        break
    rawCapture.truncate(0)
