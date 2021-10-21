# TODO:
- adapt image area to window resize
- remember last opened folder
- package as .exe
- switch left - right photo according to the moment you did that action (not at initial folder load)
- status bar for the moving process
    - freeze any possibility to do anything while pictures are moved
- attach string description to photos? as a reminder for the future of what it represented. Cuz u may forget
- zoom in / out images 
- shortcut doesn't work if small caps are assigned during new label entry creation
- verify if target folder exists before moving, otherwise create it
- use GPS data of photos containing it
- new label register
    - error if label name is already taken
    - error if label shortcut is already taken (have a list of predefined, immutable shortcuts for app actions. e.g.
                "Apply Changes" - Shift + F1)
    - warning if chosen folder path is already used
    - CRUD
- support for Linux
- index media files in an external DB (or .csv file) too
- handle list of labels instead of a single one
- treat empty input directory situation
- realtime update of awwareness of files inside the opened folder
    - for now, only the files present in the folder when it was selected are registered
    - if files are added meanwhile, they won't appear in the slideshow --> fix that
- display media file name in UI
- insert img.verify() when reading images
- media support:
    - images:
        - .rw2, .bmp
- .mpo files contain two electronic images in JPG format, and may also include metadata details
    .The .mpo file extension stands for Multi Picture Object.
- rotate vids
- multiple labels on media files
- insert DEFAULT_FOLDER_BROWSE_PATH in config
- UI friendliness
    - tell user all fields have to be completed when creating a new label
    - communicate operation results to user (e.g. move / save)
    - progress bar
- search for duplicates (image, video)

# BUGS:
- crashes when clicking *Close* in the open folder dialogue box

# DONE
- when displaying image check if there is any registred custom label in its exif / metadata
- create user dialog box
- toggle delete marking
- clean code
    - split everything in modules
    - respect python coding style (naming, etc.)
    - make constants for keys (no int, string etc.)
- persist labelings on media files
   41729: {'name': 'SceneType', 'type': TYPES.Undefined},
    - don't write tags directly into photos, use integers instead
        - keep a security association table (integer --> string)
- images are displayed only in landscape mode but they exist as portrait too
    - file explorer vs media manager comparison
- rotate pics
    - save as overwrite
- media support:
    - .mpo, png, jpeg
- autorotate based on image orientation exif data
- improve quality issue at rotation
- remove existing label if same key is pressed
- image not dispalyed fully in the box
- do something after moving operation
- fix huge .jpg quality loss at rotation
- open folder instead of media in folder
- verify if date remains the same
    - some weird shit happens: date changes if file moved to file_manager folder - check that out
- logging
    - replace print with logging
    - log most of the steps you do