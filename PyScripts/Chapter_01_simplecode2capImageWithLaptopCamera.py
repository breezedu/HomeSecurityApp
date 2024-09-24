import cv2
# Open the default camera (typically the laptop's webcam)
cap = cv2.VideoCapture(0)
# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
# Window name to display the camera feed
window_name = "Laptop Camera"
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()    
    if not ret:
        print("Error: Failed to capture image.")
        break
    # Resize the frame to a smaller size (e.g., 640x480)
    resized_frame = cv2.resize(frame, (640, 480))
    # Display the resized frame
    cv2.imshow(window_name, resized_frame)
    # Wait for the user to press the 's' key to save the image or 'q' to quit
    key = cv2.waitKey(1) & 0xFF    
    if key == ord('s'):
        # Save the original (non-resized) frame as an image
        cv2.imwrite('captured_image.png', frame)
        print("Image saved as 'captured_image.png'")
    elif key == ord('q'):
        # Break the loop and quit
        print("Exiting...")
        break
# When everything is done, release the camera and close all windows
cap.release()
cv2.destroyAllWindows()
