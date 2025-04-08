import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
from pathlib import Path
import os
import subprocess
import string
import random
import threading as th
import glob
import time
import datetime
import pyperclip

# Set working directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Show messages on the right side of the window
def show_message(message: str, color: str):
    status_text.set(message)
    status_label.configure(fg=color)

# Send update command to yt-dlp and show resulting line
def update_ytdlp():
    result = subprocess.run("yt-dlp --update", stdout=subprocess.PIPE, text=True, shell=True)
    show_message(next((line for line in reversed(result.stdout.split('\n')) if line), ""), "black")

# Open the target save location
def open_folder():
    target_folder = full_video_folder_field.get()

    if target_folder != "":
            path = target_folder
            os.startfile(path)
    else:
        path = Path.cwd()
        os.startfile(path)

# Open window for folder selection
def open_location_select(type: str):
    selected_folder = askdirectory()

    if type == "full":
        full_video_folder_field.delete(0, tk.END)
        full_video_folder_field.insert(0, selected_folder)
    
    elif type == "clips":
        clip_folder_field.delete(0, tk.END)
        clip_folder_field.insert(0, selected_folder)

# Reset fields to default settings
def clear_fields():
    text_fields = [url_field, rename_field, full_video_folder_field, clip_folder_field, start_hours_field, start_minutes_field, start_seconds_field, end_hours_field, end_minutes_field, end_seconds_field]

    for item in text_fields:
        item.delete(0, 'end')

    only_audio_checkbox.set(0)

# Copy text to system clipboard
def copy_to_clipboard(type, command):
    text = str(command[0])
    pyperclip.copy(text)

    if type == "full":
        show_message("yt-dlp command copied to clipboard.", "black")
    else:
        show_message("FFMPEG command copied to clipboard.", "black")


# Open context menu when user right-clicks on a text field, allows user to cut, copy and paste text
class context_menu:
    def __init__(self, e):
        options = ["Cut", "Copy", "Paste"]
        dropdown = tk.Menu(None, tearoff=0, takefocus=0)

        for txt in options:
            dropdown.add_command(label=txt, command=lambda e=e, txt=txt:self. select_option(e, txt))

        dropdown.tk_popup(e.x_root + 00, e.y_root + 5, entry="0")

    def select_option(self, e, cmd):
        e.widget.event_generate(f'<<{cmd}>>')

# If user presses Enter key when typing into url field, start download process
def press_enter(event):
    th.Thread(target=start_download).start()

# Resize decorative image when window rsize changes
def resize_image(event):
    global resized_tk
    canvas_ratio = event.width / event.height
    
    if canvas_ratio > image_ratio:
        width = int(event.width)
        height = int(width / image_ratio)
    else:
        height = int(event.height)
        width = int(height * image_ratio)

    resized_image = image_original.resize((width, height))
    resized_tk = ImageTk.PhotoImage(resized_image)
    canvas.create_image(int(event.width / 2), int(event.height / 2), anchor="center", image=resized_tk)

def create_video_folder(video_target_folder):
    if not os.path.exists(video_target_folder):
        os.makedirs(video_target_folder)

def create_clip_folder(clip_target_folder):
    if not os.path.exists(clip_target_folder):
        os.makedirs(clip_target_folder)

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = None
    result = None

    for line in process.stdout:
        print(line, end='')
        result = line.strip()

    if result:
        output = result

    process.wait()

    return output

# Get the name of the latest finished file and show message
def show_success_message(file_location):
    list_of_files = glob.glob(file_location)
    file_name = max(list_of_files, key=os.path.getctime)

    show_message(str("Download finished: " + file_name), "green")

def prepare_timestamps(timestamp_numbers, timestamps):
    start_timestamp = str(timestamp_numbers[0]) + ":" + str(timestamp_numbers[1]) + ":" + str(timestamp_numbers[2])
    end_timestamp = str(timestamp_numbers[3]) + ":" + str(timestamp_numbers[4]) + ":" + str(timestamp_numbers[5])

    starting_time: int
    starting_time = (int(timestamp_numbers[0]) * 3600) + (int(timestamp_numbers[1]) * 60) + int(timestamp_numbers[2])
    ending_time: int
    ending_time = (int(timestamp_numbers[3]) * 3600) + (int(timestamp_numbers[4]) * 60) + int(timestamp_numbers[5])

    timestamps = [starting_time, ending_time]
    return timestamps

