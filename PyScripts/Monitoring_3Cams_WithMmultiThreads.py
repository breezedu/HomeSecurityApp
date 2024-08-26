#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2 as cv
import threading
import time
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk 
import os 
import json 


# In[2]:


# Load Haar Cascade for face detection
face_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')


# In[3]:



class CameraApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Camera Monitor")

        # Initialize variables
        self.capturing = False
        self.recording = False
        self.video_dir = "output"  # Default directory for saving videos
        self.preview_image = None
        
        # Create labels for the cameras
        
        ## Garage view: 
        self.cameraLabel = tk.Label(root,  fg="black", text="Garage View", font=('Times New Room',20))
        self.cameraLabel.grid(row=1, column=1, padx=10, pady=10, columnspan=2) 
        
        self.label_camera_1 = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
        self.label_camera_1.grid(row=2, column=1, padx=10, pady=10, columnspan=2)
        
        ## backyard view: 
        self.cameraLabel2 = tk.Label(root, fg="black", text="Backyard View", font=('Times New Room',20))
        self.cameraLabel2.grid(row=1, column=3, padx=10, pady=10, columnspan=2) 
        
        self.label_camera_2 = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
        self.label_camera_2.grid(row=2, column=3, padx=10, pady=10, columnspan=2) 
        
        
        ## Living room view: 
        self.cameraLabel3 = tk.Label(root, fg="black", text="LivingRoom View", font=('Times New Room',20))
        self.cameraLabel3.grid(row=5, column=1, padx=10, pady=10, columnspan=2) 
        
        self.label_camera_3 = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
        self.label_camera_3.grid(row=6, column=1, padx=10, pady=10, columnspan=2)
        
        # bottome right label: 
        # Create label for displaying preview with the detected face 
        self.previewlabel = Label(root, bg="LIGHTBLUE", fg="black", text="PreView", font=('Times New Room',20))
        self.previewlabel.grid(row=5, column=3, padx=10, pady=10, columnspan=2)

        self.label_preview = Label(root, bg="steelblue", borderwidth=3, relief="groove")
        self.label_preview.grid(row=6, column=3, padx=10, pady=10, columnspan=2)
        
        #self.label_preview = Label(root, bg="LIGHTBLUE", fg="black", text="PreView", font=('Times New Room',20))
        #self.label_preview.grid(row=5, column=3, padx=10, pady=10, columnspan=2)

        # Start camera threads
        self.camera_1_thread = threading.Thread(target=self.monitor_camera, args=( self.label_camera_1, root.cap1))
        self.camera_2_thread = threading.Thread(target=self.monitor_camera, args=( self.label_camera_2, root.cap2))
        self.camera_3_thread = threading.Thread(target=self.monitor_camera, args=( self.label_camera_3, root.cap3))

        self.camera_1_thread.start()
        self.camera_2_thread.start()
        self.camera_3_thread.start() 

    def monitor_camera(self, label, cap):
        # cap = cv.VideoCapture(camera_index)
        while True:
            ret, frame = cap.read()
            frame = cv.resize(frame, (500, 300))
            if not ret:
                break
            
            # Handle face detection
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                self.preview_image = frame  # Save the detected face region for preview
                self.display_preview(self.preview_image)

            # Check for recording
            if len(faces) > 0 and not self.recording:
                #self.start_recording(cap)
                print(" Person detected. ")

            # Convert frame for display
            img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)

        # cap.release()
        # root.after(10, lambda:monitor_camera(self, camera_index, label) )

    def start_recording(self, cap):
        self.recording = True

        # cap = cv.VideoCapture(camera_index)
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        out = cv.VideoWriter(f'video_camera{time.time()}.avi', fourcc, 20.0, (640, 480))
        
        start_time = time.time()
        while time.time() - start_time < 30:
            ret, frame = cap.read()
            if not ret:
                break
            
            out.write(frame)
            time.sleep(0.033)  # 30 FPS approx
            
        out.release()
        cap.release()
        self.recording = False

    def display_preview(self, face_image):
        if face_image is not None and face_image.size != 0:
            face_image = cv.cvtColor(face_image, cv.COLOR_BGR2RGB)
            img = Image.fromarray(face_image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_preview.imgtk = imgtk
            self.label_preview.configure(image=imgtk)


# In[4]:


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
        data = json.load(f)
    return data


# In[5]:


if __name__ == "__main__":
    root = tk.Tk()
    
    f_json = os.path.join( os.getcwd(), "camera_information.json")
    # Read in camera information from a jason file
    
    cameras = read_ip_camera_info(f_json)
    
    rtsp_url = ["" for x in range(3)]
    rtsp_url[0] = str( "rtsp://" + cameras[0]['Name'] + ":" + cameras[0]['Password'] 
                      + "@" + cameras[0]['ip'] + "/" + cameras[0]['stream'] )
    rtsp_url[1] = str( "rtsp://" + cameras[1]['Name'] + ":" + cameras[1]['Password'] 
                      + "@" + cameras[1]['ip'] + "/" + cameras[1]['stream'] )
    rtsp_url[2] = str( "rtsp://" + cameras[2]['Name'] + ":" + cameras[2]['Password'] 
                      + "@" + cameras[2]['ip'] + "/" + cameras[2]['stream'] )
    
    # Setting the title, window size, background color and disabling the resizing property
    root.title("HomeSecurity_Views")  
    root.geometry("1200x900")  
    root.resizable(True, True)  
    root.configure(background = "gray")
    
    # Capture frames from both cameras
    root.cap1 = cv.VideoCapture(rtsp_url[0])
    root.cap2 = cv.VideoCapture(rtsp_url[1])
    root.cap3 = cv.VideoCapture(rtsp_url[2])
    
    app = CameraApp(root)
    
    root.mainloop()
    
    

