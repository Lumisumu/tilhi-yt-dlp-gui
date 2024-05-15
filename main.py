import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess
import string
import random
import threading as th
import glob
import time
import datetime

def resize_image(event):
    global resized_tk

    # Get canvas ratio
    canvas_ratio = event.width / event.height
    
    # Check if the canvas is wider than the image
    if canvas_ratio > image_ratio:
        width = int(event.width)
        height = int(width / image_ratio)
    else:
        height = int(event.height)
        width = int(height * image_ratio)

    # Resize
    resized_image = image_original.resize((width, height))
    resized_tk = ImageTk.PhotoImage(resized_image)
    canvas.create_image(int(event.width / 2), int(event.height / 2), anchor="center", image=resized_tk)

def start_download():
    if url_field.get() != "":

        # Set full video save location
        if full_video_folder_field.get() != "":
            video_target_folder = full_video_folder_field.get()
        else:
            video_target_folder = "full-videos"

        # Set clip save location
        if clip_folder_field.get() != "":
            clip_target_folder = clip_folder_field.get()
        else:
            clip_target_folder = "clips"

        # If folder does not exist yet, create it before downloading
        if not os.path.exists(video_target_folder):
            os.makedirs(video_target_folder)

        # Create yt-dlp command to download the video
        if checkbox_only_audio.get() == "On":
            command = 'yt-dlp -P ' + video_target_folder + " -f 140 " + url_field.get()
        else:
            command = 'yt-dlp -P ' + video_target_folder + " " + url_field.get()      

        # Arrays for timestamp editing
        timestamp_numbers = []
        timestamp_numbers.extend([start_hours_field.get(), start_minutes_field.get(), start_seconds_field.get(), end_hours_field.get(), end_minutes_field.get(), end_seconds_field.get()])

        # If end timestamp fields have any entries, make a clip. Otherwise only download.
        if timestamp_numbers[3] != "" or timestamp_numbers[4] != "" or timestamp_numbers[5] != "":
            edited_timestamps = []

            # If folder does not exist yet, create it before downloading
            if not os.path.exists(clip_target_folder):
                os.makedirs(clip_target_folder)

            for i in range(len(timestamp_numbers)):
                if not timestamp_numbers[i]:
                    # If the item is empty, replace it with "hello"
                    timestamp_numbers[i] = "00"

            # Handle timestamps to proper format
            for s in timestamp_numbers:
                # Trim to only two first numbers
                if len(s) > 2:
                    new_string = s[:2]
                # Add missing number if only one number
                elif len(s) == 1:
                    new_string = '0' + s
                else:
                    new_string = s

                edited_timestamps.append(new_string)

            # Timestamp field into one string
            start_timestamp = edited_timestamps[0] + ":" + edited_timestamps[1] + ":" + edited_timestamps[2]
            end_timestamp = edited_timestamps[3] + ":" + edited_timestamps[4] + ":" + edited_timestamps[5]

            # Start download
            subprocess.run(command, shell=True)

            # Get latest file name
            file_location = video_target_folder + "/*"
            list_of_files = glob.glob(file_location)
            file_name = max(list_of_files, key=os.path.getctime)

            # Remove folder name and "\" from the string to get only the video file name
            file_name = file_name.replace("\\", "")
            file_name = file_name.replace(video_target_folder, "")

            ts = time.time()
            date_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S-%f')
            date_string = date_string.replace(':', '-')

            # If user wants audio only, replace file extension
            if checkbox_only_audio.get() == "On":
                new_file_name = file_name.replace('.m4a', '')
                cutter = 'ffmpeg -ss ' + start_timestamp + ' -to ' + end_timestamp + ' -i "' + video_target_folder + "/" + file_name + '" -c copy "' + clip_target_folder + '/' + file_name + " - clip " + date_string + '.m4a"'
            else:
                new_file_name = file_name.replace('.webm', '')
                cutter = 'ffmpeg -ss ' + start_timestamp + ' -to ' + end_timestamp + ' -i "' + video_target_folder + "/" + file_name + '" -c copy "' + clip_target_folder + '/' + file_name + " - clip " + date_string + '.webm"'
            
            # Run the ffmpeg command
            subprocess.run(cutter, shell=True)

            # Remove original full video file if user wants it deleted
            if checkbox_keep_original.get() == "On":
                string = video_target_folder + "/" + file_name
                os.remove(string)

        else:
            # Only download video
            subprocess.run(command, shell=True)

            # Get latest file name
            file_location = video_target_folder + "/*"
            list_of_files = glob.glob(file_location)
            file_name = max(list_of_files, key=os.path.getctime)

        status_text.set("Download finished: " + file_name)

    else:
        status_text.set("Error: url field is empty.")

