import os

import sys
import shutil
import ctypes
import importlib
import maya.OpenMayaUI as omui
import maya.cmds as cmds

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
from shiboken6 import getCppPointer

from . import guides
from . import builder
from . import project

importlib.reload(guides)
importlib.reload(builder)
importlib.reload(project)

main_path = project.main_path
assets_path = '{}/assets/'.format(main_path)

def display_image(self):
    index = self.tree.selectedIndexes()[0]
    path = self.tree.model().filePath(self.index)
    name = self.tree.model().fileName(self.index)

    self.parent_name = self.tree.model().fileName(self.index.parent())

    if os.path.isfile(self.path):
        self.char = os.path.split(os.path.dirname(self.path))[-2]
        self.img = "{}/preview/{}_prev.jpg".format(self.char, self.name[:-3])
    elif os.path.isdir(self.path):
        if self.parent_name == 'assets':
            self.img = "{}{}/preview/{}_geo_prev.jpg".format(assets_path, self.name, self.name)
        else:
            self.char = os.path.split(os.path.dirname(self.path))[-1]
            self.img = "{}{}/preview/{}_geo_prev.jpg".format(assets_path, self.char, self.char)

    self.pix_map = QtGui.QPixmap(self.img)
    self.thumbnail.setPixmap(self.pix_map.scaled(400, 225))
    self.thumbnail.setScaledContents(True)

