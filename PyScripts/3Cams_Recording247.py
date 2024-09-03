
import cv2 as cv
import os
import threading
import time
from datetime import datetime
import json 




# Configuration
CAMERA_INDEXES = [0, 1, 2]  # Adjust based on your camera setup
VIDEO_LENGTH_SECONDS = 30*60  # 900 for 15 minutes in seconds
BASE_TARGET_PATH = "/home/jeff/HomeSecurity_VideoRecording/videos/"  # Replace with your desired base target path
FRAME_RATE = 20  # Frames per second (adjust as needed)
VIDEO_RESOLUTION = (1280, 720)  # Adjust resolution based on your camera capability

def create_target_directory(base_path):
    """Create the target directory with a subdirectory for the current date."""
    # Get current date in YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    # Create the full path including the date subdirectory
    target_path = os.path.join(base_path, date_str)

    # Create the directory if it does not exist
    if not os.path.exists(target_path):
        os.makedirs(target_path)
        print(f"Created directory: {target_path}")
    else:
        print(f"Directory already exists: {target_path}")

    return target_path

def get_video_filename(camera_index):
    """Generate a filename based on camera index and current time."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"camera_{camera_index}_{timestamp}.avi"

def record_camera(rtsp_url, camera_index, base_path):
    """Record video from a single camera."""
    cap = cv.VideoCapture(rtsp_url[camera_index])
    cap.set(cv.CAP_PROP_FRAME_WIDTH, VIDEO_RESOLUTION[0])
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, VIDEO_RESOLUTION[1])
    cap.set(cv.CAP_PROP_FPS, FRAME_RATE)

    # Check if camera is opened correctly
    if not cap.isOpened():
        print(f"Error: Camera {camera_index} could not be opened.")
        return

    while True:
        # Get a new filename and path for each recording
        target_path = create_target_directory(base_path)
        video_filename = get_video_filename(camera_index)
        video_path = os.path.join(target_path, video_filename)
        #fourcc = cv.VideoWriter_fourcc(*'XVID')  # MPEG-4 codec
        out = cv.VideoWriter(video_path, cv.VideoWriter_fourcc(*'XVID'), FRAME_RATE, VIDEO_RESOLUTION)

        start_time = time.time()
        print(f"Recording started for camera {camera_index}: {video_filename}")

        frames_recorded = 0  # Counter to track if frames are being captured correctly
        while time.time() - start_time < VIDEO_LENGTH_SECONDS:
            ret, frame = cap.read()
            frame = cv.resize( frame, VIDEO_RESOLUTION)
            if not ret:
                print(f"Error: Camera {camera_index} frame could not be read.")
                break
            out.write(frame)
            frames_recorded += 1

        out.release()
        if frames_recorded == 0:
            print(f"Warning: No frames recorded for camera {camera_index}. Check camera connection.")
        else:
            print(f"Recording finished for camera {camera_index}: {video_filename}")
            print(" --- frames recorded: " + str( frames_recorded))

    cap.release()

def start_recording(rtsp_url):
    """Start recording for all configured cameras."""
    # Create a target directory with today's date as a subdirectory
    # target_path = create_target_directory(BASE_TARGET_PATH)
    threads = []
    for index in CAMERA_INDEXES:
        thread = threading.Thread(target=record_camera, args=(rtsp_url, index, BASE_TARGET_PATH))
        thread.start()
        threads.append(thread)

    # Join threads to keep the main thread alive
    for thread in threads:
        thread.join()

        

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
        
        
        

    
if __name__ == "__main__":
    # get camera information list from json file
    f_json = os.path.join( os.getcwd(), "camera_information.json")
    # Read in camera information from a jason file, return a list     
    rtsp_url = read_ip_camera_info(f_json) 
    
    # start multi threads camera recording task
    start_recording(rtsp_url)    

#END 