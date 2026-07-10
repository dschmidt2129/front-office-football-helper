import os
import sys
import types
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class _Signal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class _Widget:
    def __init__(self, parent=None):
        self._parent = parent
        self._layout = None

    def setLayout(self, layout):
        self._layout = layout

    def parentWidget(self):
        return self._parent

    def setWindowTitle(self, _title):
        return None

    def setGeometry(self, *_args):
        return None

    def show(self):
        return None


class _Label(_Widget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _LineEdit(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""

    def setText(self, text):
        self._text = text

    def text(self):
        return self._text


class _PushButton(_Widget):
    def __init__(self, *_args, **_kwargs):
        super().__init__()
        self.clicked = _Signal()


class _TextEdit(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []

    def append(self, text):
        self.messages.append(text)

    def setText(self, text):
        self.messages = [text]

    def clear(self):
        self.messages = []

    def update(self):
        return None


class _ComboBox(_Widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._index = 0

    def addItems(self, items):
        self._items.extend(items)

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, index):
        self._index = index

    def currentText(self):
        if not self._items:
            return ""
        return self._items[self._index]


class _Layout:
    def __init__(self):
        self.items = []

    def addWidget(self, widget):
        self.items.append(widget)

    def addLayout(self, layout, *_args):
        self.items.append(layout)

    def addItem(self, item):
        self.items.append(item)


class _QFileDialog:
    ShowDirsOnly = 1

    @staticmethod
    def getExistingDirectory(*_args, **_kwargs):
        return ""


class _QSizePolicy:
    Minimum = 0
    Expanding = 1


class _QSpacerItem:
    def __init__(self, *_args, **_kwargs):
        return None


class _QApplication:
    def __init__(self, *_args, **_kwargs):
        return None

    @staticmethod
    def processEvents():
        return None

    def exec_(self):
        return 0


def _install_fake_pyqt5():
    qtwidgets = types.SimpleNamespace(
        QApplication=_QApplication,
        QWidget=_Widget,
        QLabel=_Label,
        QTextEdit=_TextEdit,
        QComboBox=_ComboBox,
        QPushButton=_PushButton,
        QHBoxLayout=_Layout,
        QVBoxLayout=_Layout,
        QLineEdit=_LineEdit,
        QFileDialog=_QFileDialog,
        QSpacerItem=_QSpacerItem,
        QSizePolicy=_QSizePolicy,
    )
    pyqt5 = types.SimpleNamespace(QtWidgets=qtwidgets)
    sys.modules.setdefault("PyQt5", pyqt5)
    sys.modules.setdefault("PyQt5.QtWidgets", qtwidgets)


_install_fake_pyqt5()


@pytest.fixture(autouse=True, scope="session")
def fake_pyqt5_module():
    return None


@pytest.fixture(autouse=True)
def add_project_to_sys_path():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def output_widget():
    class Output:
        def __init__(self):
            self.messages = []

        def append(self, value):
            self.messages.append(str(value))

        def setText(self, value):
            self.messages = [str(value)]

        def clear(self):
            self.messages = []

        def update(self):
            return None

    return Output()


@pytest.fixture
def temp_data_root(tmp_path):
    base = tmp_path / "fof"
    (base / "leaguedata" / "SFL00004").mkdir(parents=True)
    (base / "leagues" / "SFL00004").mkdir(parents=True)
    return base


@pytest.fixture
def in_temp_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path
