# ascii-motion

A terminal-based video player that converts video files into colored ASCII art and plays them in real-time.

## How It Works
1. **Frame Reading**: OpenCV reads video frames sequentially
2. **Resizing**: Each frame is resized to fit your terminal dimensions
3. **ASCII Conversion**: 
   - Frame is converted to grayscale
   - Each pixel's brightness maps to an ASCII character from the density table
   - Original RGB colors are preserved using ANSI escape codes
4. **Display**: Colored ASCII frame is printed to terminal
5. **Threading**: Frame processing runs in a separate thread for smooth playback

## Features

- Play any video format supported by OpenCV
- Full-color ASCII art conversion using RGB values
- Playback controls (play, pause, speed adjustment)
- Automatic terminal size adaptation
- Multi-threaded frame processing for smooth playback
- Real-time playback speed indicator

## Requirements

- Python 3.7+
- OpenCV
- 
## Installation

1. Clone this repository:
```bash
git clone https://github.com/manthanawgan/ascii-motion.git
cd ascii-motion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py <video_file>
```

### Example
```bash
python main.py my_video.mp4
```

## Controls

| Key | Action |
|-----|--------|
| `q` or `Q` | Quit the player |
| `Space` | Pause/Resume playback |
| `←` (Left Arrow) | Slow down playback (0.25x → 4x) |
| `→` (Right Arrow) | Speed up playback (4x → 0.25x) |

### ASCII Density Table
The conversion uses this character density table (darkest to lightest):
```
     .'`^",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
