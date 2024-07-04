# Tilhi - yt-dlp GUI

Tilhi is an easy-to-use graphic use interface for yt-dlp and ffmpeg. Download videos in multiple different video and audio formats. Project goal is to make a handy tool for my friend who has had difficulty using command-line programs.

"Tilhi" is a bird that only shows itself during Autumn, in English it's name is "bohemian waxwing".

Available in English and Finnish.

## User installation

Download the project and either run it locally or compile it. Sections with instructions are below.

Download yt-dlp.exe: https://github.com/yt-dlp/yt-dlp/releases

Download ffmpeg: https://github.com/yt-dlp/FFmpeg-Builds/releases

Extract ffmpeg folder. Move both ffmpeg.exe, ffprobe.exe and yt-dlp.exe to the same folder where Tilhi is.

## How to use

Only required input field is the url address of the video page you want to download from. Videos are downloaded in webm file format.

You can also make a clip by filling timestamp field and it uses HH:MM:SS format. Only ending timestamp is required, starting timestamp starts from 00:00:00 by default. Empty fields are filled with "00".

After making a clip, you can make another one by filling in new timestamps. The same full video will not be downloaded again if the full video is still in the folder, only new clip is created.

If you check the audio-only option, both full video and the clips are downloaded in audio-only format. Audio file format is m4a.

If you check the delete original option, the full version is deleted and only clips are kept.

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
pyinstaller --name=Tilhi --icon=res/tilhi-icon.ico main.py --onefile
```

## Credits and learning links

Image resizing tutorial by Atlas: https://www.youtube.com/watch?v=VnwDPa9biwc

Icon and cover images are generated by DALL-E 3 with following prompts:

- Icon: "Icon on white background, cartoony bohemian waxwing sitting on a green download icon"
- Cover 1: "Vibrant and playful painting with flowing brushtrokes and vibrant colors, two bohemian waxwings playfully flying among sorbus tree branches that have berries, blue sunny sky, happy feeling"
- Cover 2: "Watercolor pencil drawing, hand drawn, bohemian waxwing at a scandinavic bird feeder, blue sunny sky"
- Cover 3: "Digital 3D art, bohemian waxwing flying over a lake, no other birds or animals"
