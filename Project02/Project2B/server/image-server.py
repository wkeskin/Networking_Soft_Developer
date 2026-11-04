#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMP216 - SEC 401
Networking for Software Developers - Lab 5 Part II
Group 2: 
    Aiko Bislig 
    Jacob Ferreira
    Lissette Gorrin Rodriguez
    Samer Aljundi Al Fattouhi Aljundi
    Wardatul Keskin

Enhanced with multi-session support
"""

from flask import Flask, request, jsonify, send_file, session
import os
import time
import uuid
from PIL import Image
from io import BytesIO
import datetime
import threading
import logging
from flask_socketio import SocketIO
from functools import wraps

class ImageServer:
    def __init__(self, host='127.0.0.1', port=5000):
        """Initialize the Flask-based API server with session support"""
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)  # Required for session management
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.host = host
        self.port = port
        self.images_dir = os.path.join(os.getcwd(), 'images')
        self.session_lock = threading.Lock()
        self.active_sessions = {}  # Track active client sessions
        self.client_activities = {}  # Track client activities 
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            handlers=[logging.FileHandler("server.log"), 
                                     logging.StreamHandler()])
        self.logger = logging.getLogger("ImageServer")
        
        # Create images directory if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        
        # Define routes
        self.define_routes()
        self.setup_socketio()
        
    def session_required(self, f):
        """Decorator to ensure session is active"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = session.get('session_id')
            if not session_id or session_id not in self.active_sessions:
                # Create a new session if one doesn't exist
                if not session_id:
                    session_id = str(uuid.uuid4())
                    session['session_id'] = session_id
                    with self.session_lock:
                        self.active_sessions[session_id] = {
                            'created_at': datetime.datetime.now(),
                            'last_activity': datetime.datetime.now(),
                            'client_ip': request.remote_addr,
                            'user_agent': request.headers.get('User-Agent', 'Unknown')
                        }
                    self.logger.info(f"Created new session: {session_id} for {request.remote_addr}")
                    self.notify_all_clients_session_update()
            
            # Update last activity time
            with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]['last_activity'] = datetime.datetime.now()
                    
                    # Track this activity
                    if session_id not in self.client_activities:
                        self.client_activities[session_id] = []
                    
                    activity = {
                        'endpoint': request.path,
                        'method': request.method,
                        'timestamp': datetime.datetime.now()
                    }
                    self.client_activities[session_id].append(activity)
                    
                    # Limit activity history to 100 entries per client
                    if len(self.client_activities[session_id]) > 100:
                        self.client_activities[session_id] = self.client_activities[session_id][-100:]
            
            return f(*args, **kwargs)
        return decorated_function
        
    def define_routes(self):
        """Define the API routes for the server"""
        @self.app.route('/')
        def home():
            return jsonify({
                "message": "Welcome to the Image Server!",
                "endpoints": {
                    "List Images": "/image-list",
                    "Upload Image": "/uploads",
                    "Get Image": "/get-image/<filename>",
                    "Delete Image": "/delete-image/<filename>",
                    "Session Info": "/session-info"
                }
            }), 200
        @self.app.route('/session-info', methods=['GET'])
        @self.session_required
        def get_session_info():
            session_id = session.get('session_id')
            return jsonify({
                'session_id': session_id,
                'session_created': self.active_sessions[session_id]['created_at'].isoformat(),
                'last_activity': self.active_sessions[session_id]['last_activity'].isoformat(),
                'client_ip': self.active_sessions[session_id]['client_ip']
            })
                    
        @self.app.route('/admin/active-sessions', methods=['GET'])
        def get_active_sessions():
            # This would typically require admin authentication
            # Simplified for demonstration
            admin_key = request.args.get('admin_key')
            if admin_key != 'admin123':  # Simple auth for demo purposes
                return jsonify({'error': 'Unauthorized'}), 401
                
            with self.session_lock:
                sessions_info = {}
                for sess_id, sess_data in self.active_sessions.items():
                    sessions_info[sess_id] = {
                        'created_at': sess_data['created_at'].isoformat(),
                        'last_activity': sess_data['last_activity'].isoformat(),
                        'client_ip': sess_data['client_ip'],
                        'user_agent': sess_data['user_agent'],
                        'activity_count': len(self.client_activities.get(sess_id, []))
                    }
                return jsonify({
                    'active_sessions': sessions_info,
                    'total_count': len(self.active_sessions)
                })
        
        @self.app.route('/admin/terminate-session/<session_id>', methods=['POST'])
        def terminate_session(session_id):
            # This would typically require admin authentication
            admin_key = request.args.get('admin_key')
            if admin_key != 'admin123':  # Simple auth for demo purposes
                return jsonify({'error': 'Unauthorized'}), 401
                
            with self.session_lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                    if session_id in self.client_activities:
                        del self.client_activities[session_id]
                    self.logger.info(f"Terminated session: {session_id}")
                    self.notify_all_clients_session_update()
                    return jsonify({'message': f'Session {session_id} terminated'})
                else:
                    return jsonify({'error': 'Session not found'}), 404
                    
        @self.app.route('/admin/session-activity/<session_id>', methods=['GET'])
        def get_session_activity(session_id):
            # This would typically require admin authentication
            admin_key = request.args.get('admin_key')
            if admin_key != 'admin123':  # Simple auth for demo purposes
                return jsonify({'error': 'Unauthorized'}), 401
                
            with self.session_lock:
                if session_id not in self.active_sessions:
                    return jsonify({'error': 'Session not found'}), 404
                
                activities = self.client_activities.get(session_id, [])
                formatted_activities = []
                for activity in activities:
                    formatted_activities.append({
                        'endpoint': activity['endpoint'],
                        'method': activity['method'],
                        'timestamp': activity['timestamp'].isoformat()
                    })
                
                return jsonify({
                    'session_id': session_id,
                    'activities': formatted_activities,
                    'total_count': len(formatted_activities)
                })
        
        @self.app.route('/image-list', methods=['GET'])
        @self.session_required
        def get_image_list():
            try:
                # Get all PNG files in the images directory
                image_list = [f for f in os.listdir(self.images_dir) if f.endswith('.png')]
                self.logger.info(f"Session {session.get('session_id')} requested image list, found {len(image_list)} images")
                return jsonify({'images': image_list})
            except Exception as e:
                self.logger.error(f"Error retrieving image list: {str(e)}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/get-image/<filename>', methods=['GET'])
        @self.session_required
        def get_image(filename):
            try:
                image_path = os.path.join(self.images_dir, filename)
                
                if not os.path.exists(image_path):
                    return jsonify({'error': 'Image not found'}), 404
        
                # Get requested format
                req_format = request.args.get('format', 'PNG').upper()
                valid_formats = ['PNG', 'JPEG', 'JPG', 'GIF', 'BMP']
                
                if req_format not in valid_formats:
                    return jsonify({'error': f'Invalid format. Supported: {", ".join(valid_formats)}'}), 400
        
                img = Image.open(image_path)
                return_img = BytesIO()
                
                # Handle format conversion
                if req_format == 'JPG':
                    req_format = 'JPEG'
                    
                img.save(return_img, req_format)
                return_img.seek(0)
                
                # Get image properties
                image_properties = {
                    'format': req_format,
                    'size': img.size,
                    'mode': img.mode,
                    'date_modified': datetime.datetime.fromtimestamp(os.path.getmtime(image_path)).strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Dynamic MIME type and filename
                mimetype = f'image/{req_format.lower()}'
                download_name = f"{os.path.splitext(filename)[0]}.{req_format.lower()}"
                
                response = send_file(
                    return_img,
                    mimetype=mimetype,
                    as_attachment=True,
                    download_name=download_name
                )
                
                # Add headers
                for key, value in image_properties.items():
                    if isinstance(value, tuple):
                        value = f"{value[0]}x{value[1]}"
                    response.headers[f'X-Image-{key.capitalize()}'] = str(value)
                
                # Notify clients of the view event
                self.notify_all_clients_image_viewed(filename, session.get('session_id'))
                
                return response
                
            except Exception as e:
                self.logger.error(f"Error retrieving image {filename}: {str(e)}")
                return jsonify({'error': str(e)}), 500
        @self.app.route('/uploads', methods=['POST'])
        @self.session_required
        def upload_image():
            try:
                # Check if the post request has the file part
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part'}), 400
                
                file = request.files['file']
                
                # If user does not select file, browser also
                # submits an empty part without filename
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                
                # Save the uploaded file
                image = Image.open(file)
                
                # Generate a unique filename if none provided
                if '.' in file.filename:
                    filename = file.filename.rsplit('.', 1)[0]
                else:
                    filename = file.filename
                
                # Convert to PNG and save
                png_filename = f"{filename}.png"
                png_path = os.path.join(self.images_dir, png_filename)
                
                # If file exists, add timestamp to make it unique
                if os.path.exists(png_path):
                    timestamp = int(time.time())
                    png_filename = f"{filename}_{timestamp}.png"
                    png_path = os.path.join(self.images_dir, png_filename)
                
                image.save(png_path, 'PNG')
                
                self.logger.info(f"Session {session.get('session_id')} uploaded image: {png_filename}")
                
                # Notify all clients that a new image was uploaded
                self.notify_all_clients_image_uploaded(png_filename, session.get('session_id'))
                
                return jsonify({
                    'message': 'Image uploaded successfully',
                    'filename': png_filename
                })
            
            except Exception as e:
                self.logger.error(f"Error uploading image: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        # Extra feature: Image deletion
        @self.app.route('/delete-image/<filename>', methods=['DELETE'])
        @self.session_required
        def delete_image(filename):
            try:
                image_path = os.path.join(self.images_dir, filename)
                
                # Check if file exists
                if not os.path.exists(image_path):
                    self.logger.warning(f"Session {session.get('session_id')} attempted to delete non-existent image: {filename}")
                    return jsonify({'error': 'Image not found'}), 404
                
                # Delete the file
                os.remove(image_path)
                
                self.logger.info(f"Session {session.get('session_id')} deleted image: {filename}")
                
                # Notify all clients that an image was deleted
                self.notify_all_clients_image_deleted(filename, session.get('session_id'))
                
                return jsonify({'message': f'Image {filename} deleted successfully'})
            
            except Exception as e:
                self.logger.error(f"Error deleting image {filename}: {str(e)}")
                return jsonify({'error': str(e)}), 500

    def setup_socketio(self):
        """Setup Socket.IO event handlers"""
        @self.socketio.on('connect')
        def handle_connect():
            client_sid = request.sid
            self.logger.info(f"Client connected via WebSocket: {client_sid}")
            
            # Associate session ID with socket ID if available
            if 'session_id' in session:
                session_id = session['session_id']
                with self.session_lock:
                    if session_id in self.active_sessions:
                        self.active_sessions[session_id]['socket_id'] = client_sid
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_sid = request.sid
            self.logger.info(f"Client disconnected from WebSocket: {client_sid}")
            
            # Find and update the session that used this socket
            with self.session_lock:
                for session_id, session_data in self.active_sessions.items():
                    if session_data.get('socket_id') == client_sid:
                        session_data.pop('socket_id', None)
                        self.logger.info(f"Removed socket association for session: {session_id}")
            
        @self.socketio.on('client_heartbeat')
        def handle_heartbeat(data):
            # Update session activity time on heartbeat
            if 'session_id' in session:
                session_id = session['session_id']
                with self.session_lock:
                    if session_id in self.active_sessions:
                        self.active_sessions[session_id]['last_activity'] = datetime.datetime.now()
                        self.logger.debug(f"Heartbeat from session: {session_id}")
                
    def notify_all_clients_image_uploaded(self, filename, uploader_session_id):
        """Notify all connected clients that a new image was uploaded"""
        notification = {
            'type': 'image_uploaded',
            'filename': filename,
            'uploaded_by': uploader_session_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.socketio.emit('server_notification', notification)
    
    def notify_all_clients_image_deleted(self, filename, deleter_session_id):
        """Notify all connected clients that an image was deleted"""
        notification = {
            'type': 'image_deleted',
            'filename': filename,
            'deleted_by': deleter_session_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.socketio.emit('server_notification', notification)
    
    def notify_all_clients_image_viewed(self, filename, viewer_session_id):
        """Notify all connected clients that an image was viewed"""
        notification = {
            'type': 'image_viewed',
            'filename': filename,
            'viewed_by': viewer_session_id,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.socketio.emit('server_notification', notification)
    
    def notify_all_clients_session_update(self):
        """Notify all connected clients about session updates"""
        with self.session_lock:
            active_count = len(self.active_sessions)
        
        notification = {
            'type': 'session_update',
            'active_count': active_count,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.socketio.emit('server_notification', notification)
    
    def clean_inactive_sessions(self):
        """Clean up inactive sessions (runs periodically)"""
        threshold = datetime.datetime.now() - datetime.timedelta(minutes=30)
        removed_count = 0
        
        with self.session_lock:
            inactive_sessions = []
            for session_id, session_data in self.active_sessions.items():
                if session_data['last_activity'] < threshold:
                    inactive_sessions.append(session_id)
            
            for session_id in inactive_sessions:
                del self.active_sessions[session_id]
                if session_id in self.client_activities:
                    del self.client_activities[session_id]
                removed_count += 1
        
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} inactive sessions")
            self.notify_all_clients_session_update()
    
    def session_cleanup_scheduler(self):
        """Background thread to periodically clean up inactive sessions"""
        while True:
            self.clean_inactive_sessions()
            time.sleep(300)  # Run every 5 minutes
    
    def convert_images_to_png(self):
        """Convert all images in the images directory to PNG format"""
        try:
            # Get all files in the images directory
            files = [f for f in os.listdir(self.images_dir) if os.path.isfile(os.path.join(self.images_dir, f))]
            
            for file in files:
                file_path = os.path.join(self.images_dir, file)
                
                # Skip PNG files
                if file.lower().endswith('.png'):
                    continue
                
                try:
                    # Open the image
                    with Image.open(file_path) as img:
                        # Create PNG filename
                        png_filename = os.path.splitext(file)[0] + '.png'
                        png_path = os.path.join(self.images_dir, png_filename)
                        
                        # Save as PNG
                        img.save(png_path, 'PNG')
                    
                    # Delete original file
                    os.remove(file_path)
                    self.logger.info(f"Converted {file} to {png_filename}")
                
                except Exception as e:
                    self.logger.error(f"Failed to convert {file}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error converting images to PNG: {e}")
    def clear_property_labels(self):
        self.format_label['text'] = "Format: "
        self.size_label['text'] = "Size: "
        self.mode_label['text'] = "Mode: "
        self.date_label['text'] = "Date Modified: "
        
    def on_image_selected(self, event=None):
        selected_image = self.image_var.get()
        if selected_image:
            #self.delete_button['state'] = tk.NORMAL
            #self.download_button['state'] = tk.NORMAL  # Enable download
            self.fetch_and_display_image(selected_image)
    def run(self):
        """Run the server"""
        # Convert existing images to PNG
        self.convert_images_to_png()
        
        # Start session cleanup thread
        cleanup_thread = threading.Thread(target=self.session_cleanup_scheduler)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        # Log server startup
        self.logger.info(f"Starting Image Server on {self.host}:{self.port}")
        
        # Start the Flask app with Socket.IO
        self.socketio.run(self.app, host=self.host, port=self.port, debug=True, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    server = ImageServer()
    server.run()
