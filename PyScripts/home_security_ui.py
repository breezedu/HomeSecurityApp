import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import cv2
import time
import os
import threading
import json
import shutil
from datetime import datetime
from PIL import Image, ImageTk
from scapy.all import ARP, Ether, srp

class HomeSecurityUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Home Security Camera System")
        self.root.geometry("1200x800")
        
        # Configuration
        self.config = {
            "video_duration": 30 * 60,  # 30 minutes
            "target_directory": "./recorded_videos2026",
            "network_range": "192.168.1.0/24",
            "json_path": "camera_information_mac.json"
        }
        
        # State variables
        self.is_recording = False
        self.camera_threads = []
        self.camera_infos = []
        self.camera_status = {}
        self.preview_labels = {}
        self.status_labels = {}
        
        # Setup UI
        self.setup_ui()
        
        # Load cameras
        self.load_cameras()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        camera_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cameras", menu=camera_menu)
        camera_menu.add_command(label="Add Camera", command=self.add_camera_dialog)
        camera_menu.add_command(label="Edit Camera", command=self.edit_camera_dialog)
        camera_menu.add_command(label="Delete Camera", command=self.delete_camera_dialog)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="▶ Start Recording", 
                                     command=self.start_recording, style="Success.TButton")
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹ Stop Recording", 
                                    command=self.stop_recording, state="disabled", 
                                    style="Danger.TButton")
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.refresh_btn = ttk.Button(control_frame, text="🔄 Refresh Cameras", 
                                       command=self.refresh_cameras)
        self.refresh_btn.grid(row=0, column=2, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Stopped", 
                                       font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=3, padx=20)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Camera Monitor Tab
        self.camera_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.camera_frame, text="📹 Camera Monitor")
        
        # Create scrollable frame for cameras
        canvas = tk.Canvas(self.camera_frame)
        scrollbar = ttk.Scrollbar(self.camera_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Log Tab
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Logs")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                   height=20, font=("Courier", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Recordings Tab
        recordings_frame = ttk.Frame(self.notebook)
        self.notebook.add(recordings_frame, text="💾 Recordings")
        
        recordings_control = ttk.Frame(recordings_frame)
        recordings_control.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(recordings_control, text="Open Recordings Folder", 
                   command=self.open_recordings_folder).pack(side="left", padx=5)
        ttk.Button(recordings_control, text="Refresh List", 
                   command=self.refresh_recordings).pack(side="left", padx=5)
        
        # Treeview for recordings
        tree_frame = ttk.Frame(recordings_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.recordings_tree = ttk.Treeview(tree_frame, 
                                            columns=("Camera", "Date", "Size"), 
                                            show="tree headings")
        self.recordings_tree.heading("#0", text="Filename")
        self.recordings_tree.heading("Camera", text="Camera")
        self.recordings_tree.heading("Date", text="Date/Time")
        self.recordings_tree.heading("Size", text="Size")
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", 
                                     command=self.recordings_tree.yview)
        self.recordings_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.recordings_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Apply custom styles
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom ttk styles"""
        style = ttk.Style()
        style.configure("Success.TButton", foreground="green")
        style.configure("Danger.TButton", foreground="red")
        
    def load_cameras(self):
        """Load camera information from JSON file"""
        try:
            if os.path.exists(self.config["json_path"]):
                with open(self.config["json_path"], 'r') as f:
                    cameras = json.load(f)
                    
                self.camera_infos = []
                for camera in cameras:
                    camera_info = {
                        "name": camera.get("Name", "Unknown"),
                        "mac": camera.get("mac", ""),
                        "username": camera.get("username", camera.get("Name", "")),
                        "password": camera.get("Password", ""),
                        "ip": camera.get("ip", ""),
                        "stream": camera.get("stream", "stream1"),
                        "enabled": camera.get("enabled", True)  # Default to enabled
                    }
                    self.camera_infos.append(camera_info)
                    
                self.update_camera_display()
                self.log(f"Loaded {len(self.camera_infos)} cameras from configuration")
            else:
                self.log("No camera configuration file found. Please add cameras.")
        except Exception as e:
            self.log(f"Error loading cameras: {e}")
            messagebox.showerror("Error", f"Failed to load cameras: {e}")
    
    def update_camera_display(self):
        """Update the camera display grid"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.preview_labels.clear()
        self.status_labels.clear()
        
        # Create camera cards in a grid (3 per row)
        for idx, camera_info in enumerate(self.camera_infos):
            row = idx // 3
            col = idx % 3
            
            camera_card = ttk.LabelFrame(self.scrollable_frame, 
                                         text=camera_info["name"], 
                                         padding="10")
            camera_card.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N))
            
            # On/Off toggle at the top
            toggle_frame = ttk.Frame(camera_card)
            toggle_frame.pack(fill="x", pady=(0, 5))
            
            enabled_var = tk.BooleanVar(value=camera_info.get("enabled", True))
            
            def create_toggle_handler(cam_idx, var):
                def toggle_handler():
                    self.toggle_camera(cam_idx, var.get())
                return toggle_handler
            
            toggle_btn = ttk.Checkbutton(toggle_frame, 
                                         text="Enable Recording",
                                         variable=enabled_var,
                                         command=create_toggle_handler(idx, enabled_var))
            toggle_btn.pack(side="left")
            
            # Visual indicator of enabled state
            enabled_indicator = ttk.Label(toggle_frame, 
                                          text="✓ ON" if camera_info.get("enabled", True) else "✕ OFF",
                                          foreground="green" if camera_info.get("enabled", True) else "gray",
                                          font=("Arial", 9, "bold"))
            enabled_indicator.pack(side="right")
            
            # Store reference for updates
            if not hasattr(self, 'enabled_indicators'):
                self.enabled_indicators = {}
            self.enabled_indicators[idx] = enabled_indicator
            
            # Preview placeholder
            preview_label = ttk.Label(camera_card, text="No Preview", 
                                      background="gray" if camera_info.get("enabled", True) else "darkgray",
                                      width=30, anchor="center",
                                      cursor="hand2" if camera_info.get("enabled", True) else "arrow")
            preview_label.pack(pady=5)
            self.preview_labels[idx] = preview_label
            
            # Make preview clickable only if enabled
            if camera_info.get("enabled", True):
                preview_label.bind("<Button-1>", lambda e, cam_idx=idx: self.open_camera_zoom(cam_idx))
            
            # Status
            status_text = "● Disabled" if not camera_info.get("enabled", True) else "● Idle"
            status_color = "gray"
            status_label = ttk.Label(camera_card, text=status_text, 
                                     foreground=status_color, font=("Arial", 9, "bold"))
            status_label.pack(pady=5)
            self.status_labels[idx] = status_label
            
            # Button frame for zoom and info buttons
            button_frame = ttk.Frame(camera_card)
            button_frame.pack(pady=5)
            
            # Add zoom button (disabled if camera is off)
            zoom_btn = ttk.Button(button_frame, text="🔍 View Full Screen", 
                                  command=lambda cam_idx=idx: self.open_camera_zoom(cam_idx),
                                  state="normal" if camera_info.get("enabled", True) else "disabled")
            zoom_btn.pack(side="left", padx=2)
            
            # Add camera info button
            info_btn = ttk.Button(button_frame, text="ℹ️ Camera Info", 
                                  command=lambda cam_idx=idx: self.show_camera_info(cam_idx))
            info_btn.pack(side="left", padx=2)
            
            # Store reference for updates
            if not hasattr(self, 'zoom_buttons'):
                self.zoom_buttons = {}
            self.zoom_buttons[idx] = zoom_btn
            
            self.camera_status[idx] = "disabled" if not camera_info.get("enabled", True) else "idle"
    
    def toggle_camera(self, camera_index, enabled):
        """Toggle a camera on or off"""
        if camera_index >= len(self.camera_infos):
            return
        
        camera_info = self.camera_infos[camera_index]
        camera_info["enabled"] = enabled
        
        # Update UI elements
        if camera_index in self.enabled_indicators:
            indicator = self.enabled_indicators[camera_index]
            if enabled:
                indicator.config(text="✓ ON", foreground="green")
            else:
                indicator.config(text="✕ OFF", foreground="gray")
        
        # Update preview background
        if camera_index in self.preview_labels:
            preview = self.preview_labels[camera_index]
            preview.config(background="gray" if enabled else "darkgray",
                          cursor="hand2" if enabled else "arrow")
            # Update click binding
            preview.unbind("<Button-1>")
            if enabled:
                preview.bind("<Button-1>", lambda e, cam_idx=camera_index: self.open_camera_zoom(cam_idx))
        
        # Update zoom button state
        if camera_index in self.zoom_buttons:
            self.zoom_buttons[camera_index].config(state="normal" if enabled else "disabled")
        
        # Update status
        if self.is_recording:
            if not enabled:
                # Stop this camera if it's recording
                self.update_camera_status(camera_index, "● Disabled", "gray")
                self.camera_status[camera_index] = "disabled"
                self.log(f"Camera {camera_info['name']} disabled during recording")
            else:
                # Start this camera if recording is active
                self.update_camera_status(camera_index, "● Starting...", "orange")
                self.camera_status[camera_index] = "starting"
                # Start a new thread for this camera
                monitor_thread = threading.Thread(target=self.monitor_camera, 
                                                   args=(camera_info, camera_index), 
                                                   daemon=True)
                self.camera_threads.append(monitor_thread)
                monitor_thread.start()
                self.log(f"Camera {camera_info['name']} enabled during recording")
        else:
            # Not recording, just update status
            if enabled:
                self.update_camera_status(camera_index, "● Idle", "gray")
                self.camera_status[camera_index] = "idle"
            else:
                self.update_camera_status(camera_index, "● Disabled", "gray")
                self.camera_status[camera_index] = "disabled"
        
        # Save the updated configuration
        self.save_camera_config()
        
        self.log(f"Camera {camera_info['name']} {'enabled' if enabled else 'disabled'}")
    
    def save_camera_config(self):
        """Save current camera configuration including enabled states"""
        try:
            cameras = []
            for camera_info in self.camera_infos:
                camera = {
                    "Name": camera_info["name"],
                    "mac": camera_info.get("mac", ""),
                    "username": camera_info["username"],
                    "Password": camera_info["password"],
                    "ip": camera_info.get("ip", ""),
                    "stream": camera_info["stream"],
                    "enabled": camera_info.get("enabled", True)
                }
                cameras.append(camera)
            
            with open(self.config["json_path"], 'w') as f:
                json.dump(cameras, f, indent=2)
                
        except Exception as e:
            self.log(f"Error saving camera configuration: {e}")
    
    def start_recording(self):
        """Start recording from all enabled cameras"""
        if self.is_recording:
            return
        
        # Check if at least one camera is enabled
        enabled_cameras = [cam for cam in self.camera_infos if cam.get("enabled", True)]
        if not enabled_cameras:
            messagebox.showwarning("No Cameras Enabled", 
                                   "Please enable at least one camera before starting recording.")
            return
        
        if not self.camera_infos:
            messagebox.showwarning("No Cameras", "Please add cameras before starting recording.")
            return
        
        self.is_recording = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="Status: Recording", foreground="red")
        
        self.log("=" * 50)
        self.log("Starting recording session...")
        
        # Start recording threads only for enabled cameras
        for i, camera_info in enumerate(self.camera_infos):
            if camera_info.get("enabled", True):
                monitor_thread = threading.Thread(target=self.monitor_camera, 
                                                   args=(camera_info, i), 
                                                   daemon=True)
                self.camera_threads.append(monitor_thread)
                monitor_thread.start()
                time.sleep(1)  # Stagger starts
            else:
                self.update_camera_status(i, "● Disabled", "gray")
                self.camera_status[i] = "disabled"
                self.log(f"Skipping disabled camera: {camera_info['name']}")
            
        enabled_count = len(enabled_cameras)
        self.update_status_bar(f"Recording from {enabled_count} camera(s)")
        self.log(f"Started recording from {enabled_count} enabled camera(s)")
    
    def stop_recording(self):
        """Stop recording from all cameras"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Status: Stopped", foreground="black")
        
        self.log("Stopping all recordings...")
        
        # Threads will exit on their own when is_recording becomes False
        self.camera_threads.clear()
        
        # Update all camera statuses
        for idx in self.camera_status:
            camera_info = self.camera_infos[idx] if idx < len(self.camera_infos) else {}
            if not camera_info.get("enabled", True):
                self.camera_status[idx] = "disabled"
                self.update_camera_status(idx, "● Disabled", "gray")
            else:
                self.camera_status[idx] = "idle"
                self.update_camera_status(idx, "● Idle", "gray")
        
        self.update_status_bar("Recording stopped")
        self.log("All recordings stopped")
        
    def monitor_camera(self, camera_info, camera_index):
        """Monitor and record from a camera"""
        while self.is_recording and camera_info.get("enabled", True):
            try:
                self.record_camera(camera_info, camera_index)
            except Exception as e:
                self.log(f"Error in monitoring camera {camera_info['name']}: {e}")
                if self.is_recording and camera_info.get("enabled", True):
                    self.log(f"Restarting camera {camera_info['name']}...")
                    time.sleep(5)
    
    def record_camera(self, camera_info, camera_index):
        """Record video from a camera"""
        while self.is_recording and camera_info.get("enabled", True):
            try:
                # Find IP if using MAC address
                if camera_info.get("mac") and not camera_info.get("ip"):
                    self.update_camera_status(camera_index, "● Finding IP...", "orange")
                    camera_info["ip"] = self.find_ip_by_mac(camera_info["mac"])
                    if not camera_info["ip"]:
                        self.log(f"Could not find IP for {camera_info['name']} (MAC: {camera_info['mac']})")
                        self.update_camera_status(camera_index, "● IP Not Found", "red")
                        time.sleep(10)
                        continue
                
                # Construct RTSP URL
                rtsp_url = f"rtsp://{camera_info['username']}:{camera_info['password']}@{camera_info['ip']}/{camera_info['stream']}"
                
                self.update_camera_status(camera_index, "● Connecting...", "orange")
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                
                if not cap.isOpened():
                    self.log(f"Could not open camera {camera_info['name']} at {camera_info['ip']}")
                    self.update_camera_status(camera_index, "● Connection Failed", "red")
                    time.sleep(10)
                    continue
                
                # Get video properties
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS)) or 15
                
                # Setup output
                end_time = time.time() + self.config["video_duration"]
                video_path = self.create_target_directory(self.config["target_directory"])
                
                # Cleanup old recordings
                now = time.time()
                three_weeks_ago = now - (3 * 7 * 24 * 60 * 60)
                self.delete_old_subdirectories(self.config["target_directory"], three_weeks_ago)
                
                filename = self.get_video_filename(camera_index, camera_info['name'])
                filepath = os.path.join(video_path, filename)
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(filepath, fourcc, fps, (frame_width, frame_height))
                
                self.log(f"Recording {camera_info['name']} to {filename}")
                self.update_camera_status(camera_index, "● Recording", "green")
                self.camera_status[camera_index] = "recording"
                
                frame_count = 0
                while time.time() < end_time and self.is_recording and camera_info.get("enabled", True):
                    ret, frame = cap.read()
                    if not ret:
                        self.log(f"Failed to read frame from {camera_info['name']}")
                        break
                    
                    out.write(frame)
                    frame_count += 1
                    
                    # Update preview every 30 frames
                    if frame_count % 30 == 0:
                        self.update_preview(camera_index, frame)
                
                cap.release()
                out.release()
                
                if not camera_info.get("enabled", True):
                    self.log(f"Camera {camera_info['name']} was disabled - stopping recording")
                    break
                elif self.is_recording:
                    self.log(f"Finished recording {camera_info['name']} - {frame_count} frames")
                else:
                    self.log(f"Recording stopped for {camera_info['name']}")
                    break
                
            except Exception as e:
                self.log(f"Exception in camera {camera_info['name']}: {e}")
                self.update_camera_status(camera_index, "● Error", "red")
                if self.is_recording:
                    time.sleep(5)
                else:
                    break
    
    def update_preview(self, camera_index, frame):
        """Update camera preview image"""
        try:
            # Resize frame for preview
            preview_frame = cv2.resize(frame, (240, 180))
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(preview_frame)
            photo = ImageTk.PhotoImage(image=img)
            
            # Update label
            if camera_index in self.preview_labels:
                label = self.preview_labels[camera_index]
                label.config(image=photo, text="")
                label.image = photo  # Keep a reference
        except Exception as e:
            pass  # Ignore preview errors
    
    def update_camera_status(self, camera_index, text, color):
        """Update camera status label"""
        if camera_index in self.status_labels:
            self.status_labels[camera_index].config(text=text, foreground=color)
    
    def find_ip_by_mac(self, mac_address):
        """Find IP address by MAC address using ARP"""
        try:
            network_range = self.config["network_range"]
            arp_request = ARP(pdst=network_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            responses, _ = srp(packet, timeout=2, verbose=False)
            
            for sent, received in responses:
                if received.hwsrc.lower() == mac_address.lower():
                    return received.psrc
            return None
        except Exception as e:
            self.log(f"Error finding IP for MAC {mac_address}: {e}")
            return None
    
    def create_target_directory(self, base_directory):
        """Create dated directory for recordings"""
        date_dir = datetime.now().strftime('%Y-%m-%d')
        full_path = os.path.join(base_directory, date_dir)
        os.makedirs(full_path, exist_ok=True)
        return full_path
    
    def delete_old_subdirectories(self, directory, three_weeks_ago):
        """Delete recordings older than 3 weeks"""
        if not os.path.exists(directory):
            return
        
        for subdir in os.listdir(directory):
            subdir_path = os.path.join(directory, subdir)
            if os.path.isdir(subdir_path):
                creation_time = os.path.getctime(subdir_path)
                if creation_time < three_weeks_ago:
                    self.log(f"Deleting old recordings: {subdir_path}")
                    shutil.rmtree(subdir_path)
    
    def get_video_filename(self, camera_index, camera_name):
        """Generate video filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = camera_name.replace(" ", "_")
        return f"{safe_name}_{timestamp}.mp4"
    
    def refresh_cameras(self):
        """Reload cameras from configuration"""
        self.load_cameras()
        self.update_status_bar("Cameras refreshed")
    
    def add_camera_dialog(self):
        """Show dialog to add a new camera"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Camera")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="Camera Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="MAC Address:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        mac_entry = ttk.Entry(dialog, width=30)
        mac_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="IP Address (optional):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ip_entry = ttk.Entry(dialog, width=30)
        ip_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Username:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        username_entry = ttk.Entry(dialog, width=30)
        username_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Password:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        password_entry = ttk.Entry(dialog, width=30, show="*")
        password_entry.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Stream Path:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        stream_entry = ttk.Entry(dialog, width=30)
        stream_entry.insert(0, "stream1")
        stream_entry.grid(row=5, column=1, padx=10, pady=5)
        
        def save_camera():
            name = name_entry.get().strip()
            mac = mac_entry.get().strip()
            ip = ip_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get()
            stream = stream_entry.get().strip()
            
            if not name or not mac or not username or not password:
                messagebox.showwarning("Invalid Input", "Please fill in all required fields.")
                return
            
            new_camera = {
                "Name": name,
                "mac": mac,
                "username": username,
                "Password": password,
                "ip": ip,
                "stream": stream
            }
            
            # Load existing cameras
            cameras = []
            if os.path.exists(self.config["json_path"]):
                with open(self.config["json_path"], 'r') as f:
                    cameras = json.load(f)
            
            cameras.append(new_camera)
            
            # Save to file
            with open(self.config["json_path"], 'w') as f:
                json.dump(cameras, f, indent=2)
            
            self.log(f"Added camera: {name}")
            self.load_cameras()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_camera).grid(row=6, column=0, columnspan=2, pady=20)
    
    def edit_camera_dialog(self):
        """Show dialog to edit a camera"""
        messagebox.showinfo("Edit Camera", "Select a camera from the list and use Delete + Add for now.")
    
    def delete_camera_dialog(self):
        """Show dialog to delete a camera"""
        if not self.camera_infos:
            messagebox.showinfo("No Cameras", "No cameras to delete.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Camera")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Select camera to delete:").pack(padx=10, pady=10)
        
        listbox = tk.Listbox(dialog)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for camera in self.camera_infos:
            listbox.insert(tk.END, camera["name"])
        
        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a camera to delete.")
                return
            
            idx = selection[0]
            camera_name = self.camera_infos[idx]["name"]
            
            if messagebox.askyesno("Confirm Delete", f"Delete camera '{camera_name}'?"):
                # Load cameras from file
                with open(self.config["json_path"], 'r') as f:
                    cameras = json.load(f)
                
                # Remove camera
                cameras.pop(idx)
                
                # Save back
                with open(self.config["json_path"], 'w') as f:
                    json.dump(cameras, f, indent=2)
                
                self.log(f"Deleted camera: {camera_name}")
                self.load_cameras()
                dialog.destroy()
        
        ttk.Button(dialog, text="Delete Selected", command=delete_selected).pack(pady=10)
    
    def open_settings(self):
        """Show settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x300")
        
        ttk.Label(dialog, text="Video Duration (minutes):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        duration_var = tk.IntVar(value=self.config["video_duration"] // 60)
        duration_entry = ttk.Entry(dialog, textvariable=duration_var, width=20)
        duration_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(dialog, text="Recording Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        dir_entry = ttk.Entry(dialog, width=30)
        dir_entry.insert(0, self.config["target_directory"])
        dir_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def browse_directory():
            directory = filedialog.askdirectory(initialdir=self.config["target_directory"])
            if directory:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, directory)
        
        ttk.Button(dialog, text="Browse", command=browse_directory).grid(row=1, column=2, padx=5, pady=10)
        
        ttk.Label(dialog, text="Network Range:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        network_entry = ttk.Entry(dialog, width=30)
        network_entry.insert(0, self.config["network_range"])
        network_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save_settings():
            self.config["video_duration"] = duration_var.get() * 60
            self.config["target_directory"] = dir_entry.get()
            self.config["network_range"] = network_entry.get()
            self.log("Settings updated")
            messagebox.showinfo("Settings", "Settings saved successfully!")
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_settings).grid(row=3, column=0, columnspan=3, pady=20)
    
    def open_recordings_folder(self):
        """Open the recordings folder in file explorer"""
        if os.path.exists(self.config["target_directory"]):
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                os.startfile(self.config["target_directory"])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.config["target_directory"]])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.config["target_directory"]])
        else:
            messagebox.showinfo("No Recordings", "Recordings folder does not exist yet.")
    
    def refresh_recordings(self):
        """Refresh the recordings list"""
        self.recordings_tree.delete(*self.recordings_tree.get_children())
        
        if not os.path.exists(self.config["target_directory"]):
            return
        
        for date_dir in sorted(os.listdir(self.config["target_directory"]), reverse=True):
            date_path = os.path.join(self.config["target_directory"], date_dir)
            if os.path.isdir(date_path):
                parent = self.recordings_tree.insert("", "end", text=date_dir, open=True)
                
                for filename in sorted(os.listdir(date_path), reverse=True):
                    filepath = os.path.join(date_path, filename)
                    if os.path.isfile(filepath) and filename.endswith('.mp4'):
                        # Extract camera name
                        camera_name = filename.split('_')[0] if '_' in filename else "Unknown"
                        
                        # Get file info
                        file_size = os.path.getsize(filepath)
                        size_mb = file_size / (1024 * 1024)
                        
                        # Get timestamp from filename or file
                        try:
                            timestamp = datetime.fromtimestamp(os.path.getmtime(filepath))
                            date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            date_str = "Unknown"
                        
                        self.recordings_tree.insert(parent, "end", text=filename, 
                                                    values=(camera_name, date_str, f"{size_mb:.1f} MB"))
        
        self.update_status_bar("Recordings list refreshed")
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        print(message)  # Also print to console
    
    def update_status_bar(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
    
    def show_camera_info(self, camera_index):
        """Show detailed camera information in a dialog"""
        if camera_index >= len(self.camera_infos):
            return
        
        camera_info = self.camera_infos[camera_index]
        
        # Create info dialog
        info_dialog = tk.Toplevel(self.root)
        info_dialog.title(f"Camera Information - {camera_info['name']}")
        info_dialog.geometry("450x350")
        info_dialog.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(info_dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, 
                                text=f"📹 {camera_info['name']}", 
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Information grid
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="both", expand=True)
        
        # Configure grid columns
        info_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Camera Name
        ttk.Label(info_frame, text="Camera Name:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ttk.Label(info_frame, text=camera_info['name'], 
                  font=("Arial", 9)).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Status
        status_text = "Enabled" if camera_info.get("enabled", True) else "Disabled"
        status_color = "green" if camera_info.get("enabled", True) else "gray"
        ttk.Label(info_frame, text="Status:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        status_label = ttk.Label(info_frame, text=status_text, 
                                 font=("Arial", 9), foreground=status_color)
        status_label.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Separator
        ttk.Separator(info_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, 
                                                             sticky="ew", pady=10)
        row += 1
        
        # IP Address
        ttk.Label(info_frame, text="IP Address:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ip_text = camera_info.get('ip', 'Not found')
        ip_label = ttk.Label(info_frame, text=ip_text, font=("Arial", 9))
        ip_label.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # MAC Address
        if camera_info.get('mac'):
            ttk.Label(info_frame, text="MAC Address:", 
                      font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
            ttk.Label(info_frame, text=camera_info['mac'], 
                      font=("Arial", 9)).grid(row=row, column=1, sticky="w", pady=5)
            row += 1
        
        # Username
        ttk.Label(info_frame, text="Username:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ttk.Label(info_frame, text=camera_info['username'], 
                  font=("Arial", 9)).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Stream Path
        ttk.Label(info_frame, text="Stream Path:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 10))
        ttk.Label(info_frame, text=camera_info['stream'], 
                  font=("Arial", 9)).grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Separator
        ttk.Separator(info_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, 
                                                             sticky="ew", pady=10)
        row += 1
        
        # RTSP URL
        ttk.Label(info_frame, text="RTSP URL:", 
                  font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="nw", pady=5, padx=(0, 10))
        rtsp_url = f"rtsp://{camera_info['username']}:****@{camera_info.get('ip', 'unknown')}/{camera_info['stream']}"
        rtsp_label = ttk.Label(info_frame, text=rtsp_url, 
                               font=("Arial", 8), wraplength=250)
        rtsp_label.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        # Copy IP button
        def copy_ip():
            info_dialog.clipboard_clear()
            info_dialog.clipboard_append(camera_info.get('ip', ''))
            messagebox.showinfo("Copied", f"IP address copied to clipboard:\n{camera_info.get('ip', '')}", 
                               parent=info_dialog)
        
        ttk.Button(button_frame, text="📋 Copy IP", 
                   command=copy_ip).pack(side="left", padx=5)
        
        # Test connection button
        def test_connection():
            test_btn.config(state="disabled", text="Testing...")
            info_dialog.update()
            
            rtsp_url = f"rtsp://{camera_info['username']}:{camera_info['password']}@{camera_info.get('ip', '')}/{camera_info['stream']}"
            
            def test_thread():
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                success = cap.isOpened()
                if success:
                    ret, frame = cap.read()
                    success = ret
                cap.release()
                
                # Update UI in main thread
                info_dialog.after(0, lambda: show_result(success))
            
            def show_result(success):
                test_btn.config(state="normal", text="🔌 Test Connection")
                if success:
                    messagebox.showinfo("Connection Test", 
                                       "✅ Connection successful!\nCamera is reachable and streaming.", 
                                       parent=info_dialog)
                else:
                    messagebox.showerror("Connection Test", 
                                        "❌ Connection failed!\nCheck camera power, network, and credentials.", 
                                        parent=info_dialog)
            
            threading.Thread(target=test_thread, daemon=True).start()
        
        test_btn = ttk.Button(button_frame, text="🔌 Test Connection", 
                              command=test_connection)
        test_btn.pack(side="left", padx=5)
        
        # Close button
        ttk.Button(button_frame, text="✕ Close", 
                   command=info_dialog.destroy).pack(side="left", padx=5)
        
        # Center the dialog
        info_dialog.transient(self.root)
        info_dialog.grab_set()
        
        # Center on parent window
        info_dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (info_dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (info_dialog.winfo_height() // 2)
        info_dialog.geometry(f"+{x}+{y}")
    
    def open_camera_zoom(self, camera_index):
        """Open a zoomed/detailed view of a specific camera"""
        if camera_index >= len(self.camera_infos):
            return
        
        camera_info = self.camera_infos[camera_index]
        
        # Create zoom window
        zoom_window = tk.Toplevel(self.root)
        zoom_window.title(f"{camera_info['name']} - Live View")
        zoom_window.geometry("960x720")
        
        # Main container
        main_frame = ttk.Frame(zoom_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Camera info header
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        camera_title = ttk.Label(info_frame, 
                                  text=f"📹 {camera_info['name']}", 
                                  font=("Arial", 14, "bold"))
        camera_title.pack(side="left")
        
        camera_details = ttk.Label(info_frame, 
                                    text=f"IP: {camera_info['ip']} | Stream: {camera_info['stream']}", 
                                    font=("Arial", 10))
        camera_details.pack(side="left", padx=20)
        
        status_label = ttk.Label(info_frame, text="● Connecting...", 
                                 foreground="orange", font=("Arial", 10, "bold"))
        status_label.pack(side="right")
        
        # Video display area
        video_frame = ttk.Frame(main_frame, relief="solid", borderwidth=2)
        video_frame.pack(fill="both", expand=True)
        
        video_label = ttk.Label(video_frame, text="Loading...", 
                                background="black", foreground="white",
                                font=("Arial", 16))
        video_label.pack(fill="both", expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=(10, 0))
        
        # Recording indicator
        rec_indicator = ttk.Label(control_frame, text="⏺ Not Recording", 
                                  foreground="gray", font=("Arial", 10))
        rec_indicator.pack(side="left")
        
        # Snapshot button
        snapshot_btn = ttk.Button(control_frame, text="📸 Take Snapshot",
                                  command=lambda: self.take_snapshot(camera_index, video_label))
        snapshot_btn.pack(side="left", padx=10)
        
        # Close button
        close_btn = ttk.Button(control_frame, text="✕ Close", 
                               command=zoom_window.destroy)
        close_btn.pack(side="right")
        
        # Stream state
        stream_active = {"active": True}
        cap = None
        
        def update_zoom_view():
            """Update the zoomed camera view"""
            nonlocal cap
            
            if not stream_active["active"]:
                return
            
            try:
                # Initialize capture if needed
                if cap is None or not cap.isOpened():
                    rtsp_url = f"rtsp://{camera_info['username']}:{camera_info['password']}@{camera_info['ip']}/{camera_info['stream']}"
                    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                    
                    if not cap.isOpened():
                        status_label.config(text="● Connection Failed", foreground="red")
                        video_label.config(text="Failed to connect to camera\nCheck camera status and try again")
                        zoom_window.after(5000, update_zoom_view)  # Retry after 5 seconds
                        return
                    
                    status_label.config(text="● Connected", foreground="green")
                
                # Read frame
                ret, frame = cap.read()
                
                if ret:
                    # Resize frame to fit window (maintain aspect ratio)
                    window_width = video_label.winfo_width()
                    window_height = video_label.winfo_height()
                    
                    if window_width > 1 and window_height > 1:  # Window is ready
                        # Calculate scaling to fit window
                        frame_height, frame_width = frame.shape[:2]
                        scale_w = window_width / frame_width
                        scale_h = window_height / frame_height
                        scale = min(scale_w, scale_h)
                        
                        new_width = int(frame_width * scale)
                        new_height = int(frame_height * scale)
                        
                        resized_frame = cv2.resize(frame, (new_width, new_height))
                        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                        
                        # Convert to PhotoImage
                        img = Image.fromarray(resized_frame)
                        photo = ImageTk.PhotoImage(image=img)
                        
                        # Update label
                        video_label.config(image=photo, text="")
                        video_label.image = photo  # Keep reference
                        
                        # Update recording indicator
                        if self.is_recording and camera_index in self.camera_status:
                            if self.camera_status[camera_index] == "recording":
                                rec_indicator.config(text="⏺ Recording", foreground="red")
                            else:
                                rec_indicator.config(text="⏺ Not Recording", foreground="gray")
                    
                    # Schedule next update (30 FPS)
                    zoom_window.after(33, update_zoom_view)
                else:
                    status_label.config(text="● Stream Error", foreground="orange")
                    video_label.config(text="Stream interrupted\nRetrying...")
                    if cap:
                        cap.release()
                        cap = None
                    zoom_window.after(2000, update_zoom_view)  # Retry after 2 seconds
                    
            except Exception as e:
                print(f"Error in zoom view: {e}")
                status_label.config(text="● Error", foreground="red")
                if cap:
                    cap.release()
                    cap = None
                zoom_window.after(5000, update_zoom_view)  # Retry after 5 seconds
        
        def on_zoom_close():
            """Cleanup when zoom window closes"""
            stream_active["active"] = False
            if cap:
                cap.release()
            zoom_window.destroy()
        
        # Start video stream
        zoom_window.after(100, update_zoom_view)
        zoom_window.protocol("WM_DELETE_WINDOW", on_zoom_close)
    
    def take_snapshot(self, camera_index, video_label):
        """Take a snapshot from the current video feed"""
        try:
            # Get the current image from the label
            if hasattr(video_label, 'image'):
                # Create snapshots directory
                snapshot_dir = "./snapshots"
                os.makedirs(snapshot_dir, exist_ok=True)
                
                # Generate filename
                camera_name = self.camera_infos[camera_index]["name"]
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{camera_name}_snapshot_{timestamp}.png"
                filepath = os.path.join(snapshot_dir, filename)
                
                # Save the image
                # Get the PhotoImage and convert back to PIL Image
                photo_image = video_label.image
                # Since PhotoImage doesn't have a direct save method, we'll capture from camera
                
                # Alternative: Capture fresh frame from camera
                camera_info = self.camera_infos[camera_index]
                rtsp_url = f"rtsp://{camera_info['username']}:{camera_info['password']}@{camera_info['ip']}/{camera_info['stream']}"
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imwrite(filepath, frame)
                        self.log(f"Snapshot saved: {filename}")
                        messagebox.showinfo("Snapshot Saved", 
                                          f"Snapshot saved to:\n{filepath}")
                    cap.release()
                else:
                    messagebox.showerror("Error", "Failed to capture snapshot")
            else:
                messagebox.showwarning("No Image", "No video feed available to capture")
                
        except Exception as e:
            self.log(f"Error taking snapshot: {e}")
            messagebox.showerror("Error", f"Failed to save snapshot: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_recording:
            if messagebox.askokcancel("Quit", "Recording is in progress. Stop and quit?"):
                self.stop_recording()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = HomeSecurityUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
