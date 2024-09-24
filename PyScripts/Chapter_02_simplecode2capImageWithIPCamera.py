import cv2
# Replace with your IP camera's URL (usually in RTSP or HTTP format)
# Example: 'rtsp://username:password@ip_address:port/stream_path'
ip_camera_url = 'rtsp://THECAMERANAME:THEPASSWORD@192.168.1.168:554/stream1'
# Open the IP camera stream
cap = cv2.VideoCapture(ip_camera_url)
# Check if the camera stream opened successfully
if not cap.isOpened():
    print("Error: Could not open IP camera stream.")
    exit()
# Window name to display the camera feed
window_name = "IP Camera Feed"
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break
    # Resize the frame to a smaller size (e.g., 640x480)
    resized_frame = cv2.resize(frame, (320, 240))
    # Display the resized frame
    cv2.imshow(window_name, resized_frame)
    # Wait for the user to press the 's' key to save the image or 'q' to quit
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        # Save the original (non-resized) frame as an image
        cv2.imwrite('captured_image_ip_camera.png', frame)
        print("Image saved as 'captured_image_ip_camera.png'")
    elif key == ord('q'):
        # Break the loop and quit
        print("Exiting...")
        break
# When everything is done, release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
