# spectralyze visualizer
Graphical visualizer for [spectralyze](https://github.com/Lauchmelder23/spectralyze) by [Lauchmelder23](https://github.com/Lauchmelder23)

## Install
Install matplotlib and ffmpeg. Put `ffmpeg.exe` in same folder as `visualize.py` for Windows installations.

For best results, use the [spectralyze](https://github.com/Lauchmelder23/spectralyze) file for Windows available in the [most recent release](https://github.com/mpsparrow/spectralyze-visualizer/releases/latest) in this repository.

## Usage
Most flags are experimental and may result in a less than ideal end result.

Use `python visualizer.py -h` for more up to date information.
```
usage: 
visualize.py json audio [-h] [-x min max] [-y min max] [-d dpi] [-w] [-f fps] 
[-t] [-l] [-b] [-c color] [-th dark/light] [-n] 

Spectrum video file generator

positional arguments:
  json            Spectrum JSON file
  audio           Audio file (mp3 or wav)

optional arguments:
  -h, --help      show this help message and exit
  -x min max      x-axis range (default auto)
  -y min max      y-axis range (default auto)
  -d dpi          DPI of the output video (default 100)
  -w              Changes ratio to 16:9 (default 4:3)
  -f fps          FPS of the output video (default 20) (FPS * spectralyze intervals (-i) = 1000)
  -t              Hides plot title
  -l              Hides plot labels
  -b              Hides borders and ticks
  -c color        Color of plot lines (default dependant on theme)
  -th dark/light  Graph theme (default dark)
  -n float        Attempts to remove low, messy magnitudes for a cleaner noise floor with more defined notes (highly experimental)
```

Match the `-f` FPS in visualizer with the `-i` interval flag in spectralyze so that `FPS * interval = 1000ms` (i.e. `20FPS * 50 = 1000`). Failure to do so will result in unsynced audio and video.

## Examples

Starting out, I recommend using the following set of commands.

#### visualizer
```
python visualize.py file.json file.mp3 -d 100 -f 20 -w -t -l -b
```
#### spectralyze
```
spectralyze.exe -i 50 -p 3 file.wav
```
```
spectralyze.exe -i 50 file.wav
```

## Finished results
```
python visualize.py Tetris.json Tetris.mp3 -d 300 -f 20 -x 0 1000 -y -1.01 1.01 -n 0.25 -c purple -w -t -l -b
```
https://user-images.githubusercontent.com/6476699/146701756-f725f36c-20bc-4055-a501-b29e30333adf.mp4

```
python visualize.py Tetris.json Tetris.mp3 -d 300 -f 20 -x 0 1000 -w -t -l -b -c purple
```
https://user-images.githubusercontent.com/6476699/146705851-4bd56d7a-384b-4af4-a87f-0fb32dd24bef.mp4


(don't have the command for the one below)

https://user-images.githubusercontent.com/6476699/146703506-d7e26dc5-2ad1-4552-bf99-bb67f007e8d8.mp4


## Credits
[mpsparrow](https://github.com/mpsparrow)

[Lauchmelder23](https://github.com/Lauchmelder23)
