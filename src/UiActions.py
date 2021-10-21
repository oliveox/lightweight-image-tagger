import json
import logging
import os
import shutil
import sys
from enum import Enum
from random import randrange

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QTableWidgetItem

from src import ChangeSaver
from src import config
from src import Utils
from src.CurrentMedia import CurrentMedia
from src.LabelInputDialog import LabelInputDialog
from src.MediaFile import MediaFile


class UiActions:

    def __init__(self, rendered_ui):
        self.media_objects_list = None
        self.current_media = None
        self.ui_renderer = rendered_ui
        self.media_folder = None

    def reset(self):
        self.media_objects_list = None
        self.current_media = None
        self.ui_renderer.mediaLabel.clear()  # clear displayed media
        self.ui_renderer.mediaFileLabel.clear()  # clear displayed media

    def open_folder_dialog(self):
        logging.info("Opened folder dialog")

        self.media_folder = QtWidgets.QFileDialog.getExistingDirectory(None
                                                                       , 'Select a folder:'
                                                                       , ""
                                                                       , QtWidgets.QFileDialog.ShowDirsOnly
                                                                       )

        logging.info(f"Selected folder path: {self.media_folder}")

        self.display_folder_contents(self.media_folder)

    def display_folder_contents(self, folder_path):

        self.reset()

        first_media = True
        self.media_objects_list = []  # make sure media file lists is reset and empty
        for f in os.listdir(folder_path):  # TODO - go recursive?

            if f.lower().endswith(config.VALID_IMAGE_EXTENSIONS):

                # create list of available media files
                full_media_file_path = os.path.join(folder_path, f)

                labels = Utils.get_labels_from_media(full_media_file_path)

                if isinstance(labels, list):
                    logging.error(f"Can't handle list of labels yet. Path {full_media_file_path}")
                    sys.exit()

                # TODO move the process of associating a label with a media object inside the MediaFile class
                if labels:
                    media_file_object = MediaFile(full_media_file_path, labels)
                else:
                    media_file_object = MediaFile(full_media_file_path)

                self.media_objects_list.append(media_file_object)

                if first_media:
                    self.update_displayed_media(0)  # always display first media file in the directory
                    first_media = False

    def update_displayed_media(self, media_index):

        # update currently displayed media object
        media_object = self.media_objects_list[media_index]

        pixmap = media_object.get_pixmap()
        pixmap = pixmap.scaled(
            self.ui_renderer.mediaLabel.width()
            , self.ui_renderer.mediaLabel.height()
            , QtCore.Qt.KeepAspectRatio
        )

        self.ui_renderer.mediaLabel.setPixmap(pixmap)

        self.current_media = CurrentMedia(media_index, pixmap)

        logging.info(f"Updated displayed image: '{media_object.filePath}'")

        # display media label
        if media_object.to_delete:
            media_label = config.TO_DELETE_LABEL_TEXT
        elif media_object.label:
            media_label = media_object.label
        else:
            media_label = config.EMPTY_LABEL_TEXT

        self.update_label_box(media_label)

    def update_label_box(self, media_label):
        displayed_label = media_label if media_label is not None else config.EMPTY_LABEL_TEXT
        self.ui_renderer.mediaFileLabel.setText(displayed_label)
        logging.info(f"Updated label box: '{displayed_label}'")

    def update_label_entry(self, item):
        # get available labels
        labels = Utils.get_available_labels()

        # get label entry
        clicked_row = item.row()

        # open editing dialog box
        label = labels[clicked_row]
        dialog = LabelInputDialog()
        dialog.set_label_values(
            label[config.LABEL_NAME]
            , label[config.LABEL_SHORTCUT]
            , label[config.LABEL_FOLDER_PATH]
        )

        if dialog.exec():  # if 'save' button is pressed

            # update config files with registered labels
            updated_label_data = dialog.get_inputs()
            # TODO - check if target directory path exists
            # TODO - check if any changes exist

            json_file = open(config.CONFIG_FILE_PATH, "r")
            config_data = json.load(json_file)
            json_file.close()

            logging.info(f"Updated label\n"
                         f" from: {config_data['labels'][clicked_row]}"
                         f" \n"
                         f" to: {updated_label_data}")

            # change values of the same entry
            config_data["labels"][clicked_row] = updated_label_data

            json_file = open(config.CONFIG_FILE_PATH, "w")
            json.dump(config_data, json_file)
            json_file.close()

            self.display_available_labels()

        elif dialog.STATUS is dialog.DELETED_LABEL_ENTRY:
            label_to_remove = dialog.get_inputs()
            self.delete_label_entry(label_to_remove)

    def display_available_labels(self):
        labels = Utils.get_available_labels()
        self.ui_renderer.tableWidget.setRowCount(0)

        for label in labels:
            name = label[config.LABEL_NAME]
            shortcut = label[config.LABEL_SHORTCUT]
            path = label[config.LABEL_FOLDER_PATH]

            row_position = self.ui_renderer.tableWidget.rowCount()
            self.ui_renderer.tableWidget.insertRow(row_position)

            self.ui_renderer.tableWidget.setItem(row_position, 0, QTableWidgetItem(name))
            self.ui_renderer.tableWidget.setItem(row_position, 1, QTableWidgetItem(shortcut))
            self.ui_renderer.tableWidget.setItem(row_position, 2, QTableWidgetItem(path))

        logging.debug("Displaying available labels")

    def delete_label_entry(self, label_data):
        if label_data is not None:
            json_file = open(config.CONFIG_FILE_PATH, "r")
            config_data = json.load(json_file)
            json_file.close()

            # change values of the same entry
            config_data["labels"].remove(label_data)

            json_file = open(config.CONFIG_FILE_PATH, "w")
            json.dump(config_data, json_file)
            json_file.close()

            logging.info(f"Deleted label: {label_data}")

            self.display_available_labels()

    def dispaly_previous_media_file(self):

        if self.current_media:

            current_media_index = self.current_media.index
            logging.debug(f"Current media index: '{current_media_index}'")

            # get previous filename
            if current_media_index == 0:
                current_media_index = len(self.media_objects_list) - 1
                logging.debug(f"Updating media index to the last one: {current_media_index}")
            else:
                current_media_index -= 1
                logging.debug(f"Updating media index to previous: {current_media_index}")

            self.update_displayed_media(current_media_index)

    def display_next_media_file(self):

        if self.current_media:

            current_media_index = self.current_media.index
            logging.debug(f"Current media index: '{current_media_index}'")

            # get next filename
            if current_media_index == len(self.media_objects_list) - 1:
                current_media_index = 0
                logging.debug(f"Updating media index to first one: {current_media_index}")
            else:
                current_media_index += 1
                logging.debug(f"Updating media index to next: {current_media_index}")

            self.update_displayed_media(current_media_index)

    def label_current_media(self, press_key):

        if self.current_media:
            labels = Utils.get_available_labels()

            for label in labels:
                if label[config.LABEL_SHORTCUT] == press_key:

                    logging.info(f"Registered label key pressed: '{press_key}'")

                    media_object = self.media_objects_list[self.current_media.index]

                    if media_object.label == label[config.LABEL_NAME]:
                        media_object.reset_label()
                        logging.info(f"Label removed. Label: {label[config.LABEL_NAME]}."
                                     f" Media path: {media_object.filePath}")
                    else:
                        media_object.label = label[config.LABEL_NAME]
                        media_object.mark_as_delete(False)
                        logging.info(f"Label applied. Label: {label[config.LABEL_NAME]}."
                                     f" Media path: {media_object.filePath}")

                    self.update_label_box(media_object.label)

    def rotate_image(self, direction):

        if self.current_media is not None:
            # check if image or video displayed

            image_pixmap = self.current_media.edited_pixmap
            transform = QTransform()

            if direction is RotateDirection.LEFT:
                transform.rotate(-90)
                self.current_media.rotation -= 90
                logging.info(f"Rotating current image 90 degrees to left")
            if direction is RotateDirection.RIGHT:
                transform.rotate(90)
                self.current_media.rotation += 90
                logging.info(f"Rotating current image 90 degrees  to right")

            rotated_image_pixmap = image_pixmap \
                .transformed(transform) \
                .scaled(self.ui_renderer.mediaLabel.width(), self.ui_renderer.mediaLabel.height(),
                        QtCore.Qt.KeepAspectRatio)
            self.current_media.edited_pixmap = rotated_image_pixmap
            self.display_pixmap(rotated_image_pixmap)

    def display_pixmap(self, pixmap):
        logging.debug("Updating displayed pixmap")
        self.ui_renderer.mediaLabel.setPixmap(pixmap)
        self.ui_renderer.mediaLabel.setAlignment(QtCore.Qt.AlignCenter)

    def create_new_label(self):
        # persist new label
        dialog = LabelInputDialog()

        if dialog.exec():  # if 'save' button is pressed

            # update config files with registered labels
            new_label_data = dialog.get_inputs()  # TODO - check if target directory path exists

            if new_label_data is not None:

                # update UI available labels
                json_file = open(config.CONFIG_FILE_PATH, "r")
                config_json = json.load(json_file)
                json_file.close()

                # check if label name is not already registered in current sessions
                if not new_label_data[config.LABEL_NAME] in [label[config.LABEL_NAME]
                                                             for label in config_json["labels"]]:

                    json_file = open(config.CONFIG_FILE_PATH, "w")
                    config_json["labels"].append(new_label_data)  # add data
                    json.dump(config_json, json_file)
                    json_file.close()

                    logging.info(f"New label registered in current session: {new_label_data}")

                    # update all ever registered labels
                    label_name = new_label_data[config.LABEL_NAME]
                    json_file = open(config.LABELS_TABLE_FILE_PATH, "r")
                    labels_table_json = json.load(json_file)
                    json_file.close()

                    # check if label already exists
                    try:
                        labels_table_json[label_name]
                        logging.warning(f"Label '{label_name}' already exists in labels table!")
                    except KeyError:
                        # get all already assigned integer numbers
                        registered_numbers = []
                        for key in config_json:
                            registered_numbers.append(config_json[key])

                        # generate unique integer
                        random_number = randrange(9999)
                        while random_number in registered_numbers:
                            random_number = randrange(9999)

                        labels_table_json[label_name] = random_number

                        json_file = open(config.LABELS_TABLE_FILE_PATH, "w")
                        json.dump(labels_table_json, json_file)
                        json_file.close()

                        logging.debug(f"Label '{label_name}' was not registered before. Registering it.")

                    self.display_available_labels()

                else:
                    logging.info(f"Label '{new_label_data[config.LABEL_NAME]}' "
                                 f"is already registered in the current session!")

    def save_media_changes_to_file(self):

        '''
        media changes types:

        !!! IT IS IMPORTANT TO APPLY CHANGES IN A SINGLE SAVE
        Multiple saves can compress the image more and more --> loss of quality

        - save rotation to physical file
        - label in exif
        '''

        if self.current_media is not None:
            media_object = Utils.get_media_object_by_current_media(self.media_objects_list, self.current_media)

            # rotation
            rotated_virtual_image = Utils.get_rotated_virtual_image(self.media_objects_list, self.current_media)

            # label to exif
            exif_update = Utils.get_label_exif_update(media_object)

            ChangeSaver.save_changes(media_object, rotated_virtual_image, exif_update)

    def apply_actions_on_media_folder(self):

        existing_labels = Utils.get_available_labels()

        for media_object in self.media_objects_list:

            if media_object.to_delete:
                try:
                    logging.info(f"Media {media_object.filePath} marked to delete. Attempting to delete it")
                    os.remove(media_object.filePath)
                except FileNotFoundError:
                    logging.error(f"File not deleted. It doesn't exist: {media_object.filePath}")
                except PermissionError:
                    logging.error(f"File not deleted. No permission: {media_object.filePath}")

            else:
                '''
                # update any label exif changes
                - label toggeled off (same label applied twice)
                - label changed
                '''

                label_exif_update = Utils.get_label_exif_update(media_object)
                if media_object.label \
                        and label_exif_update \
                        and ChangeSaver.save_changes(media_object, None, label_exif_update):

                    # move file only if a new label has been added to the media

                    source_file_path = media_object.filePath
                    target_folder_path = [
                        label[config.LABEL_FOLDER_PATH]
                        for label in existing_labels
                        if label[config.LABEL_NAME] == media_object.label
                    ][0]

                    if os.path.isdir(target_folder_path):
                        try:
                            shutil.move(source_file_path, target_folder_path)
                            logging.info(f"Moved {media_object.filePath} to {target_folder_path}")
                        except shutil.Error as e:
                            logging.error(f"File NOT moved! Error: {str(e)}")
                    else:
                        logging.error(f"File NOT moved. Target folder doesn't exist {target_folder_path}")

        # reopen initially opened folder
        self.display_folder_contents(self.media_folder)

    def toggle_media_delete_status(self):

        if self.current_media:
            media_object = self.media_objects_list[self.current_media.index]
            delete_status = media_object.to_delete
            delete_status = not delete_status

            media_object.mark_as_delete(delete_status)
            media_object.label = config.EMPTY_LABEL_TEXT if delete_status else media_object.label

            label_to_display = config.TO_DELETE_LABEL_TEXT if delete_status else config.EMPTY_LABEL_TEXT

            logging.debug(f"Toggled {config.TO_DELETE_LABEL_TEXT} on {media_object.filePath} to {delete_status}")

            self.update_label_box(label_to_display)


class RotateDirection(Enum):
    LEFT = 1
    RIGHT = 2
