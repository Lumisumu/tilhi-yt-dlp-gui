import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
import string
import random
import threading as th

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

        start_timestamp = start_hours_field.get() + ":" + start_minutes_field.get() + ":" + start_seconds_field.get()
        end_timestamp = end_hours_field.get() + ":" + end_minutes_field.get() + ":" + end_seconds_field.get()

        file_name = subprocess.getoutput('yt-dlp --print filename ' + url_field.get())
        file_name = file_name.replace("WARNING: [generic] Falling back on generic information extractor", "")
        file_name = ''.join(file_name.splitlines())

        if end_timestamp != "::":
            download_and_clip(start_timestamp, end_timestamp)

            if checkbox_keep_original.get() == "On":
                os.remove(file_name)
        else:
            thread = th.Thread(target=normal_download)
            thread.start()

        status_text.set("Download started for: " + file_name)

    else:
        status_text.set("Error: url field is empty.")

def normal_download():
    # Download video with yt-dlp
    command = 'yt-dlp ' + url_field.get()
    subprocess.run(command, shell=True)

def download_and_clip(start, end):
    thread = th.Thread(target=normal_download)
    thread.start()

    # Get video file name
    file_name = subprocess.getoutput('yt-dlp --print filename ' + url_field.get())
    file_name = file_name.replace("WARNING: [generic] Falling back on generic information extractor", "")
    file_name = ''.join(file_name.splitlines())

    # Cut video with ffmpeg
    cutter = 'ffmpeg -ss ' + start + ' -to ' + end + ' -i "' + file_name + '" -c copy clip.webm'
    subprocess.run(cutter, shell=True)

def update_ytdlp():
    subprocess.run("yt-dlp --update", shell=True)
    status_text.set("yt-dlp updated.")

# Create window, set size and window title
window = tk.Tk()
window.title("Tilhi - yt-dlp GUI")
window.geometry("950x600")
window.iconbitmap("tilhi-icon.ico")

# Choose one of the three cover images at random
random_number = random.randint(1, 3)
image_name = "cover-images/cover" + str(random_number) + ".jpg"
image_original = Image.open(image_name)
image_ratio = image_original.size[0] / image_original.size[1]
image_tk = ImageTk.PhotoImage(image_original)

# Storing variables
checkbox_keep_original = tk.StringVar(value="Off")
start_timestamp = "00:00:00"
end_timestamp = "00:00:00"
status_text = tk.StringVar()
status_text.set("Input url and press Start to download.")

### GRIDS ###

# Main grid that slips window into two parts
window.columnconfigure(0, weight = 3)
window.columnconfigure(1, weight = 1)
window.rowconfigure(0, weight = 1)

# Grid that holds the content area
side_frame = tk.Frame(window)
side_frame.grid(row=0, column=1, sticky="nsew")
side_frame.columnconfigure(0, weight=1)
side_frame.rowconfigure(0, weight=1)
side_frame.rowconfigure(1, weight=1)
side_frame.rowconfigure(2, weight=1)
side_frame.rowconfigure(3, weight=1)
side_frame.rowconfigure(4, weight=1)

# 1st content frame: file settings
file_info_frame = tk.Frame(side_frame)
file_info_frame.grid(row=1, column=0, sticky="nsew")
file_info_frame.columnconfigure(0, weight=1)
file_info_frame.columnconfigure(1, weight=3)
file_info_frame.columnconfigure(2, weight=1)
file_info_frame.rowconfigure(0, weight=1)

# 2nd content frame: timestamps
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

# 3rd content frame: buttons
buttons_frame = tk.Frame(side_frame)
buttons_frame.grid(row=4, column=0, sticky="nsew")
buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=3)
buttons_frame.columnconfigure(2, weight=1)
buttons_frame.rowconfigure(0, weight=1)

### CONTENT ###

# Content, left side: decoration image
canvas = tk.Canvas(window, background="red", bd=0, highlightthickness=0, width=40)
canvas.grid(row=0, column=0, sticky="nsew")
canvas.bind("<Configure>", resize_image)

# Content section 1: download url field
url_label = tk.Label(file_info_frame, text="Download url:", font=('Arial', 15), height = 1)
url_label.grid(row=0, column=0, sticky="e")
url_field = tk.Entry(file_info_frame)
url_field.grid(row=0, column=1, sticky="ew", padx=20)

# Content section 2: clips text
clips_label = tk.Label(timestamps_frame, text="Cut a clip", font=('Arial', 15), height = 1)
clips_label.grid(row=0, column=0, sticky="e")

# Clip section 2: clip start timestamp fields
start_timestamp_label = tk.Label(timestamps_frame, text="Start timestamp:", font=('Arial', 15), height = 1)
start_timestamp_label.grid(row=1, column=0, sticky="e")
start_hours_field = tk.Entry(timestamps_frame, justify="center")
start_hours_field.grid(row=1, column=1, padx=20)
start_first_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1)
start_first_middle_label.grid(row=1, column=2)
start_minutes_field = tk.Entry(timestamps_frame, justify="center")
start_minutes_field.grid(row=1, column=3, padx=20)
start_second_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1)
start_second_middle_label.grid(row=1, column=4, sticky="ew")
start_seconds_field = tk.Entry(timestamps_frame, justify="center")
start_seconds_field.grid(row=1, column=5, padx=20)

# Clip section 2: clip end timestamp fields
end_timestamp_label = tk.Label(timestamps_frame, text="End timestamp:", font=('Arial', 15), height = 1)
end_timestamp_label.grid(row=2, column=0, sticky="e")
end_hours_field = tk.Entry(timestamps_frame, justify="center")
end_hours_field.grid(row=2, column=1, padx=20)
end_first_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1)
end_first_middle_label.grid(row=2, column=2)
end_minutes_field = tk.Entry(timestamps_frame, justify="center")
end_minutes_field.grid(row=2, column=3, padx=20)
end_second_middle_label = tk.Label(timestamps_frame, text=":", font=('Arial', 15), height = 1)
end_second_middle_label.grid(row=2, column=4)
end_seconds_field = tk.Entry(timestamps_frame, justify="center")
end_seconds_field.grid(row=2, column=5, padx=20)

# Clip section 2: keep original video
keep_original_checkbutton = tk.Checkbutton(timestamps_frame, text="Delete full video", font=('Arial', 13), variable=checkbox_keep_original, onvalue="On", offvalue="Off")
keep_original_checkbutton.grid(row=3, column=1, sticky="ew", padx=15)

# Button to update yt-dlp
ytdlp_update_button = tk.Button(buttons_frame, text="Update yt-dlp", font=('Arial', 13), command=update_ytdlp, height = 1, width = 13)
ytdlp_update_button.grid(row=0, column=0, sticky="e", padx=30, pady=30)

# Status text for guiding user
status_label = tk.Label(buttons_frame, textvariable=status_text, font=('Arial', 13), wraplength=300, width=30, anchor="w")
status_label.grid(row=0, column=1, sticky="w")

# Button to start download
start_button = tk.Button(buttons_frame, text="Start Download", font=('Arial', 15), command=start_download, height = 1, width = 15)
start_button.grid(row=0, column=2, sticky="e", padx=30, pady=30)

# Start process
window.mainloop()