import json
import sys
import piexif
from PIL import Image
import logging

from src import config

def get_available_labels():
    logging.debug("Getting available labels from config file")

    with open(config.CONFIG_FILE_PATH) as json_file:
        data = json.load(json_file)
        json_file.close()

        return data["labels"]


def get_labels_from_media(file_path):
    # read exif section
    img = Image.open(file_path)
    has_exif = None
    label = None
    try:
        exif_dict = piexif.load(img.info["exif"])
        has_exif = True
    except KeyError:
        logging.warning(f"Image doens't have EXIF: {file_path}")

    if has_exif:
        try:
            existing_label_exif = exif_dict["0th"][config.EXIF_LABEL_TAG_CODE]
            logging.debug(f"Exif label section has data there. Image: {file_path}. Data: {existing_label_exif}")

            # get label acording to code
            for item in existing_label_exif:
                if isinstance(item, int):
                    label = get_label_name_by_code(existing_label_exif[1])
                    break
                else:
                    label = get_label_name_by_code(item[1])
                    break  # TOOD - handle list of labels

        except KeyError:
            logging.debug(f"Exif label section empty: {file_path}")

    return label


def get_label_name_by_code(code):
    # read labels table
    json_file = open(config.LABELS_TABLE_FILE_PATH, "r")
    labels = json.load(json_file)
    json_file.close()

    logging.debug(f"Searching label name for code '{code}'")

    for label in labels:
        if labels[label] == code:
            return label

    logging.error(f"Label code '{code}' is not registered")


def get_label_code_by_name(label_name):
    json_file = open(config.LABELS_TABLE_FILE_PATH, "r")
    config_file = json.load(json_file)
    json_file.close()

    try:
        code = config_file[label_name]
        return code
    except KeyError:
        logging.error(f"Label with name '{label_name}' is not registered!")
        sys.exit("Unexpected error!")


def get_media_object_by_current_media(media_objects_list, current_media):
    logging.debug("Fetching media objects of the current displayed media")
    return media_objects_list[current_media.index]


def get_rotated_virtual_image(media_objects_list, current_media):
    # see virtual changes done on the media
    # apply them on the original file
    # reset the virtual changes to zero
    if current_media.rotation != 0:
        media_object = get_media_object_by_current_media(media_objects_list, current_media)
        current_image_path = media_object.filePath
        image_required_rotation = current_media.rotation

        '''
        Get MPO format images to be read as JPEG (first frame taken)
        '''
        # JpegImagePlugin._getmp = lambda x: None
        img = Image.open(current_image_path)
        #
        # exif_bytes = None
        # try:
        #     exif_dict = piexif.load(img.info["exif"])
        #     exif_dict.pop('thumbnail', None)  # thumbnail must rotate too, thus --> not preserved
        #     exif_bytes = piexif.dump(exif_dict)
        # except KeyError:
        #     logging.warning(f"Image doens't have EXIF: {current_image_path}")

        # PIL rotation direction is opposed than pixmap
        im_rotated = img.rotate(-image_required_rotation, expand=True, resample=Image.BICUBIC)
        im_rotated.format = img.format
        img.close()

        logging.debug(f"Rotated current pixmap by {current_media.rotation} degrees")

        # TODO - no feedback if saving the rotation to file succeeded
        current_media.rotation = 0
        current_media.set_pixmap(current_media.edited_pixmap)

        return im_rotated

    logging.debug("Current pixmap doesn't have any rotation associated")
    return None


