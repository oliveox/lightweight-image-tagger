import logging
import ntpath
import os
import shutil
import piexif
from PIL import Image, JpegImagePlugin
from enum import Enum
import traceback
import sys

from src import config


class OperationTypes(Enum):
    ROTATION = "rotation"
    EXIF_LABEL_UPDATE = "exif_update"
    ROTATION_AND_EXIF_LABEL_UPDATE = "rotation_and_exif_update"


def save_changes(media_object, pixmap_rotation, exif_update):
    if exif_update or pixmap_rotation:
        backup_file_path = create_backup_media_file(media_object.filePath)
        operation = None

        if pixmap_rotation and exif_update:
            save_rotation_and_exif(media_object, exif_update, pixmap_rotation)
            operation = OperationTypes.ROTATION_AND_EXIF_LABEL_UPDATE
        elif pixmap_rotation:
            save_rotation(media_object, pixmap_rotation)
            operation = OperationTypes.ROTATION
        elif exif_update:
            save_exif(media_object, exif_update)
            operation = OperationTypes.EXIF_LABEL_UPDATE

        change_is_valid = check_media_changes(backup_file_path, media_object.filePath, operation)
        if change_is_valid:
            # change is valid, remove backup file
            try:
                os.remove(backup_file_path)
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                logging.error(f"Traceback: {traceback.print_exc()}")
                sys.exit("Exiting on unexpected error")

            return True
        else:
            logging.error(f"Invalid changes. Changes could not be saved to: {media_object.filePath}")

            # change not valid
            try:
                os.remove(media_object.filePath)  # remove original file
                os.rename(backup_file_path, media_object.filePath)  # rename backup file to original filename
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                logging.error(f"Traceback: {traceback.print_exc()}")
                sys.exit("Exiting on unexpected error")

            return False
    else:
        logging.warning(f"Media '{media_object.filePath}' doesn't have any changes to be saved")


def save_exif(media_object, new_exif_bytes):
    img = Image.open(media_object.filePath)
    image_format = img.format
    image_path = media_object.filePath

    if image_format in ["JPEG", "JPG", "MPO"]:
        piexif.insert(new_exif_bytes, image_path)  # not supported for .PNG
    elif image_format == "PNG":
        img.save(image_path
                 , format=image_format
                 , exif=new_exif_bytes
                 , quality='keep'
                 , compress_level=9  # png param
                 )
    else:
        logging.error(f"Can't update image exif! Path: {image_path}. Reason: Unknown image format: {image_format}.")

    logging.info(f"Updated image file exif. Path: {image_path}")

    img.close()


def save_rotation(media_object, img_rotated):
    image_path = media_object.filePath
    img = Image.open(image_path)

    # gotta preserve the original image exif
    original_image_exif = None
    try:
        exif_dict = piexif.load(img.info["exif"])

        # thumbnail must rotate too, thus --> don't preserve the original (not rotated one)
        exif_dict.pop('thumbnail', None)

        original_image_exif = piexif.dump(exif_dict)
    except KeyError:
        logging.warning(f"Image doens't have EXIF: {image_path}")

    image_format = img_rotated.format

    # TODO - same save settings for both JPEG and MPO ?
    if image_format in ["JPEG", "JPG"]:
        quantization = img.quantization
        subsampling = JpegImagePlugin.get_sampling(img)

        # compare parameters combinations with a tool
        img_rotated.save(image_path
                         , format=image_format
                         , exif=original_image_exif
                         , qtables=quantization
                         , subsampling=subsampling
                         # , subsampling=0 # PIL will also use subsampling technique to reduce the image size. You can use subsampling=0 to turn off this feature
                         # , quality='keep'
                         , quality=95
                         # , optimize=True # JPEG param
                         )

    elif image_format == "MPO":
        """
        MPO is pretty similar to JPEG, there's an exif tag that determines it, and then there's a bit extra in the data.

        -------------------------
        from PIL import JpegImagePlugin
        JpegImagePlugin._getmp = lambda x: None

        before importing any images, you'd never get an MPO file out of it.

        Tested method: it gets the first frame of the MPO
        -------------------------------

        My MPO camera files:
        - first frame: large resolution, a lot of exif data, thumbnail
        - second frame: small resolution, verry little exif data, no thumbnail

        """

        quantization = img.quantization
        subsampling = JpegImagePlugin.get_sampling(img)

        # compare parameters combinations with a tool
        img_rotated.save(image_path
                         , format=image_format
                         , exif=original_image_exif
                         , qtables=quantization
                         , subsampling=subsampling
                         # , subsampling=0 # PIL will also use subsampling technique to reduce the image size. You can use subsampling=0 to turn off this feature
                         , quality=95  # 'keep' doesn't work on non-JPEG files
                         )

    elif image_format == "PNG":
        img_rotated.save(image_path
                         , format=image_format
                         , exif=original_image_exif
                         , quality='keep'
                         , compress_level=9  # png param
                         )
    else:
        logging.error(
            f"Can't save rotation to image file! Path: {image_path}. Reason: Unknown image format: {image_format}.")

    logging.info(f"Updated image file rotation. Path: {image_path}")

    img.close()
    img_rotated.close()


