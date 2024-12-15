import streamlit as st
from PIL import Image
import subprocess
import os
import zipfile
import json
from io import BytesIO

# File to store user credentials
USER_FILE = "users.json"

# Load User Data
def load_users():
    if not os.path.exists(USER_FILE):
        return {"admin": "admin123"}
    with open(USER_FILE, "r") as file:
        return json.load(file)

# Save User Data
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

# Initialize Session State
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'admin' not in st.session_state:
    st.session_state['admin'] = False
if 'user_passwords' not in st.session_state:
    st.session_state['user_passwords'] = load_users()

# Authentication Functions
def authenticate(username, password):
    users = st.session_state['user_passwords']
    if username in users and users[username] == password:
        st.session_state['authenticated'] = True
        st.session_state['current_user'] = username
        st.session_state['admin'] = username == "admin"
        st.success(f"Welcome, {username}!")
        st.rerun()
    else:
        st.error("Invalid Username or Password!")

# Add User Function
def add_user(new_username, new_password):
    if new_username and new_password:
        st.session_state['user_passwords'][new_username] = new_password
        save_users(st.session_state['user_passwords'])
        st.success(f"User '{new_username}' added successfully!")
    else:
        st.error("Username and password cannot be empty!")

# Delete User Function
def delete_user(username_to_delete):
    if username_to_delete in st.session_state['user_passwords']:
        del st.session_state['user_passwords'][username_to_delete]
        save_users(st.session_state['user_passwords'])
        st.success(f"User '{username_to_delete}' deleted successfully!")
    else:
        st.error("User not found!")

# Logout Function
def logout():
    st.session_state['authenticated'] = False
    st.session_state['admin'] = False
    st.session_state['current_user'] = None
    st.query_params.update(logout="true")

