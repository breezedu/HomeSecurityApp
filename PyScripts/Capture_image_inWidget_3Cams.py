#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[1]:


import cv2 as cv
import tkinter as tk
from tkinter import *
from PIL import Image,ImageTk
from datetime import datetime
from tkinter import messagebox, filedialog
import json 
import os


# In[ ]:





# In[ ]:





# In[2]:


######## 


# In[ ]:





# In[ ]:





# In[3]:


# Defining CreateWidgets() function to create necessary tkinter widgets
def createwidgets(root, destPath, imagePath, rtsp_url ): 
    # left panel 
    root.feedlabel = tk.Label(root,  fg="black", text="Garage View", font=('Times New Room',20))
    root.feedlabel.grid(row=1, column=1, padx=10, pady=10, columnspan=2)

    root.cameraLabel = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.cameraLabel.grid(row=2, column=1, padx=10, pady=10, columnspan=2)

    root.saveLocationEntry = Entry(root, width=55, textvariable=destPath)
    root.saveLocationEntry.grid(row=3, column=3, padx=10, pady=10)

    root.browseButton = tk.Button(root, width=18, text="Browse Save Path", command=lambda:destBrowse(destPath))
    root.browseButton.grid(row=3, column=2, padx=10, pady=10)

    root.captureBTN = tk.Button(root, text="Capture #1", command=lambda:Capture(root.cap1, destPath),  
                                font=('Times New Room',15), width=20)
    root.captureBTN.grid(row=4, column=1, padx=10, pady=10)

    root.CAMBTN = tk.Button(root, text="Stop Camera1", command=lambda:StopCAM(1, root, rtsp_url),  
                            font=('Times New Room',15), width=15)
    root.CAMBTN.grid(row=4, column=2)
    
    # right panel 
    root.feedlabel2 = tk.Label(root, fg="black", text="Backyard View", font=('Times New Room',20))
    root.feedlabel2.grid(row=1, column=3, padx=10, pady=10, columnspan=2)

    root.cameraLabel2 = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.cameraLabel2.grid(row=2, column=3, padx=10, pady=10, columnspan=2)

    root.captureBTN2 = Button(root, text="Capture #2", command=lambda:Capture(root.cap2, destPath),  
                             font=('Times New Room',15), width=20)
    root.captureBTN2.grid(row=4, column=3, padx=10, pady=10)

    root.CAMBTN2 = Button(root, text="Stop Camera2", command=lambda:StopCAM(2, root, rtsp_url),  
                          font=('Times New Room',15), width=15)
    root.CAMBTN2.grid(row=4, column=4) 
    
    # bottom left panel 
    root.feedlabel3 = tk.Label(root, fg="black", text="Indoor View", font=('Times New Room',20))
    root.feedlabel3.grid(row=5, column=1, padx=10, pady=10, columnspan=2)

    root.cameraLabel3 = tk.Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.cameraLabel3.grid(row=6, column=1, padx=10, pady=10, columnspan=2)

    root.captureBTN3 = Button(root, text="Capture #3", command=lambda:Capture(root.cap3, destPath),  
                             font=('Times New Room',15), width=20)
    root.captureBTN3.grid(row=8, column=1, padx=10, pady=10)

    root.CAMBTN3 = Button(root, text="Stop Camera3", command=lambda:StopCAM(3, root, rtsp_url),  
                          font=('Times New Room',15), width=15)
    root.CAMBTN3.grid(row=8, column=2)

    
    # bottom right panel 
    root.previewlabel = Label(root, bg="LIGHTBLUE", fg="black", text="PreView", font=('Times New Room',20))
    root.previewlabel.grid(row=5, column=3, padx=10, pady=10, columnspan=2)

    root.imageLabel = Label(root, bg="steelblue", borderwidth=3, relief="groove")
    root.imageLabel.grid(row=6, column=3, padx=10, pady=10, columnspan=2)

    #root.openImageEntry = Entry(root, width=55, textvariable=imagePath)
    #root.openImageEntry.grid(row=7, column=2, padx=10, pady=10)

    root.openImageButton = Button(root, width=20, text="Browse Source Path", command=lambda:imageBrowse(root))
    root.openImageButton.grid(row=5, column=4, padx=10, pady=10)

    # Calling ShowFrame() function
    ShowFrame( root ) 
    


# In[ ]:





# In[4]:


