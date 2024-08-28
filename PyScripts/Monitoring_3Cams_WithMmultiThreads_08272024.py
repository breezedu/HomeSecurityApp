#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2 as cv
import threading
import time
import tkinter as tk
from tkinter import * 
from tkinter import Label
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk 
import os 
import json 
from datetime import datetime 
from pathlib import Path


# In[2]:


# Load Haar Cascade for face detection or upper body detection: haarcascade_upperbody 
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml') 
body_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_upperbody.xml') 
video_dir = os.getcwd() 
# Lock to prevent simultaneous recording from both cameras
recording_lock = threading.Lock()


# In[ ]:





# In[3]:


def create_widget(self ):
    global camera1_label, camera2_label, camera3_label, label_preview

    # Create labels for the cameras
    # self.video_dir = StringVar()  # set directory for saving videos 
    
    ## Garage view: 
    cameraLabel = tk.Label(root,  fg="black", text="Garage View", font=('Times New Room',20))
    cameraLabel.grid(row=1, column=1, padx=10, pady=10, columnspan=2) 
        
    camera1_label = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    camera1_label.grid(row=2, column=1, padx=10, pady=10, columnspan=2)
        
    ## backyard view: 
    cameraLabel2 = tk.Label(root, fg="black", text="Backyard View", font=('Times New Room',20))
    cameraLabel2.grid(row=1, column=3, padx=10, pady=10, columnspan=2) 
       
    camera2_label = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    camera2_label.grid(row=2, column=3, padx=10, pady=10, columnspan=2) 
        
        
    ## Living room view: 
    cameraLabel3 = tk.Label(root, fg="black", text="LivingRoom View", font=('Times New Room',20))
    cameraLabel3.grid(row=5, column=1, padx=10, pady=10, columnspan=2) 
      
    camera3_label = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    camera3_label.grid(row=6, column=1, padx=10, pady=10, columnspan=2)
        
    # bottome right label: 
    # Create label for displaying preview with the detected face 
    previewlabel = Label(root, bg="LIGHTBLUE", fg="black", text="PreView", font=('Times New Room',20))
    previewlabel.grid(row=5, column=3, padx=10, pady=10, columnspan=2)

    label_preview = Label(root, bg="steelblue", borderwidth=3, relief="groove") 
    label_preview.grid(row=6, column=3, padx=10, pady=10, columnspan=2) 
        
    # save directory for captured videos or images
    saveLocationEntry = Entry(root, width=50)
    saveLocationEntry.grid(row=7, column=2, padx=10, pady=10) 
    saveLocationEntry.insert(0, video_dir)  # initiate with default dir

    browseButton = tk.Button(root, width=18, text="Choose Save Path", command=lambda:choose_directory(saveLocationEntry))
    browseButton.grid(row=7, column=1, padx=10, pady=10)


# In[4]:


def choose_directory(saveLocationEntry):
    global video_dir
    selected_dir = filedialog.askdirectory()
    if selected_dir:
        video_dir = selected_dir
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
        saveLocationEntry.delete(0, tk.END)
        saveLocationEntry.insert(0, video_dir)


# In[5]:


def saveDirBrowse(targetPath):
    # A pop-up window for target directory selection. 
    # by default, the initialdir would be os.getcwd() 
    # Retrieving the mouse selected destination directory
    targetDir = filedialog.askdirectory(initialdir="Choose Your target Dir for videos/images.")

    # Displaying the target directory in the txt dialog
    targetPath.set(targetDir) 


# In[ ]:





# In[6]:


def saveImage(camera_index, image, image_path):
    # Storing the date in the mentioned format in the image_name variable
    image_name = datetime.now().strftime('%d-%m-%Y %H-%M-%S') 
    
    #image_path = os.getcwd() or video_dir
    
    # Concatenating the image_path with image_name and with .jpg extension and saving it in imgName variable
    imgName = image_path + '/Camera_' + str(camera_index) + image_name + ".jpg"
    
    # Capturing the frame
    #ret, frame = cap.read() 
    #frame = root.cap.resize(frame, (640, 480))   # resize immediately; 

    # Displaying date and time on the frame
    cv.putText(image, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (430,460), cv.FONT_HERSHEY_DUPLEX, 0.5, (0,255,255))

    # Writing the image with the captured frame. Function returns a Boolean Value which is stored in success variable
    frame = cv.resize(image, (500, 280))
    success = cv.imwrite(imgName, image)

    # Displaying messagebox
    if success :
        #messagebox.showinfo("Image saved!", "The captured image has been saved to: " + imgName)
        print( "A new image with person detected has been saved!")


# In[ ]:





# In[7]:


