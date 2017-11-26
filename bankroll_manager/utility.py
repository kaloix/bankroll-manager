from PyQt5.QtWidgets import QComboBox


class Object(object):
    pass


class QComboBox_(QComboBox):
    """ This class adds Qt5 features. First, the signal currentTextChanged is
    forwarded to currentIndexChanged while providing index to text conversion
    for the target function. Similarly, setCurrentText is forwarded to
    setCurrentIndex.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentTextChanged = Object()
        self.currentTextChanged.connect = lambda func: \
            self.currentIndexChanged.connect(lambda index:
                                             func(self.itemText(index)))

    def setCurrentText(self, text):
        self.setCurrentIndex(self.findText(text))