def update_ytdlp():
    result = subprocess.run("yt-dlp --update", stdout=subprocess.PIPE, text=True, shell=True)
    output_lines = result.stdout.split('\n')
    last_line = next((line for line in reversed(output_lines) if line), "")
    status_text.set(last_line)

# Create window, set size and window title
window = tk.Tk()
window.title("Tilhi - yt-dlp GUI")
window.geometry("1000x600")
window.iconbitmap("res/tilhi-icon.ico")

# Choose one of the three cover images at random
random_number = random.randint(1, 3)
image_name = "res/cover" + str(random_number) + ".jpg"
image_original = Image.open(image_name)
image_ratio = image_original.size[0] / image_original.size[1]
image_tk = ImageTk.PhotoImage(image_original)

# Status text variable
status_text = tk.StringVar()
status_text.set("Input url and press Start to download.")

# User selections
video_target_folder = "full-videos"
clip_target_folder = "clips"
start_timestamp = "00:00:00"
end_timestamp = "00:00:00"
checkbox_keep_original = tk.StringVar(value="Off")
checkbox_only_audio = tk.StringVar(value="Off")

# Main grid that slips window into two parts
window.columnconfigure(0, weight = 3)
window.columnconfigure(1, weight = 1)
window.rowconfigure(0, weight = 1)

# Decoration image on the left side of the window
canvas = tk.Canvas(window, background="red", bd=0, highlightthickness=0, width=40)
canvas.grid(row=0, column=0, sticky="nsew")
canvas.bind("<Configure>", resize_image)

# Grid for widgets on the right side of the window
side_frame = tk.Frame(window)
side_frame.grid(row=0, column=1, sticky="nsew")
side_frame.columnconfigure(0, weight=1)
side_frame.rowconfigure(0, weight=1)
side_frame.rowconfigure(1, weight=1)
side_frame.rowconfigure(2, weight=1)
side_frame.rowconfigure(3, weight=1)
side_frame.rowconfigure(4, weight=1)
side_frame.rowconfigure(5, weight=1)

# Grid for file settings
file_info_frame = tk.Frame(side_frame)
file_info_frame.grid(row=1, column=0, sticky="nsew")
file_info_frame.columnconfigure(0, weight=1)
file_info_frame.columnconfigure(1, weight=3)
file_info_frame.columnconfigure(2, weight=1)
file_info_frame.rowconfigure(0, weight=3)
file_info_frame.rowconfigure(1, weight=3)
file_info_frame.rowconfigure(2, weight=3)
file_info_frame.rowconfigure(3, weight=1)
file_info_frame.rowconfigure(4, weight=1)

# Url field
url_label = tk.Label(file_info_frame, text="Download url:*", font=('Arial', 15), height = 1).grid(row=0, column=0, sticky="e")
url_field = tk.Entry(file_info_frame).grid(row=0, column=1, sticky="ew", padx=20)

# Only-audio checkbox
only_audio_checkbutton = tk.Checkbutton(file_info_frame, text="Download only audio track",  font=('Arial', 13), variable=checkbox_only_audio, onvalue="On", offvalue="Off").grid(row=1, column=1, sticky="w", padx=15)

# Video save location field
full_video_folder_label = tk.Label(file_info_frame, text="Full video save location:", wraplength=200, font=('Arial', 15), height = 2).grid(row=2, column=0, sticky="e")
full_video_folder_field = tk.Entry(file_info_frame).grid(row=2, column=1, sticky="ew", padx=20)

# Clip save location field
clip_folder_label = tk.Label(file_info_frame, text="Clip save location:", wraplength=200, font=('Arial', 15), height = 2).grid(row=3, column=0, sticky="e")
clip_folder_field = tk.Entry(file_info_frame).grid(row=3, column=1, sticky="ew", padx=20)

# File location notes label
folder_tips_label = tk.Label(file_info_frame, text='Default folders are named "full-videos" and "clips".', font=('Arial', 11), height = 1).grid(row=4, column=1, sticky="w", padx=20)

# Separator
separator1 = ttk.Separator(side_frame, orient="horizontal").grid(row=2, column=0, columnspan=1, sticky="news", padx=30, pady=20)

