import logging

class CurrentMedia:

    def __init__(self, index, pixmap):

        logging.debug("Initialised new current media object")

        self.index = index
        self.original_pixmap = pixmap
        self.edited_pixmap = pixmap
        self.rotation = 0

    def set_pixmap(self, pixmap):

        logging.debug("Set pixmap on current media object")

        self.original_pixmap = pixmap
        self.edited_pixmap = pixmap
