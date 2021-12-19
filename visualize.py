"""
FFMPEG COMMANDS

MP3 -> WAV:         ffmpeg -i input.mp3 output.wav
WAV -> MP3:         ffmpeg -i input.wav -vn -ar 44100 -ac 2 -b:a 192k output.mp3
Combine MP4 + MP3:  ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -c:v copy -c:a copy output.mp4 -y

There are some adjustable parameters in this script
"""

import json
import argparse
import subprocess as sp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

parser = argparse.ArgumentParser(description="Spectrum video file generator")
parser.add_argument("json", help="Spectrum JSON file")
parser.add_argument("audio", help="Audio file (mp3 or wav)")
parser.add_argument("-x", help="x-axis range (default auto)", type=float, nargs=2, metavar=('min', 'max'))
parser.add_argument("-y", help="y-axis range (default auto)", type=float, nargs=2, metavar=('min', 'max'))
parser.add_argument("-d", help="DPI of the output video (default 100)", type=int, nargs=1, metavar="dpi")
parser.add_argument("-w", help="Changes ratio to 16:9 (default 4:3)", default=False, action="store_true")
parser.add_argument("-f", help="FPS of the output video (default 20)", type=int, nargs=1, metavar="fps")
parser.add_argument("-t", help="Hides plot title", default=False, action="store_true")
parser.add_argument("-l", help="Hides plot labels", default=True, action="store_false")
parser.add_argument("-b", help="Hides borders and ticks", default=False, action="store_true")
parser.add_argument("-log", help="y-axis log scale", default=False, action="store_true")
parser.add_argument("-c", help="Color of plot lines (default dependant on theme)", type=str, nargs=1, metavar="color")
parser.add_argument("-th", help="Graph theme (default dark)", type=str, nargs=1, metavar="dark/light")
args = parser.parse_args()

dpi = 100 # DPI
if args.d is not None:
    dpi = args.d[0]

fps = 20  # FPS (match with spectrum FPS - 1000ms / interval)
if args.f is not None:
    fps = args.f[0]

if args.th is not None and args.th[0] == "light":
    lineColor = "blue"  # light theme
else:
    lineColor = "white"  # dark theme (default)
    plt.style.use('dark_background')

if args.c is not None: # line color (if specified)
    lineColor = args.c[0]

fig, ax = plt.subplots()
if args.w:
    fig, ax = plt.subplots(figsize=(8, 4.5))
ln, = plt.plot([], [], color=lineColor)
ln2, = plt.plot([], [], color=lineColor)

with open(args.json) as file:
    data = json.load(file)

def maxMag(): # get the max magnitude estimate
    mag = 0

    for frame in range(0, len(data["channel_1"])):
        for sample in data["channel_1"][frame]["spectrum"]:
            if abs(sample) > mag:
                mag = abs(sample)

    return mag*1.1

def maxFreq(): # get the max frequency estimate
    freq = 0
    mag = maxMag()

    for frame in range(0, len(data["channel_1"])):
        for sample in range(len(data["freqs"])):
            if abs(data["channel_1"][frame]["spectrum"][sample]) > mag*0.15: # exclude anything below the 5% percentile of the average mag
                if data["freqs"][sample] > freq:
                    freq = data["freqs"][sample]

    return freq*1.01

def init():
    if args.x is None:
        freq = maxFreq()
        ax.set_xlim(0, freq)
        print(f"freq: {0}, {freq}")
    else:
        ax.set_xlim(args.x[0], args.x[1])
        print(f"freq: {args.x[0]}, {args.x[1]}")

    if args.y is None:
        mag = maxMag()
        ax.set_ylim(mag*-1, mag)
        print(f"mag: {mag*-1}, {mag}")
    else:
        ax.set_ylim(args.y[0], args.y[1])
        print(f"mag: {args.y[0]}, {args.y[1]}")

    if args.l:
        ax.set_xlabel("Frequency [Hz]")
        ax.set_ylabel("Magnitude")
    
    if args.b:
        ax.axes.xaxis.set_visible(False)
        ax.axes.yaxis.set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

    if args.th is not None and args.th[0] == "light":
        lineColor = "blue"  # light theme
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")
    else:
        lineColor = "white"  # dark theme (default)
        plt.style.use('dark_background')
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")

    if args.log:
        ax.set_xscale('log', base=2)

    return ln, ln2,

def update(frame):
    print(f"Frame {frame+1}/{len(data['channel_1'])}       ", flush=True, end="\r")
    xdata, ydata = data["freqs"], data["channel_1"][frame]["spectrum"]
      
    if not args.t:
      ax.set_title(f"Sample {data['channel_1'][frame]['begin']}")

    ln.set_data(xdata, ydata)
    ln2.set_data(xdata, [ -y for y in ydata])
    return ln, ln2,

ani = FuncAnimation(fig, update, frames=range(0, len(data["channel_1"])-1), init_func=init, blit=True)
ani.save(f"spectrum_{args.audio[:-4]}.mp4", fps=fps, dpi=dpi)  # output name, dpi, framerate etc. Framerate depends on how you spliced the audio

if args.audio[-3:] == "wav":  # convert wav audio file to mp3
    sp.call(f"ffmpeg -i {args.audio} -vn -ar 44100 -ac 2 -b:a 192k {args.audio[:-4]}.mp3", shell=True)
    
# combine audio and video
sp.call(f"ffmpeg -i spectrum_{args.audio[:-4]}.mp4 -i {args.audio[:-4]}.mp3 -map 0:v -map 1:a -c:v copy -c:a copy final_{args.audio[:-4]}.mp4 -y", shell=True)