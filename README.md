# Lightweight Image tagger
This visual software enables easy tagging, rotation and deletion of image batches, which can help organise media collections
   
# How to use it

## Prerequisites
- Python > 3.7.4

## Install steps
1. clone this repo
2. `cd` in repo root
3. optional: create virtual environment, activate it
4. `pip install -r requirments.txt`
5. `python main.py`

## Instructions
- Open folder: open a folder with images by clicking *Open* or *Folder* in the top left corner
- Scroll: *left/right* key arrows
- Rotate: *shift* + *left/right* key arrows
- Save modification: *shift + s*. Saveable modifications:
    - rotation
    - the label is saved in the image EXIF (or metadata)
- Label: *shift + t* 
    - All the fields are required
        - Name: label name
        - Shortcut: key (capital letter) for shortcuting image labeling
        - Browse: folder path to move the labeled images to (after pressing the *Apply modification key*)
![Tag Dialog Box](/resources/dialog-box.png)
- Mark for deletion: *DELETE* key
- Apply modifications: *ctrl + F1*. 
    -  Move labeled images to the label specific folder path
    -  Deleted images marked for deletion


# Support
## Operating Systems
- Windows (tested on Windows 10)

# Contribute
Drop an issue if you have any questions, suggestions or observations. Other not yet implemented cool features I've been thinking about can be found in the TODO file or in code marked with # TODO.

## A few code explanations
- see MainWindow.py for the currently shortcuts binded actions
- /resources/media_sorter.ui is the PyQt Designer generated UI file
- media_sorter.ui code translation (with pyuic5) is contained in the UiRenderer.py file

# Credits
Shoutout to [PyQT5](https://www.qt.io/qt-for-python)