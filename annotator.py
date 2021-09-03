#!/usr/bin/env python3

import argparse
import cv2 as cv, cv2
import numpy as np
import os
import xml.etree.ElementTree as ET

def click_and_crop(event,x,y,flags,param):
    '''Handle Mouse click events: Left-button UP/DOWN, Hold Left-button and drag'''
    global refPt, cropping, sel_rect_endpoint, image

    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False
        cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 1)
        cv2.imshow('image', image)
    elif event == cv2.EVENT_MOUSEMOVE and cropping:
        sel_rect_endpoint = [(x, y)]

def get_xywh():
    '''Get x,y,w,h form selected frame'''
    global image
    clone = image.copy()
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', click_and_crop)

    # keep looping until the 'q' key is pressed
    while True:
        # display the image and wait for a keypress
        if not cropping:
            cv2.imshow('image', image)
        elif cropping and sel_rect_endpoint:
            rect_cpy = image.copy()
            cv2.rectangle(rect_cpy, refPt[0], sel_rect_endpoint[0], (0, 255, 255), 1)
            cv2.imshow('image', rect_cpy)

        key = cv2.waitKey(1) & 0xFF

        # if the 'r' key is pressed, reset the cropping region
        if key == ord('r'):
            image = clone.copy()
            sel_rect_endpoint.clear()
        # if the 'c' key is pressed, break from the loop
        elif key == ord('c'):
            break
        elif key == ord('q'):
            quit()
            break

    if len(refPt) == 2:
        x = min(refPt[0][0],refPt[1][0])
        y = min(refPt[0][1],refPt[1][1])
        w = abs(refPt[0][0]-refPt[1][0])
        h = abs(refPt[0][1]-refPt[1][1])

        roi = clone[y:y+h, x:x+w]
        cv2.imshow('region_of interest', roi)
        cv2.destroyAllWindows()
        cv2.waitKey(0)

        return x,y,w,h

def select_video_crop():
    '''Play the video and allow user to pause at a selected frame'''
    global image
    cap = cv.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        cv.imshow('frame', frame)

        if cv.waitKey(1) == ord('q'):
            break
        elif cv.waitKey(1) == ord('g'):#g for get
            image  = frame
            cv.destroyWindow('frame')
            x , y, w, h = get_xywh()
            break
    cap.release()
    return x,y,w,h

def video_crop(x,y,w,h):
    '''Crop the video and generate output files'''
    cap = cv.VideoCapture('') # Video path
    frame_counter = 0
    image_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        frame_counter += 1

        cropped_frame = frame[y:y+h, x:x+w]
        cv.imshow('frame', cropped_frame)
        if frame_counter >= 1: #and image_count<=number_of_samples:
            image_count += 1
            frame_counter = 0
            #For xml
            folder_name = save_to_path.split('/')
            folder_name = folder_name[len(folder_name)-1]
            mod_image_name = image_name+str(image_count)+'.png'
            image_path = save_to_path+'/'+mod_image_name
            xmax = x+w
            ymax = y+h
            #print('Generating Data[',image_count,'/',number_of_samples,']...')
            print('Generating Data[',image_count,']...')
            cv2.imwrite(os.path.join(save_to_path , mod_image_name), frame)# WRITE IMAGE
            #write_xml(folder_name, mod_image_name,image_path, width, height, channels, object_name, x, y, xmax, ymax)
            write_txt(mod_image_name)

            #if image_count>=number_of_samples:
             #   print("Task Completed!")
              #  break
        if cv.waitKey(1) == ord('q'):
            break

    cap.release()

def write_xml(folder_name, image_name,image_path, source_imageW, source_imageH, image_channels, object_name, xmin, ymin, xmax, ymax):
    '''create xml file and write data'''
    #global save_to_path
    tree = ET.parse('')# path for xml file
    root = tree.getroot()

    #Set folder_name
    root[0].text = folder_name

    #Set imagefile_name and path
    root[1].text = image_name
    root[2].text = image_path
    #Set source image width, Height and channels
    root[4][0].text = str(source_imageW)
    root[4][1].text = str(source_imageH)
    root[4][2].text = str(image_channels)

    #set object name
    root[6][0].text = object_name


    #set xmin,ymin, xmax,ymax
    root[6][4][0].text = str(xmin)
    root[6][4][1].text = str(ymin)
    root[6][4][2].text = str(xmax)
    root[6][4][3].text = str(ymax)

    output_filename = save_to_path+'/'+image_name[:-4]+'.xml'
    #print(output_filename)
    tree.write(output_filename)

def write_txt(image_name):
    '''Create txt file and write data'''
    ix, iy = (x+w/2)/width, (y+h/2)/height
    iw, ih = w/width, h/height
    txt_file_name = save_to_path+'/'+image_name[:-4]+'.txt'
    file = open(txt_file_name,"w+")

    file.write("%d %f %f %f %f"%(class_id, ix , iy, iw, ih))

#************** SET these values ******************#
video_path = '' #Set video path
save_to_path = '' # Do not include '/' at the end
object_name = '' #Set Object Name
image_name = ''#Do not use . extension, just enter image name the output will be numbered.
number_of_samples = 1000 #1 sample every 10 seconds for 30fps video
class_id = 2 #Set

#Do not modify the code below
refPt = []
cropping = False
sel_rect_endpoint = []
image = None

x , y, w, h = select_video_crop()
height, width, channels = image.shape

video_crop(x,y,w,h)
cv2.destroyAllWindows()