# Defining ShowFeed() function to display webcam feed in the cameraLabel;
def ShowFrame( root ):   

    #ret, frame = root.cap.read()    
    ret1, frame1 = root.cap1.read()
    ret2, frame2 = root.cap2.read() 
    ret3, frame3 = root.cap3.read()
    
    print( "Ret1: " + str( ret1) + " Ret2: " + str(ret2) + " Ret3: " + str( ret3))
    #print( "Ret2: " + str( ret2))

    if ret1: #or ret2:
        # Resize frames to fit labels
        frame1 = cv.resize(frame1, (500, 300))
        #frame2 = cv.resize(frame2, (640, 480))
        # Convert frames to RGB format
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
        #frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)
        
        # Convert frames to PIL Image objects
        img1 = Image.fromarray(frame1)
        #img2 = Image.fromarray(frame2)

        # Convert PIL Image objects to Tkinter PhotoImage objects
        imgtk1 = ImageTk.PhotoImage(image=img1)
        #imgtk2 = ImageTk.PhotoImage(image=img2)

        # Update labels with new images
        root.cameraLabel.configure(image=imgtk1)
        root.cameraLabel.imgtk = imgtk1
        
        #root.cameraLabel2.configure(image=imgtk2)
        #root.cameraLabel2.imgtk = imgtk2        
    else:
        # Configuring the label to display the frame
        root.cameraLabel.configure(image='') 
    if ret2:
        # Resize frames to fit labels
        #frame1 = cv.resize(frame1, (640, 480))
        frame2 = cv.resize(frame2, (500,300))
        # Convert frames to RGB format
        #frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
        frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)
        
        # Convert frames to PIL Image objects
        #img1 = Image.fromarray(frame1)
        img2 = Image.fromarray(frame2)

        # Convert PIL Image objects to Tkinter PhotoImage objects
        #imgtk1 = ImageTk.PhotoImage(image=img1)
        imgtk2 = ImageTk.PhotoImage(image=img2)

        # Update labels with new images
        #root.cameraLabel.configure(image=imgtk1)
        #root.cameraLabel.imgtk = imgtk1
        #
        root.cameraLabel2.configure(image=imgtk2)
        root.cameraLabel2.imgtk = imgtk2   
    else:
        # Configuring the label to display the frame
        root.cameraLabel2.configure(image='') 
        
    if ret3:
        # Resize frames to fit labels
        #frame1 = cv.resize(frame1, (640, 480))
        frame3 = cv.resize(frame3, (500,300))
        # Convert frames to RGB format
        #frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
        frame3 = cv.cvtColor(frame3, cv.COLOR_BGR2RGB)
        
        # Convert frames to PIL Image objects
        #img1 = Image.fromarray(frame1)
        img3 = Image.fromarray(frame3)

        # Convert PIL Image objects to Tkinter PhotoImage objects
        #imgtk1 = ImageTk.PhotoImage(image=img1)
        imgtk3 = ImageTk.PhotoImage(image=img3)

        # Update labels with new images
        root.cameraLabel3.configure(image=imgtk3)
        root.cameraLabel3.imgtk = imgtk3   
    else:
        # Configuring the label to display the frame
        root.cameraLabel3.configure(image='') 
        
    # Schedule the function to be called again after 10 milliseconds
    root.after(10, lambda:ShowFrame(root) )
    #else: 
        # Configuring the label to display the frame
    #    root.cameraLabel.configure(image='') 
        


# In[5]:


def destBrowse(destPath):
    # Presenting user with a pop-up for directory selection. initialdir argument is optional
    # Retrieving the user-input destination directory and storing it in destinationDirectory
    # Setting the initialdir argument is optional. SET IT TO YOUR DIRECTORY PATH
    destDirectory = filedialog.askdirectory(initialdir="YOUR DIRECTORY PATH")

    # Displaying the directory in the directory textbox
    destPath.set(destDirectory)


# In[6]:


def imageBrowse(root):
    # Presenting user with a pop-up for directory selection. initialdir argument is optional
    # Retrieving the user-input destination directory and storing it in destinationDirectory
    # Setting the initialdir argument is optional. SET IT TO YOUR DIRECTORY PATH
    openDirectory = filedialog.askopenfilename(initialdir="YOUR DIRECTORY PATH")

    # Displaying the directory in the directory textbox
    imagePath = StringVar() 
    imagePath.set(openDirectory)

    # Opening the saved image using the open() of Image class which takes the saved image as the argument
    imageView = Image.open(openDirectory)

    # Resizing the image using Image.resize()
    imageResize = imageView.resize((500, 300), Image.Resampling.LANCZOS)

    # Creating object of PhotoImage() class to display the frame
    imageDisplay = ImageTk.PhotoImage(imageResize)

    # Configuring the label to display the frame
    root.imageLabel.config(image=imageDisplay)

    # Keeping a reference
    root.imageLabel.photo = imageDisplay
 
    
    


