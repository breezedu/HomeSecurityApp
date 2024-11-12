import cv2
import time
import os
import threading
import json
import shutil
from datetime import datetime
from scapy.all import ARP, Ether, srp

# Configuration
VIDEO_DURATION = 30 * 60  # 30 minutes in seconds
TARGET_DIRECTORY = "./recorded_videos"

def find_ip_by_mac(mac_address, network_range="192.168.1.0/24"):
    """
    Finds the IP address associated with a given MAC address on the specified network.
    """
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request
    responses, _ = srp(packet, timeout=2, verbose=False)
    for sent, received in responses:
        if received.hwsrc.lower() == mac_address.lower():
            return received.psrc
    return None

def create_target_directory(base_directory):
    date_dir = datetime.now().strftime('%Y-%m-%d')
    full_path = os.path.join(base_directory, date_dir)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def delete_old_subdirectories(directory, three_weeks_ago):
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            creation_time = os.path.getctime(subdir_path)
            if creation_time < three_weeks_ago:
                print(f"Deleting: {subdir_path}")
                shutil.rmtree(subdir_path)

def get_video_filename(camera_index):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"camera_{camera_index}_{timestamp}.mp4"

def record_camera(camera_info, camera_index, json_path):
    """
    Records the video stream from a given IP camera MAC address with retry mechanism if the camera fails to open.
    """
    while True:
        try:
            # Dynamically fetch the IP address for the camera
            camera_info["ip"] = find_ip_by_mac(camera_info["mac"])
            if not camera_info["ip"]:
                print(f"Error: Could not find IP for camera with MAC {camera_info['mac']}")
                time.sleep(5)
                continue

            # Construct the RTSP URL
            rtsp_url = f"rtsp://{camera_info['username']}:{camera_info['password']}@{camera_info['ip']}/{camera_info['stream']}"

            cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                print(f"Error: Could not open camera {camera_index} - Retrying IP fetch")
                time.sleep(5)
                continue

            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15

            end_time = time.time() + VIDEO_DURATION
            video_path = create_target_directory(TARGET_DIRECTORY)
            now = time.time()
            three_weeks_ago = now - (3 * 7 * 24 * 60 * 60)
            delete_old_subdirectories(TARGET_DIRECTORY, three_weeks_ago)
            filename = get_video_filename(camera_index)
            filepath = os.path.join(video_path, filename)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))
            print(f"Recording {filepath} from camera {camera_index}")

            while time.time() < end_time:
                ret, frame = cap.read()
                if not ret:
                    print(f"Error: Failed to read frame from camera {camera_index}")
                    break
                out.write(frame)

            cap.release()
            out.release()
            print(f"Finished recording {filepath} from camera {camera_index}")

        except Exception as e:
            print(f"Exception in camera {camera_index}: {e}")

def monitor_camera(camera_info, camera_index, json_path):
    """
    Monitors and restarts the camera recording if necessary.
    """
    while True:
        try:
            record_camera(camera_info, camera_index, json_path)
        except Exception as e:
            print(f"Error in monitoring thread for camera {camera_index}: {e}")
            print(f"Restarting camera {camera_index}...")

def start_recording(json_path):
    """
    Starts the recording process for each camera in a separate thread.
    """
    camera_infos = load_camera_infos(json_path)
    threads = []
    for i, camera_info in enumerate(camera_infos):
        monitor_thread = threading.Thread(target=monitor_camera, args=(camera_info, i, json_path))
        threads.append(monitor_thread)
        monitor_thread.start()
        time.sleep(3)

    for thread in threads:
        thread.join()
        time.sleep(3)

def load_camera_infos(json_path):
    """
    Loads camera information from a JSON file. Each camera entry should include 'mac', 'username', 'password', and 'stream'.
    """
    with open(json_path, 'r') as f:
        cameras = json.load(f)
    
    camera_infos = []
    for camera in cameras:
        camera_info = {
            "mac": camera["mac"],
            "username": camera["username"],
            "password": camera["password"],
            "stream": camera["stream"]
        }
        camera_infos.append(camera_info)
    return camera_infos

###############################################

if __name__ == "__main__":
    # Path to the JSON file with camera information
    json_path = os.path.join(os.getcwd(), "camera_information_mac.json")

    # Start recording using the loaded camera information
    start_recording(json_path)

