import cv2
import sys
import os
import time
import threading
import queue
import msvcrt
from typing import Tuple

class NonBlockingInput:
    def __init__(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
    
    def get_char(self):
        if msvcrt.kbhit():
            char = msvcrt.getch().decode('utf-8', errors='ignore')
            #handle arrow keys (two bytes)
            if char == '\xe0':  # Special key prefix on Windows
                char2 = msvcrt.getch().decode('utf-8', errors='ignore')
                if char2 == 'K':  #left arrow
                    return 'LEFT'
                elif char2 == 'M':  #light arrow
                    return 'RIGHT'
            return char
        return None

def map_range(from_range: Tuple[int, int], to_range: Tuple[int, int], s: int) -> int:
    from_min, from_max = from_range
    to_min, to_max = to_range
    
    return to_min + (s - from_min) * (to_max - to_min) // (from_max - from_min)

def find_colors(frame, gray, ascii_table: str) -> str:
    out_colors = []
    rows, cols = gray.shape
    table_len = len(ascii_table)
    
    for row in range(rows):
        for col in range(cols):
            b, g, r = frame[row, col]
            
            gray_pixel = max(0, min(255, int(gray[row, col])))
            
            ascii_index = map_range((0, 255), (0, table_len - 1), gray_pixel)
            ascii_char = ascii_table[ascii_index]
            
            out_colors.append(f"\033[38;2;{r};{g};{b}m{ascii_char}")
        
        out_colors.append("\r\n")
    
    return "".join(out_colors)

def get_terminal_size() -> Tuple[int, int]:
    try:
        return os.get_terminal_size()
    except OSError:
        return (80, 24)  #default fallback

def handle_args() -> str:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <video file>", file=sys.stderr)
        sys.exit(1)
    return sys.argv[1]

def clear_screen():
    print("\033[2J", end="")

def move_cursor(x: int, y: int):
    print(f"\033[{y};{x}H", end="")

def hide_cursor():
    print("\033[?25l", end="")

def show_cursor():
    print("\033[?25h", end="")

def set_color(color: str):
    colors = {
        "yellow": "\033[33m",
        "green": "\033[32m",
        "reset": "\033[0m"
    }
    print(colors.get(color, ""), end="")

def enable_ansi_colors():
    if os.name == 'nt':
        try:
            import subprocess
            subprocess.run('', shell=True)  #enable ANSI
            #enable virtual terminal processing
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

def frame_producer(cap, frame_queue, term_cols: int, term_rows: int, ascii_table: str):
    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break
            
            if frame.shape[1] > 0:
                resized = cv2.resize(frame, (term_cols, term_rows - 1), interpolation=cv2.INTER_AREA)
                
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                
                ascii_frame = find_colors(resized, gray, ascii_table) #into ascii 
                
                try:
                    frame_queue.put(ascii_frame, timeout=0.1)
                except queue.Full:
                    continue
    except Exception as e:
        print(f"Error in frame producer: {e}", file=sys.stderr)

def main():
    enable_ansi_colors()
    
    # Configuration
    is_paused = False
    time_multiplier = 1.0
    ascii_table = "     .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

    term_size = get_terminal_size()
    term_cols, term_rows = term_size.columns, term_size.lines
    
    video_file = handle_args()
    
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"Unable to open video file: {video_file}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30.0  # Default to 30 FPS if unable to get FPS
    
    print("\033[?1049h", end="")  #enter alternate screen
    hide_cursor()
    
    frame_queue = queue.Queue(maxsize=50)
    producer_thread = threading.Thread(
        target=frame_producer, 
        args=(cap, frame_queue, term_cols, term_rows, ascii_table),
        daemon=True
    )
    producer_thread.start()
    
    try:
        with NonBlockingInput():
            while True:
                indicator = f"{1.0/time_multiplier:.1f}x" if not is_paused else "paused"
                move_cursor((term_cols - len(indicator)) // 2 + 1, term_rows)
                set_color("yellow")
                print(indicator, end="")
                set_color("reset")
                sys.stdout.flush()
                
                if not is_paused:
                    try:
                        frame_data = frame_queue.get(timeout=0.1)
                        move_cursor(1, 1)
                        clear_screen()
                        print(frame_data, end="")
                        
                        time.sleep(frame_delay * time_multiplier)
                    except queue.Empty:
                        if not producer_thread.is_alive():
                            break
                 
                char = None
                try:
                    with NonBlockingInput() as nbi:
                        char = nbi.get_char()
                except:
                    pass
                
                if char:
                    if char == 'q' or char == 'Q':
                        break
                    elif char == ' ':
                        is_paused = not is_paused
                    elif char == 'LEFT':  #left arrow - slow down
                        if time_multiplier < 4.0:
                            time_multiplier *= 2.0
                    elif char == 'RIGHT':  #right arrow - speed up
                        if time_multiplier > 0.25:
                            time_multiplier /= 2.0
                
                move_cursor(1, 1)
        
        exit_prompt = "VIDEO FEED ENDED. PRESS ANY KEY TO EXIT"
        move_cursor((term_cols - len(exit_prompt)) // 2 + 1, term_rows)
        set_color("green")
        print(exit_prompt, end="")
        set_color("reset")
        sys.stdout.flush()
        
        with NonBlockingInput():
            while True:
                char = None
                try:
                    with NonBlockingInput() as nbi:
                        char = nbi.get_char()
                        if char:
                            break
                except:
                    pass
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    
    finally:
        cap.release()
        print("\033[?1049l", end="")
        show_cursor()
        print()

if __name__ == "__main__":
    main()