# Grid for timestamps
timestamps_frame = tk.Frame(side_frame)
timestamps_frame.grid(row=3, column=0, sticky="nsew")
timestamps_frame.columnconfigure(0, weight=1)
timestamps_frame.columnconfigure(1, weight=1)
timestamps_frame.columnconfigure(2, weight=1)
timestamps_frame.columnconfigure(3, weight=1)
timestamps_frame.columnconfigure(4, weight=1)
timestamps_frame.columnconfigure(5, weight=1)
timestamps_frame.rowconfigure(0, weight=3)
timestamps_frame.rowconfigure(1, weight=1)
timestamps_frame.rowconfigure(2, weight=1)
timestamps_frame.rowconfigure(3, weight=1)

# Clips title label
clips_label = tk.Label(timestamps_frame, text="Cut a clip", font=('Arial', 15), height = 1).grid(row=0, column=0, sticky="e")

# Clip start timestamp labels and fields
start_timestamp_label = tk.Label(timestamps_frame, text="Start timestamp:", font=('Arial', 15), height = 1).grid(row=1, column=0, sticky="e")
start_hours_field = tk.Entry(timestamps_frame, justify="center").grid(row=1, column=1, padx=20)
start_first_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1).grid(row=1, column=2)
start_minutes_field = tk.Entry(timestamps_frame, justify="center").grid(row=1, column=3, padx=20)
start_second_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1).grid(row=1, column=4, sticky="ew")
start_seconds_field = tk.Entry(timestamps_frame, justify="center").grid(row=1, column=5, padx=20)

# Clip end timestamp labels and fields
end_timestamp_label = tk.Label(timestamps_frame, text="End timestamp:", font=('Arial', 15), height = 1).grid(row=2, column=0, sticky="e")
end_hours_field = tk.Entry(timestamps_frame, justify="center").grid(row=2, column=1, padx=20)
end_first_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1).grid(row=2, column=2)
end_minutes_field = tk.Entry(timestamps_frame, justify="center").grid(row=2, column=3, padx=20)
end_second_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1).grid(row=2, column=4)
end_seconds_field = tk.Entry(timestamps_frame, justify="center").grid(row=2, column=5, padx=20)

# Keep-original checkbox
keep_original_checkbutton = tk.Checkbutton(timestamps_frame, text="Delete full video", font=('Arial', 13), variable=checkbox_keep_original, onvalue="On", offvalue="Off").grid(row=3, column=1, sticky="ew", padx=15)

# Separator
separator2 = ttk.Separator(side_frame, orient="horizontal").grid(row=4, column=0, columnspan=1, sticky="news", padx=30, pady=20)

# Grid for buttons
buttons_frame = tk.Frame(side_frame)
buttons_frame.grid(row=5, column=0, sticky="nsew")
buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=3)
buttons_frame.columnconfigure(2, weight=1)
buttons_frame.rowconfigure(0, weight=1)

# Button to update yt-dlp
ytdlp_update_button = tk.Button(buttons_frame, text="Update yt-dlp", font=('Arial', 13), command=update_ytdlp, height = 1, width = 13).grid(row=0, column=0, sticky="e", padx=30, pady=10)

# Status text for guiding user
status_label = tk.Label(buttons_frame, textvariable=status_text, font=('Arial', 13), wraplength=300, width=30, anchor="w").grid(row=0, column=1, sticky="w")

# Button to start download
start_button = tk.Button(buttons_frame, text="Start Download", font=('Arial', 15), command=lambda: th.Thread(target=start_download).start(), height = 1, width = 15).grid(row=0, column=2, sticky="e", padx=30, pady=10)

# Grid for notes
notes_frame = tk.Frame(side_frame)
notes_frame.grid(row=6, column=0, sticky="nsew")
notes_frame.columnconfigure(0, weight=1)
notes_frame.columnconfigure(1, weight=1)

# Required fields label
required_label = tk.Label(notes_frame, text="* = Required field", font=('Arial', 11), wraplength=300, width=30, anchor="w").grid(row=5, column=0, sticky="w", padx=25, pady=5)

# Version number label
version_label = tk.Label(notes_frame, text="Version 1.1", font=('Arial', 11), wraplength=300, width=30, anchor="e").grid(row=5, column=1, sticky="e", padx=25, pady=5)

# Start process
window.mainloop()