# Function to detect faces and save video
def detect_and_save_video_old(cap, camera_index):
    

    print( " ----> Video path: " + str( video_dir))
    recording = False
    out = None
    start_time = None
    start_time_string = None

    while True:
        ret, frame = cap.read() 
        frame = cv.resize( frame, (500, 280))
        if not ret:
            break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0 and not recording: 
            # Start recording video on first detection
            start_time = time.time()
            start_time_string = time.strftime("%Y-%m-%d-%H-%M-%S") 
            video_name = os.path.join(video_dir, f"camera_{camera_index}_{str(start_time_string)}.avi")
            out = cv.VideoWriter(video_name, cv.VideoWriter_fourcc(*'XVID'), 20.0, (frame.shape[1], frame.shape[0]))
            recording = True

        if recording:
            out.write(frame) 
            print(" --- writing to " + str( video_name))

            # Draw rectangle around the detected faces
            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # Update preview
                img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                label_preview.config(image=imgtk)
                label_preview.imgtk = imgtk
                # save the detected person snapshot to target path
                saveImage(frame, video_dir)

            # Stop recording after 30 seconds
            if time.time() - start_time >= 30:
                print("Done recording for current camera with person detected.")
                out.release()
                out = None
                recording = False

        # Update video feed label
        img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        if camera_index == 0:
            camera1_label.config(image=imgtk)
            camera1_label.imgtk = imgtk
        elif camera_index ==1:
            camera2_label.config(image=imgtk)
            camera2_label.imgtk = imgtk
        else: 
            camera3_label.config(image=imgtk)
            camera3_label.imgtk = imgtk


# In[8]:


# Function to detect faces and save video
def detect_and_save_video(cap, camera_index):
    
    print( " ----> Video path: " + str( video_dir))
    recording = False
    out = None
    start_time = None
    start_time_string = None

    while True:
        ret, frame = cap.read()
        frame = cv.resize(frame, (500, 280))
        if not ret:
            break

        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0 and not recording and camera_index != 2:
            # Acquire lock to ensure only one camera records
            if recording_lock.acquire(blocking=False):
                try:
                    # Start recording video on first detection
                    start_time = time.time()
                    #video_name = os.path.join(video_dir, f"camera_{camera_index}_{int(start_time)}.avi")
                    start_time_string = time.strftime("%Y-%m-%d-%H-%M-%S") 
                    video_name = os.path.join(video_dir, f"camera_{camera_index}_{str(start_time_string)}.avi")
                    out = cv.VideoWriter(video_name, cv.VideoWriter_fourcc(*'XVID'), 20.0, (frame.shape[1], frame.shape[0]))
                    recording = True
                finally:
                    recording_lock.release()

        if recording:
            out.write(frame)

            # Draw rectangle around the detected faces
            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                # Update preview
                img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
                imgtk = ImageTk.PhotoImage(image=img)
                #preview_label.config(image=imgtk)
                #preview_label.imgtk = imgtk
                label_preview.config(image=imgtk)
                label_preview.imgtk = imgtk
                # save the detected person snapshot to target path
                saveImage(camera_index, frame, video_dir)

            # Stop recording after 30 seconds
            # print( "------ start time: " + str( start_time))
            if time.time() - start_time >= 30:
                out.release()
                out = None
                recording = False

        # Update video feed label
        img = Image.fromarray(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        if camera_index == 0:
            camera1_label.config(image=imgtk)
            camera1_label.imgtk = imgtk
        elif camera_index ==1:
            camera2_label.config(image=imgtk)
            camera2_label.imgtk = imgtk
        else: 
            camera3_label.config(image=imgtk)
            camera3_label.imgtk = imgtk


# In[9]:


def start_camera_stream(camera_index, rtsp_url):
    cap = cv.VideoCapture(rtsp_url[camera_index])
    detect_and_save_video(cap, camera_index)
    cap.release()


# In[10]:


def start_monitoring(rtsp_url):
    thread1 = threading.Thread(target=start_camera_stream, args=(0, rtsp_url))
    thread2 = threading.Thread(target=start_camera_stream, args=(1, rtsp_url))
    thread3 = threading.Thread(target=start_camera_stream, args=(2, rtsp_url))
    thread1.start()
    thread2.start()
    thread3.start() 
    


# In[ ]:





# In[11]:


def read_ip_camera_info(j_path):
    """Reads IP camera information from a JSON file.
    
    Args:
    file_path: The path to the JSON file.
    
    Returns:
    A list of dictionaries, where each dictionary contains the following keys:
      - username: The username for the IP camera.
      - password: The password for the IP camera.
      - ip: The IP address of the IP camera.
      - stream: The streaming port of the camera. 
      """

    with open(j_path, 'r') as f:
        cameras = json.load(f)
    
    rtsp_url  =  [""     for x in range(len(cameras))]        
    for x in range( len(cameras)):
        rtsp_url[x] = str( "rtsp://" + cameras[x]['Name'] + ":" + cameras[x]['Password'] 
                      + "@" + cameras[x]['ip'] + "/" + cameras[x]['stream'] ) 
        print( rtsp_url[x]) 
    
    return rtsp_url


# In[ ]:


if __name__ == "__main__": 
    
    # get camera information list from json file
    f_json = os.path.join( os.getcwd(), "camera_information.json")
    # Read in camera information from a jason file, return a list     
    rtsp_url = read_ip_camera_info(f_json)    
    

    root = tk.Tk()   
    #targetPath = StringVar() 
    
    # If the user has selected the destination directory, then get the directory and save it in image_path    
    video_dir = os.getcwd()
    #     if targetPath.get() != '':
    #         video_dir = targetPath.get()    
    
 
    # Setting the title, window size, background color and disabling the resizing property
    root.title("HomeSecurity_Views")  
    root.geometry("1200x900")  
    root.resizable(True, True)  
    root.configure(background = "gray")
    # Create widgets
    create_widget(root)
    start_monitoring(rtsp_url) 
    
    root.mainloop()
    
    #End :) 


# In[ ]:


# END     