# Main function that is called when Start Download button is pressed or Enter key is pressed in url field
def start_download():
    target_url = url_field.get().replace(" ", "")

    # If user has not typed into url field, do nothing
    if target_url == "":
        show_message("Error: Url field is empty.", "black")

    # Start download process
    else:
        show_message("Trying to gather settings...", "black")

        # Get user input from fields
        video_target_folder = full_video_folder_field.get()
        clip_target_folder = clip_folder_field.get()
        only_audio_selection = only_audio_checkbox.get()
        user_input_file_name = rename_field.get()
        file_name: str
        timestamp_numbers = [start_hours_field.get(), start_minutes_field.get(), start_seconds_field.get(), end_hours_field.get(), end_minutes_field.get(), end_seconds_field.get()]

        # Insert "0" if timestamp item is empty
        for entry in range(len(timestamp_numbers)):
            if not timestamp_numbers[entry]:
                # If the item is empty, replace it with 0
                timestamp_numbers[entry] = "0"

        # Flag to check if timestamps are used
        valid_timestamp = any(item != "0" for item in timestamp_numbers)

        # Prepare timestamps and clip folder for download
        if valid_timestamp == True:
            timestamps = []
            timestamps = prepare_timestamps(timestamp_numbers, timestamps)

            # Set clip save location
            if clip_target_folder == "":
                clip_target_folder = "clips"

            create_clip_folder(clip_target_folder)

        # Set video save location
        if video_target_folder == "":
            video_target_folder = "full-videos"
            file_location = "full-videos/*"
        else:
            file_location = video_target_folder + "/*"

        # Make download command for full video
        if only_audio_selection == "On":
            command = 'yt-dlp -P "' + video_target_folder + '" -f 140 ' + target_url
        else:
            command = 'yt-dlp -P "' + video_target_folder + '" ' + target_url

        # If user is using file rename field, add it to the command
        if user_input_file_name != "":
            command = command + str(' -o "' + user_input_file_name + '"')

        # Download only full videos with a user made list from "lists" folder
        if target_url[-3:] == "txt":
            show_message("Downloading multiple videos by using a txt file...", "black")
            link_list = "lists/" + target_url

            if os.path.exists(link_list):
                # Variables for reporting the results of list download
                already_done_downloads = 0
                finished_downloads = 0
                failed_downloads = 0
                unsure_downloads = 0
                failed_downloads_list = []
                unsure_downloads_list = []

                # Open text file
                f = open(link_list, "r")

                # Loops the times of lines in the text file
                for x in f:
                    current_video_url = (x.strip().replace(" ", ""))
                    print("Current download target url: " + current_video_url)

                    # Make download command for full video
                    if only_audio_selection == "On":
                        command = 'yt-dlp -P "' + video_target_folder + '" -f 140 ' + current_video_url
                    else:
                        command = 'yt-dlp -P "' + video_target_folder + '" ' + current_video_url

                    print("yt-dlp command: " + command)
                    output = run_command(command)

                    # If video has already been downloaded show 
                    if "has already been" in output:
                        print("That video has already been downloaded: " + current_video_url)
                        already_done_downloads += 1
                    elif "truncated" in output:
                        print("Incomplete link, check the url address for: " + current_video_url)
                        failed_downloads += 1
                        failed_downloads_list.append(current_video_url)
                    elif "Deleting original" in output or "Merging formats" in output or "100%" in output:
                        print("Download finished for: " + current_video_url)
                        finished_downloads += 1
                    else:
                        print("Confirm the results in cmd and target folder." + current_video_url)
                        unsure_downloads += 1
                        unsure_downloads_list.append(current_video_url)
                    
                    print("\n\n")

                # Show message that details the results of list download
                show_message("Downloading multiple videos finished, check the folder and command line message for results.", "green")
                print("\nLIST DOWNLOAD RESULTS:\n" + str(failed_downloads) + " failed downloads\n" + str(unsure_downloads) + " downloads where result cannot be parsed (usually successful)\n" + str(already_done_downloads) + " already downloaded videos (these are skipped)\n" + str(finished_downloads) + " successfully finished downloads.\n")
                if failed_downloads_list != []:
                    print("Failed downloads:")
                    print(failed_downloads_list)
                if unsure_downloads_list != []:
                    print("Unconfirmed results:")
                    print(unsure_downloads_list)

            else:
                show_message('Text file not found in "lists" folder, check file name and file extension.', "red")

        # Download only full video if user is not using timestamps
        elif valid_timestamp == False:
            show_message("Downloading...", "black")
            create_video_folder(video_target_folder)

            # Show the command and save it to variable for copying
            command_var[0] = command
            full_video_command_text.set(command)
            
            # Run command
            output = run_command(command)

            # If video has already been downloaded show 
            if "has already been" in output:
                show_message(str("That video has already been downloaded."), "green")
            elif "truncated" in output:
                show_message(str("Incomplete link, check the url address."), "red")
            elif "Deleting original" in output or "Merging formats" in output or "100%" in output:
                show_success_message(file_location)
            else:
                show_message(str("Confirm the results in cmd and target folder."), "black")

        # Download full video and then make a clip
        elif valid_timestamp == True:
            show_message("Downloading and cutting a clip...", "black")

            # Show the command as text for copying
            command_var[0] = command
            full_video_command_text.set(command)

            # Run command to download full video
            output = run_command(command)

            # Get latest file name
            list_of_files = glob.glob(file_location)
            latest_file_name = max(list_of_files, key=os.path.getctime).split("\\")[-1]
            new_file_name = latest_file_name.rsplit('.', 1)[0]

            ts = time.time()
            date_string = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S-%f')
            date_string = date_string.replace(':', '-')
            
            # Replace the target folder with clip target folder
            clip_command = command.replace(video_target_folder, clip_target_folder)
            clip_command = clip_command + ' --download-sections "*' + str(timestamps[0]) + '-' + str(timestamps[1]) + '"'

            # Make a new command
            cutter = 'ffmpeg -ss ' + str(timestamps[0]) + ' -to ' + str(timestamps[1]) + ' -i "' + video_target_folder + '/' + latest_file_name + '" -c copy "' + clip_target_folder + '/' + new_file_name + " - clip " + date_string

            # Add file extension name
            if only_audio_selection == "On":
                cutter = cutter + '.m4a"'
            else:
                cutter = cutter + '.mp4"'

            # Show the command as text for copying
            cutter_var[0] = cutter
            clip_command_text.set(cutter)

            # Run command to cut clip
            ffmpeg_cut = subprocess.Popen(cutter, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ffmpeg_cut.wait()

            # If video has already been downloaded show 
            if output and "has already been downloaded" in output[-1]: 
                show_message(str("That video has already been downloaded. Clip has been created."), "green")
            else:
                show_success_message(file_location)

# Create window
window = tk.Tk()
window.title("Tilhi yt-dlp GUI")
window.geometry("900x600")
window.iconbitmap("res/icon.ico")

# Decorative image
image_original = Image.open("res/cover.jpg")
image_ratio = image_original.size[0] / image_original.size[1]
image_tk = ImageTk.PhotoImage(image_original)

# Text variables
status_text = tk.StringVar()
status_text.set("Input video url and press Start to download.")
full_video_command_text = tk.StringVar()
full_video_command_text.set("(yt-dlp command)")
clip_command_text = tk.StringVar()
clip_command_text.set("(FFMPEG command)")

# yt-dlp and FFMPEG commands
command_var = [""]
cutter_var = [""]

# Main grid
window.columnconfigure(0, weight = 1)
window.columnconfigure(1, weight = 1)
window.rowconfigure(0, weight = 1)

# Right-side grid for input elements
r_frame = tk.Frame(window)
r_frame.grid(row=0, column=1, sticky="nsew")
r_frame.columnconfigure(0, weight=1)
r_frame.rowconfigure(0, weight=1)
r_frame.rowconfigure(1, weight=1)

# Left-side grid for visual elements
l_frame = tk.Frame(window)
l_frame.grid(row=0, column=0, sticky="nsew")
l_frame.columnconfigure(0, weight=1)
l_frame.rowconfigure(0, weight=1)
l_frame.rowconfigure(1, weight=1)
l_frame.rowconfigure(2, weight=1)
l_frame.rowconfigure(3, weight=1)
l_frame.rowconfigure(4, weight=1)
l_frame.rowconfigure(5, weight=1)

# Decoration image on the left side of the window
canvas = tk.Canvas(r_frame, background="grey", bd=0, highlightthickness=0, width=40, height=40)
canvas.grid(row=0, column=0, sticky="nsew")
canvas.bind("<Configure>", resize_image)

# Status text for guiding user
status_label = tk.Label(r_frame, textvariable=status_text, font=('Arial', 13), wraplength=300, width=40, height=1, fg="black")
status_label.grid(row=1, column=0, padx=0, sticky="news")

# Grid for file settings
file_info_frame = tk.Frame(l_frame)
file_info_frame.grid(row=0, column=0, sticky="nsew")
file_info_frame.columnconfigure(0, weight=1)
file_info_frame.columnconfigure(1, weight=1)
file_info_frame.columnconfigure(2, weight=1)
file_info_frame.columnconfigure(3, weight=1)
file_info_frame.rowconfigure(0, weight=10)
file_info_frame.rowconfigure(1, weight=1)
file_info_frame.rowconfigure(2, weight=1)
file_info_frame.rowconfigure(3, weight=1)
file_info_frame.rowconfigure(4, weight=1)
file_info_frame.rowconfigure(4, weight=1)
file_info_frame.rowconfigure(5, weight=1)

# Url field
url_label = tk.Label(file_info_frame, text="Video url:", font=('Arial', 13), height = 1).grid(row=1, column=0, sticky="e")
url_field = tk.Entry(file_info_frame, font=('Arial', 10), width=40)
url_field.grid(row=1, column=1, sticky="w", padx=5)
url_field.bind('<Return>', press_enter)
url_field.bind("<Button-3>", context_menu)
url_tip_button = tk.Button(file_info_frame, text="\u2753", font=('Arial', 13), height = 1, command=lambda: show_message('Url of video, playlist, channel or name of your own txt file.\n\nPlaylist/channel url downloads all videos.\n\nIf you want to use your own list for downloadable videos, create a txt file in the "lists" folder and write the file name (including the ".txt") into the url field. Example txt file is in the "lists" folder.', "black"))
url_tip_button.grid(row=1, column=3, sticky="w", padx=5)

# Only-audio checkbox
only_audio_checkbox = tk.StringVar(value="Off")
only_audio_checkbutton = tk.Checkbutton(file_info_frame, text="Download only audio track",  font=('Arial', 11), variable=only_audio_checkbox, onvalue="On", offvalue="Off").grid(row=2, column=1, sticky="w", padx=15)

# Rename field
rename_label = tk.Label(file_info_frame, text="Rename file:", wraplength=200, font=('Arial', 13), height = 2).grid(row=3, column=0, sticky="e")
rename_field = tk.Entry(file_info_frame, font=('Arial', 10), width=40)
rename_field.grid(row=3, column=1, sticky="w", padx=5)
rename_field.bind("<Button-3>", context_menu)
rename_tip_button = tk.Button(file_info_frame, text="\u2753", font=('Arial', 13), height = 1, command=lambda: show_message('Default name includes video title and id.\n\nRenaming is not possible for audio-only downloads.', "black"))
rename_tip_button.grid(row=3, column=3, sticky="w", padx=5)

# Video save location field
full_video_folder_label = tk.Label(file_info_frame, text="Video save folder:", wraplength=200, font=('Arial', 13), height = 2).grid(row=4, column=0, sticky="e")
full_video_folder_field = tk.Entry(file_info_frame, font=('Arial', 10), width=40)
full_video_folder_field.grid(row=4, column=1, sticky="w", padx=5)
full_video_folder_field.bind("<Button-3>", context_menu)
full_video_folder_select_button = tk.Button(file_info_frame, text="Select folder", font=('Arial', 13), height = 1, command=lambda: open_location_select("full"))
full_video_folder_select_button.grid(row=4, column=2, sticky="w", padx=5)
full_video_folder_tip_button = tk.Button(file_info_frame, text="\u2753", font=('Arial', 13), height = 1, command=lambda: show_message('Default save folder is "full-videos". It is created in the same folder where program is run.\n\nFolder name cannot include spaces or special symbols.', "black"))
full_video_folder_tip_button.grid(row=4, column=3, sticky="w", padx=5)

# Clip save location field
clip_folder_label = tk.Label(file_info_frame, text="Clip save folder:", wraplength=200, font=('Arial', 13), height = 2).grid(row=5, column=0, sticky="e")
clip_folder_field = tk.Entry(file_info_frame, font=('Arial', 10), width=40)
clip_folder_field.grid(row=5, column=1, sticky="w", padx=5)
clip_folder_field.bind("<Button-3>", context_menu)
full_video_folder_select_button = tk.Button(file_info_frame, text="Select folder", font=('Arial', 13), height = 1, command=lambda: open_location_select("clips"))
full_video_folder_select_button.grid(row=5, column=2, sticky="w", padx=5)
clip_tip_button = tk.Button(file_info_frame, text="\u2753", font=('Arial', 13), height = 1, command=lambda: show_message('Default save folder is "clips". It is created in the same folder where program is run.\n\nFolder name cannot include spaces or special symbols.', "black"))
clip_tip_button.grid(row=5, column=3, sticky="w", padx=5)

# Separator
separator1 = ttk.Separator(l_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, sticky="news", padx=30, pady=20)

# Grid for clips
clip_frame = tk.Frame(l_frame)
clip_frame.grid(row=2, column=0, sticky="nsew")
clip_frame.columnconfigure(0, weight=1)
clip_frame.columnconfigure(1, weight=1)

# Label
clips_label = tk.Label(clip_frame, text="Download clip", font=('Arial', 13), height = 1).grid(row=0, column=0, sticky="e")

# Label
time_label = tk.Label(clip_frame, text="Timestamps:", font=('Arial', 13), height = 1).grid(row=1, column=0, sticky="e")
timestamps_tip_button = tk.Button(clip_frame, text="\u2753", font=('Arial', 13), height = 1, command=lambda: show_message('Clips are made after the download if timestamp fields have any numbers. Timestamps are in format: hh:mm:ss.', "black"))
timestamps_tip_button.grid(row=0, column=2, sticky="w", padx=5)

# Grid for timestamps
timestamps_frame = tk.Frame(clip_frame)
timestamps_frame.grid(row=1, column=1, sticky="nsew", pady=10)
timestamps_frame.columnconfigure(0, weight=1)
timestamps_frame.columnconfigure(1, weight=1)
timestamps_frame.columnconfigure(2, weight=1)
timestamps_frame.columnconfigure(3, weight=1)
timestamps_frame.columnconfigure(4, weight=1)
timestamps_frame.columnconfigure(5, weight=1)
timestamps_frame.columnconfigure(6, weight=1)
timestamps_frame.columnconfigure(7, weight=1)
timestamps_frame.columnconfigure(8, weight=1)
timestamps_frame.columnconfigure(9, weight=1)
timestamps_frame.columnconfigure(10, weight=1)
timestamps_frame.columnconfigure(11, weight=1)
timestamps_frame.rowconfigure(0, weight=1)

start_hours_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
start_hours_field.grid(row=0, column=0, padx=0)
start_hours_field.bind("<Button-3>", context_menu)

space_1_label = tk.Label(timestamps_frame, text=":", font=('Arial', 13), height = 1).grid(row=0, column=1, sticky="ew")

start_minutes_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
start_minutes_field.grid(row=0, column=2, padx=0)
start_minutes_field.bind("<Button-3>", context_menu)

space_2_label = tk.Label(timestamps_frame, text=":", font=('Arial', 13), height = 1).grid(row=0, column=3, sticky="ew")

start_seconds_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
start_seconds_field.grid(row=0, column=4, padx=0)
start_seconds_field.bind("<Button-3>", context_menu)

space_3_label = tk.Label(timestamps_frame, text="-", font=('Arial', 13), height = 1).grid(row=0, column=5, sticky="ew")

end_hours_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
end_hours_field.grid(row=0, column=6, padx=0)
end_hours_field.bind("<Button-3>", context_menu)

space_4_label = tk.Label(timestamps_frame, text=":", font=('Arial', 13), height = 1).grid(row=0, column=7, sticky="ew")

end_minutes_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
end_minutes_field.grid(row=0, column=8, padx=0)
end_minutes_field.bind("<Button-3>", context_menu)

space_5_label = tk.Label(timestamps_frame, text=":", font=('Arial', 13), height = 1).grid(row=0, column=9, sticky="ew")

end_seconds_field = tk.Entry(timestamps_frame, justify="center", font=('Arial', 13), width=5)
end_seconds_field.grid(row=0, column=10, padx=0)
end_seconds_field.bind("<Button-3>", context_menu)

# Separator
separator2 = ttk.Separator(l_frame, orient="horizontal").grid(row=3, column=0, columnspan=7, sticky="news", padx=30, pady=20)

# Grid for buttons
buttons_frame = tk.Frame(l_frame)
buttons_frame.grid(row=4, column=0, sticky="news")
buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)
buttons_frame.columnconfigure(2, weight=1)
buttons_frame.columnconfigure(3, weight=1)
buttons_frame.rowconfigure(0, weight=1)
buttons_frame.rowconfigure(1, weight=1)

