from tkinter import *
from tkinter import filedialog
import tkinter.messagebox
import os
from mutagen.mp3 import MP3
from pygame import mixer

FORMATS = ['.mp3', '.wav', '.ogg', '.flac']
PAUSED = FALSE
STOPPED = FALSE
CURR_TR = ""

mixer.init()  # initializing the mixer

root = Tk()

# Messagebox
def about_player():
    tkinter.messagebox.showinfo('About player', 'Version 0.1')

def browse_file():
    global CURR_TR
    CURR_TR = filedialog.askopenfilename()

def show_details():
    file_data = os.path.splitext(CURR_TR)
    if file_data[1] == '.mp3':
        audio = MP3(CURR_TR)
        curr_length = audio.info.length
    else:
        title_text['text'] = "Playing"
        a = mixer.Sound(CURR_TR)
        curr_length = a.get_length()
    mins, secs = divmod(curr_length, 60)  ### !!!
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    length_lab = Label(root, text='Length: ' + timeformat)
    length_lab.pack()

# Menubar
menubar = Menu(root)
root.config(menu=menubar)
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=subMenu)
subMenu.add_command(label='Open', command=browse_file)
subMenu.add_command(label='Play')
subMenu.add_command(label='Exit', command=root.destroy)
subMenu2 = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Others', menu=subMenu2)
subMenu2.add_command(label='Open', command=about_player)

#root.geometry('300x300')
root.title("More Sound")
root.iconbitmap(r'Icons/001_speaker_plus_sign_6xq_icon.ico')

title_text = Label(root, text='More Sound')
title_text.pack(pady=10)
#length_lab = Label(root, text='Length: --:--')
#length_lab.pack()

#frame
middleframe = Frame(root)
middleframe.pack(padx=10, pady=10)

PlayPhoto = PhotoImage(file=r'Icons/002-play-right-arrow-triangle-outline.png')
StopPhoto = PhotoImage(file=r'Icons/008-square-outlined-shape.png')
PausePhoto = PhotoImage(file=r'Icons/002-two-vertical-parallel-lines.png')
RewindPhoto = PhotoImage(file=r'Icons/001-left-arrows-couple.png')


def play_music():
    global PAUSED
    global STOPPED
    if PAUSED == TRUE:
        mixer.music.unpause()
        PASUED = FALSE
    elif STOPPED == TRUE:
        mixer.music.load(CURR_TR)
        mixer.music.play()
        STOPPED = FALSE
    else:
        try:
            mixer.music.load(CURR_TR)
            mixer.music.play()

        except:
            browse_file()
            mixer.music.load(CURR_TR)
            mixer.music.play()
    statusbar['text'] = 'Playing \"' + os.path.basename(CURR_TR) + '\"'
    show_details()

def pause_music():
    global PAUSED
    PAUSED = TRUE
    mixer.music.pause()
    statusbar['text'] = "Pause"

def stop_music():
    if PAUSED == TRUE:
        mixer.music.load(CURR_TR)
        mixer.music.play()
    global STOPPED
    STOPPED = TRUE
    mixer.music.stop()
    statusbar['text'] = "Stop"

PlayBtn = Button(middleframe, image=PlayPhoto, command=play_music)
PlayBtn.grid(row=0, column=1, padx=10, pady=10 )

StopBtn = Button(middleframe, image=StopPhoto, command=stop_music)
StopBtn.grid(row=0, column=2, padx=10, pady=10)

PauseBtn = Button(middleframe, image=PausePhoto, command=pause_music)
PauseBtn.grid(row=0, column=3, padx=10, pady=10)

RewindBtn = Button(middleframe, image=RewindPhoto, command=play_music)
RewindBtn.grid(row=0, column=0, padx=10, pady=10)

statusbar = Label(root, title_text,text="Welcome to More Sound", relief = SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)

def directory_chooser():
    directory = askdirectory()
    os.chdir(directory)

    current_path = directory

    list_of_paths = []

    for format in FORMATS:
        for files in os.listdir(directory):
            if files.endswith(format):
                list_of_paths.append(directory + files)

    return list_of_paths


def set_vol(val):
    volume = int(val) / 100
    mixer.music.set_volume(volume)

scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)
mixer.music.set_volume(0.7)
scale.pack()

root.mainloop()
