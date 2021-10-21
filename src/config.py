CONFIG_FILE_PATH = "config/config.json"
LABELS_TABLE_FILE_PATH = "config/table.json"

EXIF_LABEL_TAG_CODE = 532
EXIF_ORIENTATION_TAG_CODE = 274
EXIF_DATETIME_TAG_CODE = 36867

TO_DELETE_LABEL_TEXT = "TO DELETE"
EMPTY_LABEL_TEXT = ""

LABEL_NAME = "name"
LABEL_SHORTCUT = "shortcut"
LABEL_FOLDER_PATH = "folderPath"

FOLDER_BROWSE_ROOT_PATH = ""

VALID_IMAGE_EXTENSIONS = (".jpeg", ".jpg", ".png")

CHANGED_MEDIA_SIZE_THRESHOLD = 32  # percentage

################################################################################################
'''
the 1st IFD, contains a thumbnail image’s attribute information

34853	0x8825	GPS IFD	A pointer to the Exif-related GPS Info IFD
34665	0x8769	Exif IFD	A pointer to the Exif IFD.
40965	0xA005	Interoperability IFD	A pointer to the Exif-related Interoperability IFD.
'''
POSSIBLE_ROTATION_EMPTIED_SECTION = '1st->'
POSSIBLE_ROTATION_DIFFERENT_FIELD = ['0th->34853', '0th->34665', 'Exif->40965', '->thumbnail']
# 34853

MANDATORY_EXIF_LABEL_UPDATE_FIELD = '0th->532'
POSSIBLE_EXIF_LABEL_UPDATE_DIFFERENT_FIELD = ['0th->34853', '0th->34665', 'Exif->40965', '1st->513']

# VALID_EXIF_CHANGES =
################################################################################################
