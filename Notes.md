# For release:
- difficulties on label removal
- before / after move integrity check
    1. keep backup of processed photo
    2. check for integrity
    3. delete original photos if everything alright
- real-case testing on unsorted images
    - sort lots of images
    - same media size after moving without any changes
    - see img.verify() thing what effects does it have
- verifying media changes integrity before saving
- safe toggle between 'TO DELETE' and registered labels
- new method for inserting updated exif in JPEG, JPG and MPO files without creating a new file

# General testing methods:
- support for new format:
    - display (portrait / landscape)
        - conversion to pixmap
    - save changes (rotation)
        - similar quality
        - exif (if present), kept
    - test if you can  write custom exif data in it

# TESTS
    - to ensure quality of the media is not touched throughout features developments
    - no exif is lost
    - OS independent