# Button to update yt-dlp
ytdlp_update_button = tk.Button(buttons_frame, text="Update yt-dlp", font=('Arial', 12), command=lambda: th.Thread(target=update_ytdlp).start(), height = 1, width = 10).grid(row=0, column=0, sticky="news", padx=5, pady=10)

# Button to open folder
open_folder_button = tk.Button(buttons_frame, text="Open folder", font=('Arial', 12), command=open_folder, height = 1, width = 10).grid(row=0, column=1, sticky="news", padx=5, pady=10)

# Button to clear fields
clear_fields_button = tk.Button(buttons_frame, text="Clear fields", font=('Arial', 12), command=clear_fields, height = 1, width = 10).grid(row=0, column=2, sticky="news", padx=5, pady=10)

# Button to start download
start_button = tk.Button(buttons_frame, text="Start", font=('Arial', 15), command=lambda: th.Thread(target=start_download).start(), height = 1, width = 15, bg="lightgreen").grid(row=0, column=3, sticky="news", padx=5, pady=10)

# Grid for command text fields
commands_frame = tk.Frame(l_frame)
commands_frame.grid(row=5, column=0, sticky="news")
commands_frame.columnconfigure(0, weight=1)
commands_frame.columnconfigure(1, weight=1)
commands_frame.rowconfigure(0, weight=1)
commands_frame.rowconfigure(1, weight=1)

# Button and label for copying yt-dlp command
full_video_command_tip_button = tk.Button(commands_frame, text="Copy to clipboard", font=('Arial', 13), height = 1, width=20, command=lambda: th.Thread(target=copy_to_clipboard("full", command_var)).start())
full_video_command_tip_button.grid(row=0, column=0, sticky="ew", padx=5)
full_video_command_title = tk.Label(commands_frame, textvariable=full_video_command_text, font=('Arial', 10), height = 1, width = 50, anchor="w")
full_video_command_title.grid(row=0, column=1, sticky="e")

# Button and label for copying FFMPEG command
clip_command_tip_button = tk.Button(commands_frame, text="Copy to clipboard", font=('Arial', 13), height = 1, width=20, command=lambda: th.Thread(target=copy_to_clipboard("clip", cutter_var)).start())
clip_command_tip_button.grid(row=1, column=0, sticky="ew", padx=5)
clip_command_title = tk.Label(commands_frame, textvariable=clip_command_text, font=('Arial', 10), height = 1, width = 50, anchor="w")
clip_command_title.grid(row=1, column=1, sticky="e")

# Start process
window.mainloop()