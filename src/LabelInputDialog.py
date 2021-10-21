from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import logging

from src import config


class LabelInputDialog(QDialog):
    CUSTOM_FOLDER_BROWSER_PATH = None

    NEW_LABEL_REQUIRED_FIELDS = (
        config.LABEL_NAME
        , config.LABEL_SHORTCUT
        , config.LABEL_FOLDER_PATH
    )

    DELETED_LABEL_ENTRY = "deleted_label_entry"
    STATUS = None

    def __init__(self, parent=None):

        logging.debug("Initialising label input dialog")

        super().__init__(parent)

        self.labelName = QLineEdit(self)
        self.labelShortcut = QLineEdit(self)

        self.labelFolderPath = QLabel(self)
        # self.labelFolderPath.setText("no path selected")

        self.labelPathBrowseButton = QPushButton(self)
        self.labelPathBrowseButton.setText("...")
        self.labelPathBrowseButton.clicked.connect(self.browse_folder)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.Discard, self);

        layout = QFormLayout(self)
        layout.addRow("name", self.labelName)
        layout.addRow("shortcut (letter)", self.labelShortcut)
        layout.addRow("folder path", self.labelFolderPath)
        layout.addRow("Browse", self.labelPathBrowseButton)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.close)
        buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.discard_clicked)

    def discard_clicked(self):
        logging.debug("Discard button clicked")
        self.STATUS = self.DELETED_LABEL_ENTRY
        self.close()

    def set_label_values(self, name, shortcut, folder_path):
        self.labelName.setText(name)
        self.labelShortcut.setText(shortcut)
        self.labelFolderPath.setText(folder_path)
        self.CUSTOM_FOLDER_BROWSER_PATH = folder_path

    def get_inputs(self):

        dialog_inputs = {
            config.LABEL_NAME: self.labelName.text()
            , config.LABEL_SHORTCUT: self.labelShortcut.text()
            , config.LABEL_FOLDER_PATH: self.labelFolderPath.text()
        }

        # it is required that all label input fields to be filled
        if (
                all(field_key in dialog_inputs for field_key in self.NEW_LABEL_REQUIRED_FIELDS)
                and all(field_value != "" for field_value in list(dialog_inputs.values()))
        ):
            logging.debug("Valid label dialog inputs. All fields filled")
            return dialog_inputs
        else:
            logging.debug("Invalid input. Not all fields filled")
            None

    def browse_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self
            , "Select Label Folder"
            , config.FOLDER_BROWSE_ROOT_PATH if self.CUSTOM_FOLDER_BROWSER_PATH is None
            else self.CUSTOM_FOLDER_BROWSER_PATH
            , QFileDialog.ShowDirsOnly
        )

        logging.debug(f"Selected folder path: {folder_path}")

        self.labelFolderPath.setText(folder_path)