def save_rotation_and_exif(media_object, exif_data, img_rotated):
    img = Image.open(media_object.filePath)
    image_path = media_object.filePath

    image_format = img.format
    img_rotated.format = image_format

    # TODO - same save settings for both JPEG and MPO ?
    if image_format in ["JPEG", "JPG"]:
        quantization = img.quantization
        subsampling = JpegImagePlugin.get_sampling(img)

        # compare parameters combinations with a tool
        img_rotated.save(image_path
                         , format=image_format
                         , exif=exif_data
                         , qtables=quantization
                         , subsampling=subsampling
                         # , subsampling=0 # PIL will also use subsampling technique to reduce the image size. You can use subsampling=0 to turn off this feature
                         # , quality='keep'  # vs 95?
                         , quality=95
                         # , optimize=True # JPEG param
                         )

    elif image_format == "MPO":
        """
        MPO is pretty similar to JPEG, there's an exif tag that determines it, and then there's a bit extra in the data.

        -------------------------
        from PIL import JpegImagePlugin
        JpegImagePlugin._getmp = lambda x: None

        before importing any images, you'd never get an MPO file out of it.

        Tested method: it gets the first frame of the MPO
        -------------------------------

        My MPO camera files:
        - first frame: large resolution, a lot of exif data, thumbnail
        - second frame: small resolution, verry little exif data, no thumbnail

        """

        quantization = img.quantization
        subsampling = JpegImagePlugin.get_sampling(img)

        # compare parameters combinations with a tool
        img_rotated.save(image_path
                         , format=image_format
                         , exif=exif_data
                         , qtables=quantization
                         , subsampling=subsampling
                         # , subsampling=0 # PIL will also use subsampling technique to reduce the image size. You can use subsampling=0 to turn off this feature
                         , quality=95  # 'keep' doesn't work on non-JPEG files
                         )

    elif image_format == "PNG":
        img_rotated.save(image_path
                         , format=image_format
                         , exif=exif_data
                         , quality='keep'
                         , compress_level=9  # png param
                         )
    else:
        logging.error(f"Can't save rotation and exif to image file! "
                      f"Path: {image_path}. Reason: Unknown image format: {image_format}.")

    logging.info(f"Updated image rotation and exif. Path: {image_path}")

    img.close()
    img_rotated.close()


in_original_but_not_in_changed = None
different_fields = None


