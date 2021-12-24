import math
import json
import argparse
import subprocess as sp
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

parser = argparse.ArgumentParser(description="spectralyze visualizer - audio spectrum animated video generator")
parser.add_argument("json", help="Spectrum JSON file")
parser.add_argument("audio", help="Audio file (mp3 or wav)")
parser.add_argument("-fps", help="FPS of the output video (FPS * spectralyze intervals (-i) = 1000)", type=int, metavar="fps", required=True)
parser.add_argument("-dpi", help="DPI of the output video", type=int, default=100, metavar="dpi")
parser.add_argument("-x", help="x-axis range", type=float, nargs=2, metavar=('min', 'max'))
parser.add_argument("-y", help="y-axis range", type=float, nargs=2, metavar=('min', 'max'))
parser.add_argument("--lines", help="Shows all chart lines and borders", default=True, action="store_false")
parser.add_argument("--title", help="Shows chart title", default=False, action="store_true")
parser.add_argument("--verbose", help="Prints status and debug information", default=False, action="store_true")
args = parser.parse_args()

# open JSON file
with open(args.json) as file:
    data = json.load(file)

class Polar():
    def __init__(self):
        """
        ARGPARSE
            JSON -> args.json
            AUDIO -> args.audio
                NAME -> args.audio[:-4]
                FORMAT -> args.audio[-4:]
            FPS -> args.fps
            DPI -> args.dpi
            Y-AXIS -> args.y
                MIN -> args.y[0]
                MAX -> args.y[1]
            X-AXIS -> args.x
                MIN -> args.x[0]
                MAX -> args.x[1]
            LINES -> args.lines
            TITLE -> args.title
            VERBOSE -> args.verbose
        CLASS
            DATA -> self.load()
            MAG -> self.data["channel_1"]
                LENGTH -> len(self.mag)
                MAX -> self.auto_mag()
            FREQ -> self.data["freqs"]
                LENGTH -> len(self.freq)

        """
        # JSON
        self.json = args.json

        # AUDIO
        self.audio_file = args.audio
        self.audio_name = self.audio_file[:-4]
        self.audio_format = self.audio_file[-4:]

        # animation variables
        self.dpi = args.dpi
        self.fps = args.fps

        # Y-AXIS
        self.y_axis = args.y
        if self.y_axis is not None:
            self.y_axis_min = self.y_axis[0]
            self.y_axis_max = self.y_axis[1]

        # X-AXIS
        self.x_axis = args.x
        if self.x_axis is not None:
            self.x_axis_min = self.x_axis[0]
            self.x_axis_max = self.x_axis[1]

        # LINES
        self.lines = args.lines

        # TITLE
        self.title = args.title

        # VERBOSE
        self.verbose = args.verbose

        # DATA
        self.data = self.load()

        # MAG
        self.mag = self.data["channel_1"]
        self.mag_length = len(self.mag)
        self.mag_max = self.auto_mag()

        # FREQ
        self.freq = self.data["freqs"]
        self.freq_length = len(self.freq)
        self.freq_max = self.auto_freq()

        # SERIES
        self.fig = plt.figure(figsize=(8,8))
        self.ax = plt.subplot(111, polar=True)

        x = np.linspace(0.0, 2 * np.pi, len(self.mag[0]["spectrum"][:500]))
        width = (2*np.pi) / len(self.mag[1]["spectrum"][:500])
        bottom = 0.1
        self.series = self.ax.bar(x, self.mag_it(0), width=width, bottom=bottom)

    def load(self):
        """
        loads JSON file
        """
        with open(self.json) as file:
            return json.load(file)

    def auto_mag(self):
        """
        finds the maximum magnitude of the dataset
        """
        temp_mag = 0

        # iterates through all magnitudes to determine the largest
        for sample in range(0, self.mag_length):
            for mag in self.mag[sample]["spectrum"]:
                if abs(mag) > temp_mag:
                    temp_mag = abs(mag)

        return temp_mag*1.1

    def auto_freq(self):
        """
        attempts to automatically determine the best frequency range for the plot
        """
        temp_freq = 0

        for sample in range(0, self.mag_length-1):
            for mag in range(0, self.freq_length-1):
                if abs(self.mag[sample]["spectrum"][mag]) > self.mag_max*0.15: # exclude anything below the 5% percentile of the average mag
                    if self.freq[mag] > temp_freq:
                        temp_freq = self.freq[mag]

        return temp_freq*1.01

    def mag_it(self, n):
        smoothV = 0.15
        #return [((-smoothV*self.mag_max)/ele+(smoothV*self.mag_max))+1 if ele != 0 else ele for ele in [0 if abs(ele) < self.mag_max*smoothV else ele for ele in self.mag[n]["spectrum"][:500]]]
        return [(x*40) for x in self.mag[n]["spectrum"][:500]]

    def update(self, frame):
        """
        update function for FuncAnimation
        """
        if self.verbose:
            print(f"Frame {frame+1}/{self.mag_length-1}       ", flush=True, end="\r")

        if self.title:
            self.ax.set_title(f"Sample {data['channel_1'][frame]['begin']}")
        
        self.ax.set_yticks(np.arange(0,1,0.1))

        if self.lines:
            self.ax.axis("off")

        y=self.mag_it((frame-1)+1)
        for i, b in enumerate(self.series):
            b.set_height(y[i])      

    def animate(self):
        """
        animation of the plot
        """
        ani = FuncAnimation(self.fig, self.update, repeat=False, frames=range(0, self.mag_length-1), blit=False)
        ani.save(f"spectrum_{self.audio_name}.mp4", fps=self.fps, dpi=self.dpi)

        if self.audio_format == ".wav":
            self.convert()

        self.combine()
    
    def convert(self):
        """
        converts audio file to correct format
        """
        sp.call(f"ffmpeg -i {self.audio} -vn -ar 44100 -ac 2 -b:a 192k {self.audio_name}.mp3", shell=True)

    def combine(self):
        """
        combines audio with video
        """
        sp.call(f"ffmpeg -i spectrum_{args.audio[:-4]}.mp4 -i {args.audio[:-4]}.mp3 -map 0:v -map 1:a -c:v copy -c:a copy final_{args.audio[:-4]}.mp4 -y", shell=True)

spectrum = Polar()
spectrum.animate()