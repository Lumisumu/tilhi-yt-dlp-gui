# Tilhi - yt-dlp GUI

Tilhi is an easy-to-use graphic use interface for yt-dlp and ffmpeg. Download videos from the web and save them as either video or audio. You can also create clips to capture highlights of long videos/streams. Project goal is to make a handy tool for my friend who has had difficulty using command-line programs.

Active development done in English, version with Finnish UI translation available in a separate branch.

## User installation

Download the project and either run it locally or compile it. Sections with instructions are below.

Download yt-dlp.exe: https://github.com/yt-dlp/yt-dlp/releases

Download ffmpeg: https://github.com/yt-dlp/FFmpeg-Builds/releases

Extract ffmpeg folder. Move both ffmpeg.exe, ffprobe.exe and yt-dlp.exe to the same folder where Tilhi is.

## How to use

Only required input field is the url address of the video page you want to download from. Videos are downloaded in webm file format. Pressing Enter key when typing into url field starts the download process instantly.

You can also a clip by filling timestamp field and it uses HH:MM:SS format. Only ending timestamp is required, starting timestamp starts from 00:00:00 by default. Empty fields are filled with "00".

Clip section has three options in a dropdown menu. First option is best for YouTube to fix clipping issues, the other two are for other websites.

After making a clip, you can make another one by filling in new timestamps. The same full video will not be downloaded again if the full video is still in the folder, only new clip is created.

If you check the audio-only option, both full video and the clips are downloaded in audio-only format. Audio file format is m4a.

Click on the "?" buttons to view more tips on each section.

Advanced users: you can use your own yt-dlp command by starting the string in url field with "yt-dlp ". Only other input used is target folder for full videos and it is inserted into your custom command.

## Installing and running project

Install Python 3 and pip: https://www.python.org/

Install "Pillow" module with pip:

```
pip install Pillow
```

Start program by running:

```
python main.py
```

## Build executable

Install PyInstaller with pip:

```
pip install pyinstaller
```

Run in project folder:

```
pyinstaller --name=Tilhi --icon=res/icon.ico main.py --onefile
```

## Credits and learning links

Image resizing tutorial by Atlas: https://www.youtube.com/watch?v=VnwDPa9biwc

Icon and cover images are generated by DALL-E 3 with following prompts:

- Icon: "Icon on white background, cartoony bohemian waxwing sitting on a green download icon"
- Cover : "Digital 3D art, bohemian waxwing flying over a lake, no other birds or animals"

"Tilhi" is a bird that only shows itself during Autumn, in English it's name is "bohemian waxwing".