def check_media_changes(original_file_path, with_changes_file_path, operation):
    '''
    Requirments:
    - size stays relatively the same
    - exif
        - label section newly creation
        or
        - label section updated
    - rotation
        - exif changes are only in thumbnail related ones
    '''

    #########################################################################################################
    '''
    COMPARE FILE SIZE DIFFERENCE
    
    Regarding images, for now, the philosophy is: quality proportional to filesize. No exactly accurate but it's a start.
    Thus, make sure the difference between the original file and the one on which changes are applied is not that big 
    '''
    no_changes_file_size = os.path.getsize(original_file_path)
    with_changes_file_size = os.path.getsize(with_changes_file_path)

    # negative percentage is ok --> output size bigger
    percentage_difference = (no_changes_file_size - with_changes_file_size) / no_changes_file_size * 100
    if percentage_difference > config.CHANGED_MEDIA_SIZE_THRESHOLD:
        logging.error(f"Invalid save operation! File size difference (%) is too big: {percentage_difference}")
        return False
    #########################################################################################################

    '''
    COMPARE CHANGES IN IMAGES EXIF
    
    If there are differences between the original file and the one with the applied changes
    make sure:
       - the code of the exif fields that have distinct values ([differences]) are the ones listed in the 'config.py'
       - exif fields which are not transferred from the original file to the one with changes ('only_in_original') are 
           the one listed in 'config.py'
       - new exif fields that exist in the file with changes but not in the original file are listed in 'config.py'  
    '''
    global in_original_but_not_in_changed, different_fields
    in_original_but_not_in_changed = []
    different_fields = []

    original_image = Image.open(original_file_path)
    with_changes_image = Image.open(with_changes_file_path)

    input_exif = piexif.load(original_image.info["exif"]) if "exif" in original_image.info else None
    output_exif = piexif.load(with_changes_image.info["exif"]) if "exif" in with_changes_image.info else None

    if input_exif and output_exif:
        in_original_but_not_in_changed = []
        different_fields = []
        result = compare_exifs(input_exif, output_exif)
        only_in_original = result["only_in_first"]  # have ordered unique elements
        differences = result["differences"]

        in_original_but_not_in_changed = []
        different_fields = []
        result2 = compare_exifs(output_exif, input_exif)
        only_in_changed = result2["only_in_first"]
    else:
        only_in_original = None
        only_in_changed = None
        differences = None

    if operation == OperationTypes.ROTATION:
        if differences:  # meaning differences is not None and len(differences) > 0
            if not set(differences).issubset(config.POSSIBLE_ROTATION_DIFFERENT_FIELD):
                logging.error(f"Invalid rotation save operation."
                              f" There are unexpected Exif differences: {str(differences)}")
                return False
        if only_in_original:
            for item in set(only_in_original):
                if config.POSSIBLE_ROTATION_EMPTIED_SECTION not in item:
                    logging.error(f"Invalid rotation save operation. Lost exif field is not covered: {str(item)}")
                    return False

    if operation in [OperationTypes.EXIF_LABEL_UPDATE, OperationTypes.ROTATION_AND_EXIF_LABEL_UPDATE]:
        # verify for the EXIF LABEL SECTION UPDATE (which is mandatory if the operation is an exif label update)
        if not input_exif and output_exif:
            '''
            situation: 
            - input file had no exif
            - output file has exif because label tag has been put in it --> verify it is there
            '''
            try:
                output_exif["0th"][config.EXIF_LABEL_TAG_CODE]  # check the label tag was created
            except KeyError:
                logging.error(f"Invalid exif label update save operation."
                              f" Exif label section doesn't exist in changed file!")
                return False
        else:
            # label section is removed (label removal operation)
            if only_in_original:
                if len(only_in_original) > 1:
                    logging.error(f"Invalid exif label update save operation."
                                  f"More exif elements in changed file than expected: {str(only_in_changed)}")
                    return False
                else:
                    only_in_original = only_in_original[0]
                if only_in_original != config.MANDATORY_EXIF_LABEL_UPDATE_FIELD:
                    logging.error(f"Invalid exif label update save operation."
                                  f"The new label field is different than expected: {str(only_in_changed)}")
                    return False
            else:
                # label section is added
                if only_in_changed:
                    if len(only_in_changed) > 1:
                        logging.error(f"Invalid exif label update save operation."
                                      f"More exif elements in changed file than expected: {str(only_in_changed)}")
                        return False
                    else:
                        only_in_changed = only_in_changed[0]
                    if only_in_changed != config.MANDATORY_EXIF_LABEL_UPDATE_FIELD:
                        logging.error(f"Invalid exif label update save operation."
                                      f"The new label field is different than expected: {str(only_in_changed)}")
                        return False
                elif differences and config.MANDATORY_EXIF_LABEL_UPDATE_FIELD not in differences:
                    logging.error(f"Invalid exif label update save operation. "
                                  f"Exif label section doesn't appear in exif differences {str(differences)}")
                    return False

            # verify differences section doesn't contain anything else that allowed
            if not set(differences).issubset(config.POSSIBLE_EXIF_LABEL_UPDATE_DIFFERENT_FIELD):
                logging.error(f"Invalid exif label update save operation. "
                              f"There are unexpected Exif differences: {str(differences)}")
                return False
    return True


def create_backup_media_file(file_path):
    # create backup file in the same path

    dir_path, filename = ntpath.split(file_path)
    backup_filename = f"backup-{filename}"
    backup_file_path = os.path.join(dir_path, backup_filename)

    try:
        shutil.copyfile(file_path, backup_file_path)
    except shutil.SameFileError as e:
        logging.error(str(e))
    except OSError as e:
        logging.error(str(e))

    return backup_file_path


def compare_exifs(input_exif, output_exif, path=""):
    # is in input but not output
    for k in input_exif:
        if k not in output_exif:
            in_original_but_not_in_changed.append(f"{path}->{str(k)}")
        else:
            if type(input_exif[k]) is dict:
                if path == "":
                    path = str(k)
                else:
                    path += f"->{str(k)}"
                compare_exifs(input_exif[k], output_exif[k], path)
                path = ""
            else:
                if input_exif[k] != output_exif[k]:
                    different_fields.append(f"{path}->{str(k)}")
                    # path = ""
    return {
        "only_in_first": in_original_but_not_in_changed,
        "differences": different_fields
    }