def get_exif_update2(media_object):
    label = media_object.label
    first_number = 0
    if label:

        label_code = (first_number, get_label_code_by_name(label))
        image_path = media_object.filePath

        img = Image.open(image_path)

        new_exif_bytes = None
        hasExif = False
        try:
            exif_dict = piexif.load(img.info["exif"])
            logging.debug(f"Image has exif: {image_path}")
            hasExif = True
        except KeyError:
            logging.warning(f"Image doens't have EXIF: {image_path}")

        if hasExif:
            try:
                existing_label_exif = exif_dict["0th"][config.EXIF_LABEL_TAG_CODE]
                logging.debug(f"Exif label section has data there! Image :{image_path}. Data: {existing_label_exif}")

                # check if current label code exists
                label_code_exists = False

                # first and only label code registered
                if len(existing_label_exif) == 2 and isinstance(existing_label_exif[0], int):
                    if label_code == existing_label_exif:
                        label_code_exists = True
                else:
                    for item in existing_label_exif:

                        if isinstance(item, int):
                            item = (first_number, item)

                        if item == label_code:
                            label_code_exists = True
                            break

                if not label_code_exists:
                    logging.info(f"Label '{label}' doesn't exist in image '{image_path}'. Writing it.")

                    updated_data_to_write = (label_code,) + (existing_label_exif,)
                    exif_dict["0th"][config.EXIF_LABEL_TAG_CODE] = updated_data_to_write
                    new_exif_bytes = piexif.dump(exif_dict)
            except KeyError:
                logging.debug(f"Exif label section empty. Writing label '{label}' to image ")
                exif_dict["0th"][config.EXIF_LABEL_TAG_CODE] = (label_code,)

                new_exif_bytes = piexif.dump(exif_dict)

        else:
            logging.debug(f"Creating exif to image {image_path}. Writing label exif to it")
            zeroth_ifd = {config.EXIF_LABEL_TAG_CODE: (label_code,)}
            exif_dict = {"0th": zeroth_ifd}

            new_exif_bytes = piexif.dump(exif_dict)

        return new_exif_bytes

    return None


def get_label_exif_update(media_object):
    label = media_object.label
    first_number = 0

    image_path = media_object.filePath
    img = Image.open(image_path)
    new_exif_bytes = None

    if "exif" in img.info:
        logging.debug(f"Image has exif: {image_path}")
        exif_dict = piexif.load(img.info["exif"])

        if config.EXIF_LABEL_TAG_CODE in exif_dict["0th"]:
            existing_label_exif = exif_dict["0th"][config.EXIF_LABEL_TAG_CODE]
            logging.debug(f"Exif label section has data there! Image :{image_path}. Data: {existing_label_exif}")

            if label:
                label_code = (first_number, get_label_code_by_name(label))

                # check if current label code exists
                label_code_already_exists = False

                # first and only label code registered
                if len(existing_label_exif) == 2 and isinstance(existing_label_exif[0], int):
                    if label_code == existing_label_exif:
                        label_code_already_exists = True
                else:
                    for item in existing_label_exif:

                        if isinstance(item, int):
                            item = (first_number, item)

                        if item == label_code:
                            label_code_already_exists = True
                            break

                if not label_code_already_exists:
                    logging.info(f"Label '{label}' doesn't exist in image '{image_path}'. Writing it.")

                    updated_data_to_write = (label_code,) + (existing_label_exif,)
                    exif_dict["0th"][config.EXIF_LABEL_TAG_CODE] = updated_data_to_write
                    new_exif_bytes = piexif.dump(exif_dict)
            else:
                # remove label from image
                exif_dict["0th"].pop(config.EXIF_LABEL_TAG_CODE, "None")
                new_exif_bytes = piexif.dump(exif_dict)
        elif label:
            logging.debug(f"Exif label section empty. Writing label '{label}' to image ")
            label_code = (first_number, get_label_code_by_name(label))
            exif_dict["0th"][config.EXIF_LABEL_TAG_CODE] = (label_code,)
            new_exif_bytes = piexif.dump(exif_dict)
    elif label:
        logging.warning(f"Image doens't have EXIF: {image_path}")
        logging.debug(f"Creating exif to image {image_path}. Writing label exif to it")
        label_code = (first_number, get_label_code_by_name(label))
        zeroth_ifd = {config.EXIF_LABEL_TAG_CODE: (label_code,)}
        exif_dict = {"0th": zeroth_ifd}
        new_exif_bytes = piexif.dump(exif_dict)

    return new_exif_bytes