# Lock Screen UI
if not st.session_state['authenticated']:
    st.markdown("""
        <style>
            .lockscreen {
                text-align: center;
                background-color: #0079b1;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #0079b1;
            }
        </style>
        <div class="lockscreen">
            <h1>🔒 Secure Login</h1>
            <p>Enter your credentials to access the application.</p>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Enter Username", key="username_input")
    password = st.text_input("Enter Password", type="password", key="password_input")

    if st.button("Login"):
        authenticate(username, password)
        st.experimental_set_query_params(logout="false")
    st.stop()

# Admin Panel
if st.session_state['admin']:
    st.sidebar.title("⚙️ Admin Panel")
    st.sidebar.subheader("Manage Users")

    # Add New User
    new_username = st.sidebar.text_input("New Username")
    new_password = st.sidebar.text_input("New Password", type="password")
    if st.sidebar.button("Add User"):
        add_user(new_username, new_password)

    # Delete User
    username_to_delete = st.sidebar.text_input("Username to Delete")
    if st.sidebar.button("Delete User"):
        delete_user(username_to_delete)

    st.sidebar.write("### Current Users")
    st.sidebar.table({"Username": list(st.session_state['user_passwords'].keys())})

# Logout Button
st.sidebar.button("🚪 Logout", on_click=logout)

# Reset Button (Admin Only)
if st.session_state['admin']:
    if st.sidebar.button("🔄 Reset App"):
        os.remove(USER_FILE)
        st.success("App reset successfully. Restarting...")
        st.rerun()

# Welcome Message
st.title(f"Welcome, {st.session_state['current_user']} 👋")
st.write("Advanced Image and Video Compressor")

# Helper Function: Compress Single Image
def compress_image(input_path, output_path, quality=75, resize=False, width=None, height=None):
    try:
        before_size = os.path.getsize(input_path) // 1024  # Size in KB
        with Image.open(input_path) as img:
            if resize and width and height:
                img = img.resize((width, height))
            img = img.convert("RGB")
            img.save(output_path, format="JPEG", optimize=True, quality=quality)
        after_size = os.path.getsize(output_path) // 1024
        return before_size, after_size
    except Exception as e:
        st.error(f"Error compressing image: {e}")
        return None, None

# Helper Function: Compress Single Video
def compress_video(input_path, output_path, crf=23, resolution=None, bitrate=None):
    ffmpeg_path = r"C:\Users\HP\Desktop\imgvid\ffmpeg-7.1-full_build\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
    try:
        before_size = os.path.getsize(input_path) // 1024  # Size in KB

        # FFmpeg compression command
        command = [ffmpeg_path, "-y", "-i", input_path, "-vcodec", "libx264", "-crf", str(crf)]

        # Add resolution and bitrate options
        if resolution:
            command += ["-vf", f"scale={resolution}"]
        if bitrate:
            command += ["-b:v", bitrate]

        command.append(output_path)

        subprocess.run(command, capture_output=True, text=True, check=True)
        after_size = os.path.getsize(output_path) // 1024
        return before_size, after_size
    except subprocess.CalledProcessError as e:
        st.error(f"FFmpeg Error: {e.stderr}")
        return None, None

# Helper Function: Create ZIP File
def create_zip(file_paths):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for file_path in file_paths:
            zf.write(file_path, os.path.basename(file_path))
    return zip_buffer

# Streamlit UI
st.title("Advanced Image and Video Compressor")
st.write("Upload your files, adjust settings, and compress.")

# Sidebar Options
compression_quality = st.sidebar.slider("Compression Quality", 10, 100, 75)
resize_image = st.sidebar.checkbox("Resize Images")
custom_width = st.sidebar.number_input("Width (px)", min_value=100, step=50, value=800)
custom_height = st.sidebar.number_input("Height (px)", min_value=100, step=50, value=600)
resolution_option = st.sidebar.selectbox("Video Resolution", ["None", "1920x1080", "1280x720", "640x480"])
bitrate_option = st.sidebar.text_input("Video Bitrate (e.g., 1000k)", "")

compression_type = st.sidebar.radio("Select Compression Type", ["Images", "Videos"])

# Drag and Drop File Upload
uploaded_files = st.file_uploader("Drag and Drop or Browse Files", 
                                  type=["jpg", "jpeg", "png", "mp4", "avi"], 
                                  accept_multiple_files=True)

# Process Uploaded Files
if uploaded_files:
    st.write("### Uploaded Files:")
    file_paths = []
    for uploaded_file in uploaded_files:
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(temp_path)
        st.write(f"✅ {uploaded_file.name}")

    output_files = []
    size_data = []
    progress_bar = st.progress(0)

    if st.button("Compress Files"):
        total_files = len(file_paths)
        for idx, file_path in enumerate(file_paths):
            file_ext = os.path.splitext(file_path)[1].lower()
            output_path = f"compressed_{os.path.basename(file_path)}"
            before_size, after_size = None, None

            # Image Compression
            if file_ext in [".jpg", ".jpeg", ".png"]:
                before_size, after_size = compress_image(
                    file_path, output_path, quality=compression_quality,
                    resize=resize_image, width=custom_width, height=custom_height
                )
            # Video Compression
            elif file_ext in [".mp4", ".avi"]:
                before_size, after_size = compress_video(
                    file_path, output_path, crf=23, resolution=resolution_option if resolution_option != "None" else None,
                    bitrate=bitrate_option if bitrate_option else None
                )
            else:
                st.warning(f"Unsupported file format: {file_path}")
                continue

            if before_size and after_size:
                size_data.append([os.path.basename(file_path), before_size, after_size, round((before_size - after_size) / before_size * 100, 2)])
                output_files.append(output_path)

            # Update progress
            progress_bar.progress((idx + 1) / total_files)

        # Show Size Comparison Table
        if size_data:
            st.write("### Before and After Size Comparison:")
            st.table({"File Name": [row[0] for row in size_data],
                      "Before Size (KB)": [row[1] for row in size_data],
                      "After Size (KB)": [row[2] for row in size_data],
                      "Saved (%)": [row[3] for row in size_data]})

        # ZIP and Download
        if output_files:
            zip_buffer = create_zip(output_files)
            st.download_button("Download All as ZIP", data=zip_buffer.getvalue(), file_name="compressed_files.zip", mime="application/zip")
