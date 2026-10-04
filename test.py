import time
import mido
import math

def print_xy(x,y,col=17,ch=0):
    if 0 <= x < 8 and 0 <= y < 8:
        port.send(mido.Message("note_on", channel=ch, note=((y+1)*10)+(x+1), velocity=col))

def print_xy_timed(x,y,col=17,ch=0, timer=0.1):
    print_xy(x,y,col=col,ch=ch)
    time.sleep(timer)
    print_xy(x,y,col=0,ch=ch)

# --- 3x5 Digit Bitmaps ---
DIGITS = {
    '0': ["111", "101", "101", "111"],
    '1': ["010", "110", "010", "111"],
    '2': ["011", "001", "010", "011"],
    '3': ["111", "001", "011", "111"],
    '4': ["101", "111", "001", "001"],
    '5': ["011", "010", "001", "011"],
    '6': ["111", "100", "111", "111"],
    '7': ["111", "001", "010", "010"],
    '8': ["111", "010", "101", "111"],
    '9': ["111", "111", "001", "111"],
}

def draw_digit(digit, start_x, start_y, col=37):
    """Draws a single 3x5 digit starting at top-left coordinate (start_x, start_y)."""
    pattern = DIGITS.get(str(digit))
    pattern.reverse()
    if not pattern:
        return

    for row_idx, row in enumerate(pattern):
        for col_idx, char in enumerate(row):
            if char == '1':
                print_xy(start_x + col_idx, start_y + row_idx, col=col)
            else:
                print_xy(start_x + col_idx, start_y + row_idx, col=0)
            print(f"printed {char} to [{start_x + col_idx},{start_y + row_idx}]")

def box_digit(digit, box, col=116):
    if not 0 <= box < 4:
        print("Error")
        return
    BOX={"0": (0,0), "1":(4,0), "2":(0,4), "3":(4,4)}
    draw_digit(digit, BOX[str(box)][0], BOX[str(box)][1], col=col+2 if box >1 else col)

def draw_box(col=17):
    for x in range(8):
        print_xy(0,x,col=col)
        print_xy(x,0,col=col)
        print_xy(7,x,col=col)
        print_xy(x,7,col=col)

def clear():
    for y in range(8):
        for x in range(8):
            print_xy(x,y,col=0)



def rotating_radar(sweeps=4):
    """Rotating radar beam highlighting grid cells as it turns."""
    colors = [21, 25, 29]  # Bright greens
    center = 3.5
    for step in range(sweeps * 16):
        angle = (step * math.pi / 8)
        
        # Draw beam
        for y in range(8):
            for x in range(8):
                # Calculate angle of cell relative to center
                dx = x - center
                dy = y - center
                cell_angle = math.atan2(dy, dx)
                
                # Check angular distance to current beam trajectory
                diff = abs((cell_angle - angle + math.pi) % (2 * math.pi) - math.pi)
                
                if diff < 0.35:
                    col = colors[0]  # Direct beam path
                    print_xy(x, y, col=col)
                elif diff < 0.65:
                    col = 12  # Fade tail
                    print_xy(x, y, col=col)
                else:
                    print_xy(x,y,col=0)

        time.sleep(0.01)

def matrix_rain(duration=5.0):
    """Falling digital raindrops across the 8x8 matrix."""
    import random
    drops = [{'x': col, 'y': random.randint(-8, 0), 'speed': random.choice([1, 2])} for col in range(8)]
    start = time.time()
    
    while time.time() - start < duration:
        clear()
        for drop in drops:
            drop['y'] += 1
            if drop['y'] > 10:
                drop['y'] = random.randint(-4, -1)
            
            head_y = drop['y']
            tail_y = head_y - 1
            faint_y = head_y - 2
            
            # Head (White/Bright Lime)
            if 0 <= head_y < 8:
                print_xy(drop['x'], head_y, col=3)
            # Trail (Green)
            if 0 <= tail_y < 8:
                print_xy(drop['x'], tail_y, col=25)
            # Fade (Dark Green)
            if 0 <= faint_y < 8:
                print_xy(drop['x'], faint_y, col=21)
                
        time.sleep(0.09)

def draw_full():
    velocity = 3
    for y in range(8):
        for x in range(8):
            print_xy(y,x)    
            velocity+=1
            time.sleep(0.05)

# Find the Launchpad port
port_names = mido.get_output_names()
print(f"Available output ports: {port_names}")

port_name = next(name for name in port_names if "Launchpad" in name or "Launch" in name)
print(f"Connecting to: {port_name}")

with mido.open_output(port_name) as port:
    # 1. Switch Launchpad MK2 to Session Layout via SysEx (Layout 0)
    # Header: 240, 0, 32, 41, 2, 24 (Launchpad MK2 ID), 34 (Change Layout), 0 (Session), 247
    port.send(mido.Message.from_bytes([240, 0, 32, 41, 2, 24, 34, 0, 247]))
    time.sleep(0.1)  # Give the device a moment to switch modes

    print("Choose your programm:")
    print("1. Radar")
    print("2. Matrix")
    print("3. Digit")

    inner = input("[1|2|3]\n")
    try:
        if int(inner) == 1:
            rotating_radar()
        elif int(inner) == 2:
            matrix_rain()
        elif int(inner) == 3:
            for x in range(100):
                box_digit(1,x%4)
                time.sleep(1)
            time.sleep(80)
        else:
            print(f"ERROR your input was {int(inner)}")
        clear()
    except KeyboardInterrupt:
        print("[CLEARING]")
        clear()