# In[7]:


# Defining Capture() to capture and save the image and display the image in the imageLabel
def Capture(cap, destPath):
    # Storing the date in the mentioned format in the image_name variable
    image_name = datetime.now().strftime('%d-%m-%Y %H-%M-%S')

    # If the user has selected the destination directory, then get the directory and save it in image_path
    if destPath.get() != '':
        image_path = destPath.get()
    # If the user has not selected any destination directory, then set the image_path to default directory
    else:
        messagebox.showerror("ERROR", "NO DIRECTORY SELECTED TO STORE IMAGE!!")

    # Concatenating the image_path with image_name and with .jpg extension and saving it in imgName variable
    imgName = image_path + '/' + image_name + ".jpg"

    # Capturing the frame
    ret, frame = cap.read() 
    #frame = root.cap.resize(frame, (640, 480))   # resize immediately; 

    # Displaying date and time on the frame
    cv.putText(frame, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), (430,460), cv.FONT_HERSHEY_DUPLEX, 0.5, (0,255,255))

    # Writing the image with the captured frame. Function returns a Boolean Value which is stored in success variable
    frame = cv.resize(frame, (500, 300))
    success = cv.imwrite(imgName, frame)

    # Opening the saved image using the open() of Image class which takes the saved image as the argument
    saved_image = Image.open(imgName)

    # Creating object of PhotoImage() class to display the frame
    saved_image = ImageTk.PhotoImage(saved_image)

    # Configuring the label to display the frame
    root.imageLabel.config(image=saved_image)

    # Keeping a reference
    root.imageLabel.photo = saved_image

    # Displaying messagebox
    if success :
        messagebox.showinfo("Image saved!", "The captured image has been saved to: " + imgName)


# In[8]:


# Defining StopCAM() to stop WEBCAM Preview
def StopCAM(cam_num, root, rtsp_url):
    
    if cam_num == 2:        
        # Stopping the camera using release() method of cv.VideoCapture()
        root.cap2.release()    
        # Displaying text message in the camera label
        root.cameraLabel2.config(text="OFF CAM2", font=('Times New Room',70))
        # Configuring the CAMBTN to display accordingly
        root.CAMBTN2.config(text="Start Cam2", command=lambda:StartCAM( 2, root, rtsp_url ))    

    elif cam_num == 1:
        # Stopping the camera using release() method of cv.VideoCapture()
        root.cap1.release()    
        # Displaying text message in the camera label
        root.cameraLabel.config(text="OFF CAM1", font=('Times New Room',70))
        # Configuring the CAMBTN to display accordingly
        root.CAMBTN.config(text="Start Cam1", command=lambda:StartCAM( 1, root, rtsp_url ))    
        # Displaying text message in the camera label
        root.cameraLabel.config(image="", font=('Times New Room',70))   
    elif cam_num == 3:
        # Stopping the camera using release() method of cv.VideoCapture()
        root.cap3.release()    
        # Displaying text message in the camera label
        root.cameraLabel3.config(text="OFF CAM3", font=('Times New Room',70))
        # Configuring the CAMBTN to display accordingly
        root.CAMBTN3.config(text="Start Cam3", command=lambda:StartCAM( 3, root, rtsp_url ))    
        # Displaying text message in the camera label
        root.cameraLabel3.config(image="", font=('Times New Room',70))  


# In[9]:


