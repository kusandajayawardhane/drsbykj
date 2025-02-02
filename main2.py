import tkinter
import cv2
import PIL.Image, PIL.ImageTk
from functools import partial
import threading
import time
import imutils
from collections import deque

# Camera setup
stream = cv2.VideoCapture(0)  # Use 0 for default camera
if not stream.isOpened():
    print("Error opening camera.")
    exit()

SET_WIDTH = 565
SET_HEIGHT = 360
decision_pending = False
playing = False
recording = True  # Flag to control recording
frame_buffer = deque(maxlen=300)  # Store up to 300 frames (adjust as needed)
current_frame_index = 0

# ***DEFINE FUNCTIONS FIRST***

def pending(decision):  # This function needs to be defined BEFORE it is used
    global decision_pending
    decision_pending = True
    try:  # Handle potential FileNotFoundError
        frame = cv2.cvtColor(cv2.imread("pending.png"), cv2.COLOR_BGR2RGB)
        frame = imutils.resize(frame, width=SET_WIDTH, height=SET_HEIGHT)
        frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        canvas.image = frame
        canvas.create_image(0, 0, image=frame, anchor=tkinter.NW)
        window.update()
        time.sleep(1.5)

        frame = cv2.cvtColor(cv2.imread("sponser.png"), cv2.COLOR_BGR2RGB)
        frame = imutils.resize(frame, width=SET_WIDTH, height=SET_HEIGHT)
        frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        canvas.image = frame
        canvas.create_image(0, 0, image=frame, anchor=tkinter.NW)
        window.update()
        time.sleep(2.5)

        if decision == 'out':
            decisionImg = "out.png"
        else:
            decisionImg = "not_out.png"
        frame = cv2.cvtColor(cv2.imread(decisionImg), cv2.COLOR_BGR2RGB)
        frame = imutils.resize(frame, width=SET_WIDTH, height=SET_HEIGHT)
        frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        canvas.image = frame
        canvas.create_image(0, 0, image=frame, anchor=tkinter.NW)
        window.update()
    except FileNotFoundError:
        print("Error: Decision images (pending.png, sponsor.png, out.png, not_out.png) not found.")
        decision_pending = False
        return  # Exit early if images are missing

    decision_pending = False  # Reset after decision is shown


def out():  # Define out() BEFORE it is used
    thread = threading.Thread(target=pending, args=("out",))
    thread.daemon = True
    thread.start()
    print("Player is out")

def not_out():  # Define not_out() BEFORE it is used
    thread = threading.Thread(target=pending, args=("not out",))
    thread.daemon = True
    thread.start()
    print("Player is not out")



def play(speed):
    global playing, current_frame_index, recording
    playing = True
    play_continuous(speed)

def play_continuous(speed):
    global playing, current_frame_index, frame_buffer, recording, stream
    while playing:
        if recording:  # Record from camera
            grabbed, frame = stream.read()
            if grabbed:
                frame_buffer.append(frame)
                current_frame_index = len(frame_buffer) - 1  # Update index to the latest frame
            else:  # Camera disconnected or error
                playing = False
                recording = False
                print("Camera disconnected or error during recording.") # Inform user
                break
        elif not frame_buffer:  # Nothing to play back
            playing = False
            break
        else:  # Playback from buffer
            new_index = current_frame_index + speed
            if new_index < 0:
                current_frame_index = 0
            elif new_index >= len(frame_buffer):
                current_frame_index = len(frame_buffer) - 1
            else:
                current_frame_index = new_index  # Safely update the frame index

        if frame_buffer:  # Display frame (only if buffer is not empty)
            frame_to_display = frame_buffer[current_frame_index]
            frame = imutils.resize(frame_to_display, width=SET_WIDTH, height=SET_HEIGHT)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            canvas.image = frame
            canvas.create_image(0, 0, image=frame, anchor=tkinter.NW)
            window.update()
            time.sleep(0.03)  # Adjust for desired frame rate

        if decision_pending:
            canvas.create_text(134, 26, fill="black", font="Times 26 bold", text="Decision Pending")

def toggle_recording():
    global recording, playing
    recording = not recording
    if not recording:  # Stop playback when recording is stopped
        playing = False

# Tkinter GUI setup
window = tkinter.Tk()
window.title("Third Umpire Decision Review Kit")

canvas = tkinter.Canvas(window, width=SET_WIDTH, height=SET_HEIGHT)
canvas.pack()

# Buttons
btn_prev_fast = tkinter.Button(window, text="<< Previous (fast)", width=50, command=partial(play, -5))
btn_prev_fast.pack()

btn_prev_slow = tkinter.Button(window, text="<< Previous (slow)", width=50, command=partial(play, -1))
btn_prev_slow.pack()

btn_next_slow = tkinter.Button(window, text="Next (slow) >>", width=50, command=partial(play, 1))
btn_next_slow.pack()

btn_next_fast = tkinter.Button(window, text="Next (fast) >>", width=50, command=partial(play, 5))
btn_next_fast.pack()

btn_record = tkinter.Button(window, text="Start/Stop Recording", width=50, command=toggle_recording)
btn_record.pack()

btn_out = tkinter.Button(window, text="Give Out", width=50, command=out)
btn_out.pack()

btn_not_out = tkinter.Button(window, text="Give Not Out", width=50, command=not_out)
btn_not_out.pack()

def on_closing():
    global playing, recording
    playing = False
    recording = False
    stream.release()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
