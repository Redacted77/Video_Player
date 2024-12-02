# Video Player

A video player that uses **PySide6** for the GUI and **python-vlc** for video playback. The project is structured into three files:

1. **main.py**
2. **gui.py**
3. **playback_vlc.py**

---

# exe

the exe application is in **dist**

---

## main.py

This file initializes the application and allows you to run it.

---

## gui.py

Contains all the GUI elements, including:

- Video widget
- File menu
- Subtitle menu
- Play button, etc.

### Menu Bar

The menu bar has three menus:

- **File Menu**:
  - **Open Video**: Opens a window to select a video.
  - **Add Subtitles** and **Add Audio Tracks**: Add embedded subtitles and audio tracks (if available). If none are embedded, the subtitle and audio menus remain empty.
- **Subtitle Menu**
- **Audio Menu**

---

## playback_vlc.py

Handles almost all VLC-related elements.

---

## Noteworthy Information

1. A VLC instance is created in `gui.py`. When a video is selected in the `open_video()` function, a new thread is created to handle playback.
2. The thread starts video playback and emits a signal with key information such as video length and the current playback time.
3. When the video ends, another signal is emitted, triggering a function in `gui.py` to reset the GUI elements.
4. After initialization, GUI elements (e.g., volume slider, pause button, time display) are connected to the video player.
5. The `seek_in_min()` function in `playback_vlc.py` is called every second to retrieve the current playback time. It converts the time into minutes and seconds while also returning the time in milliseconds for seek functions.
6. In fullscreen mode:
   - A timer hides widgets like the seeker, volume slider, and buttons every 3 seconds.
   - Another timer hides popups for volume changes and skipping 10 seconds every 1.5 seconds.
7. The play button toggles between play and pause states, updates its displayed text accordingly, and hides both volume and skipping popups in fullscreen mode.
8. **Keyboard Shortcuts**:
   - **Spacebar**: Pause/play the video.
   - **Up Arrow**: Increase volume by 10.
   - **Down Arrow**: Decrease volume by 10.
   - **Right Arrow**: Skip forward 10 seconds.
   - **Left Arrow**: Skip backward 10 seconds.
   - **F**: Toggle fullscreen mode.
   - **S**: Add subtitles to the subtitle menu.
   - **A**: Add an audio track to the audio track menu.
9. the **exe** was created using **pyinstaller**
10. **Open With Functionality**:
    - The application can take a video path as a command-line argument in `main.py`.
    - This path is passed to the `open_with()` function in `gui.py`, which plays the video immediately upon startup.