def StartCAM(cam_num, root, rtsp_url):
    
    if cam_num == 2:
        # Creating object of class VideoCapture with webcam index
        root.cap2 = cv.VideoCapture(rtsp_url[1])
    
        # Setting width and height
        width_1, height_1 = 500, 300
        root.cap2.set(cv.CAP_PROP_FRAME_WIDTH, width_1)
        root.cap2.set(cv.CAP_PROP_FRAME_HEIGHT, height_1)

        # Configuring the CAMBTN2 to display accordingly
        root.CAMBTN2.config(text="Stop Camera2", command=lambda:StopCAM(2, root, rtsp_url))

        # Removing text message from the camera label
        root.cameraLabel2.config(text="")
        
    elif cam_num == 1:
        # Creating object of class VideoCapture with webcam index
        root.cap1 = cv.VideoCapture(rtsp_url[0])
        
        # Setting width and height
        width_1, height_1 = 500, 300
        root.cap1.set(cv.CAP_PROP_FRAME_WIDTH, width_1)
        root.cap1.set(cv.CAP_PROP_FRAME_HEIGHT, height_1)

        # Configuring the CAMBTN1 to display accordingly
        root.CAMBTN.config(text="Stop Camera1", command=lambda:StopCAM(1, root, rtsp_url))

        # Removing text message from the camera label
        root.cameraLabel.config(text="") 
    elif cam_num == 3:
        # Creating object of class VideoCapture with webcam index
        root.cap3 = cv.VideoCapture(rtsp_url[2])
        
        # Setting width and height
        width_1, height_1 = 500, 300
        root.cap3.set(cv.CAP_PROP_FRAME_WIDTH, width_1)
        root.cap3.set(cv.CAP_PROP_FRAME_HEIGHT, height_1)

        # Configuring the CAMBTN3 to display accordingly
        root.CAMBTN3.config(text="Stop Camera3", command=lambda:StopCAM(3, root, rtsp_url))

        # Removing text message from the camera label
        root.cameraLabel3.config(text="")

    # Calling the ShowFrame() Function
    ShowFrame(root) 


# In[10]:


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


# In[11]:


# Creating object of tk class
# root = tk.Tk()

# #curr_path = os.getcwd() 
# f_json = os.path.join( os.getcwd(), "Documents", "camera_information.json") 

# cameras = read_ip_camera_info(f_json)


# # Read in camera information from a jason file

# rtsp_url  = str( "rtsp://" + cameras[0]['Name'] + ":" + cameras[0]['Password'] + "@" + cameras[0]['ip'] + "/" + cameras[0]['stream'] )
# rtsp_url2 = str( "rtsp://" + cameras[1]['Name'] + ":" + cameras[1]['Password'] + "@" + cameras[1]['ip'] + "/" + cameras[1]['stream'] )
# rtsp_url3 = str( "rtsp://" + cameras[2]['Name'] + ":" + cameras[2]['Password'] + "@" + cameras[2]['ip'] + "/" + cameras[2]['stream'] )

# print( rtsp_url)
# print( rtsp_url3)

# # Setting the title, window size, background color and disabling the resizing property
# root.title("HomeSecurity_Views")  
# root.geometry("1200x900")  
# root.resizable(True, True)  
# root.configure(background = "gray") 

# # Creating tkinter variables 
# destPath = StringVar()  
# imagePath = StringVar() 

# # Capture frames from both cameras
# root.cap1 = cv.VideoCapture(rtsp_url)
# root.cap2 = cv.VideoCapture(rtsp_url2) 
# root.cap3 = cv.VideoCapture(rtsp_url3) # cheating camera using the laptop :) 

# createwidgets() 
# root.mainloop() 


# In[12]:


def main():
    # Creating object of tk class
    root = tk.Tk()

    #curr_path = os.getcwd() 
    f_json = os.path.join( os.getcwd(), "camera_information.json") 

    cameras = read_ip_camera_info(f_json)


    # Read in camera information from a jason file
    rtsp_url = ["" for x in range(3)]
    rtsp_url[0]  = str( "rtsp://" + cameras[0]['Name'] + ":" + cameras[0]['Password'] + "@" + cameras[0]['ip'] + "/" + cameras[0]['stream'] )
    rtsp_url[1]= str( "rtsp://" + cameras[1]['Name'] + ":" + cameras[1]['Password'] + "@" + cameras[1]['ip'] + "/" + cameras[1]['stream'] )
    rtsp_url[2] = str( "rtsp://" + cameras[2]['Name'] + ":" + cameras[2]['Password'] + "@" + cameras[2]['ip'] + "/" + cameras[2]['stream'] )

    print( rtsp_url)

    # Setting the title, window size, background color and disabling the resizing property
    root.title("HomeSecurity_Views")  
    root.geometry("1200x900")  
    root.resizable(True, True)  
    root.configure(background = "gray") 

    # Creating tkinter variables 
    destPath = StringVar()  
    imagePath = StringVar() 

    # Capture frames from both cameras
    root.cap1 = cv.VideoCapture(rtsp_url[0])
    root.cap2 = cv.VideoCapture(rtsp_url[1]) 
    root.cap3 = cv.VideoCapture(rtsp_url[2]) # cheating camera using the laptop :) 

    createwidgets(root, destPath, imagePath, rtsp_url )
    root.mainloop() 
    
    root.cap2.release()

    root.cap1.release() 

    root.cap3.release() 



# In[ ]:





# In[13]:



if __name__ == "__main__":
    main()



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




