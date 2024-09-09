import cv2
import time
import os
from datetime import datetime
import threading
import json 

# Configuration: IP camera URLs
# CAMERA_URLS = [
#     "rtsp://username:password@ip_address:port/stream1",  # Replace with your actual IP camera URL
#     "rtsp://username:password@ip_address:port/stream2",
#     "rtsp://username:password@ip_address:port/stream3",
# ]

# Set the duration for each video segment in seconds (e.g., 30 minutes = 1800 seconds)
VIDEO_DURATION = 30 * 60

# Directory where videos will be saved
TARGET_DIRECTORY = "./recorded_videos"

def create_target_directory(base_directory):
    """
    Creates a daily subdirectory within the target directory for organizing recordings.
    """
    date_dir = datetime.now().strftime('%Y-%m-%d')
    full_path = os.path.join(base_directory, date_dir)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def get_video_filename(camera_index):
    """
    Generates a filename based on the current timestamp and camera index.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"camera_{camera_index}_{timestamp}.mp4"

def record_camera(camera_url, camera_index):
    """
    Records the video stream from a given IP camera URL with GPU-accelerated frame capture.
    """
    while True:
        try:
            cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                print(f"Error: Could not open camera {camera_index}")
                time.sleep(5)  # Retry after a delay
                continue

            # Get video properties
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15  # Default to 15 if fps not available

            # Calculate end time for the current recording
            end_time = time.time() + VIDEO_DURATION

            # Create a new video file
            video_path = create_target_directory(TARGET_DIRECTORY)
            filename = get_video_filename(camera_index)
            filepath = os.path.join(video_path, filename)

            # VideoWriter object to save the video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))

            print(f"Recording {filepath} from camera {camera_index}")

            # CUDA-enabled GPU Mat (used only if CUDA is available)
            use_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0

            while time.time() < end_time:
                ret, frame = cap.read()
                if not ret:
                    print(f"Error: Failed to read frame from camera {camera_index}")
                    break

                # Transfer frame to GPU if CUDA is enabled
                if use_cuda:
                    gpu_frame = cv2.cuda_GpuMat()
                    gpu_frame.upload(frame)
                    frame = gpu_frame.download()  # Only needed if further GPU processing is required

                out.write(frame)

            # Release resources
            cap.release()
            out.release()
            print(f"Finished recording {filepath} from camera {camera_index}")

        except Exception as e:
            print(f"Exception in camera {camera_index}: {e}")
            # Continue loop to restart the recording process

def monitor_camera(camera_url, camera_index):
    """
    Function that monitors the camera recording and restarts if necessary.
    """
    while True:
        try:
            # Start recording in a separate thread
            record_camera(camera_url, camera_index)
        except Exception as e:
            print(f"Error in monitoring thread for camera {camera_index}: {e}")
            print(f"Restarting camera {camera_index}...")

def start_recording(CAMERA_URLS):
    """
    Starts the recording process for each camera in a separate thread.
    """
    threads = []
    for i, url in enumerate(CAMERA_URLS):
        monitor_thread = threading.Thread(target=monitor_camera, args=(url, i))
        threads.append(monitor_thread)
        monitor_thread.start()
        time.sleep(3)

    # Join threads to keep the main script running
    for thread in threads:
        thread.join()
        time.sleep(3)



###############################################
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
        




#############################################################
if __name__ == "__main__": 

    # get camera information list from json file
    f_json = os.path.join( os.getcwd(), "camera_information.json")
    # Read in camera information from a jason file, return a list     
    rtsp_url = read_ip_camera_info(f_json)     
    
    start_recording(rtsp_url)





    
# if __name__ == "__main__":
#     # get camera information list from json file
#     f_json = os.path.join( os.getcwd(), "camera_information.json")
#     # Read in camera information from a jason file, return a list     
#     rtsp_url = read_ip_camera_info(f_json) 
#     print( rtsp_url ) 
    
#     # start multi threads camera recording task
#     start_recording(rtsp_url)    

#END 