import os

import sys
import shutil
import ctypes
import importlib
import maya.OpenMayaUI as omui
import maya.cmds as cmds

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import getCppPointer

import scripts.guides as guides
import scripts.builder as builder
import scripts.project as project

importlib.reload(guides)
importlib.reload(builder)
importlib.reload(project)

main_path = project.main_path
assets_path = '{}/assets/'.format(main_path)

def display_image(self):
    self.index = self.tree.selectedIndexes()[0]
    self.path = self.tree.model().filePath(self.index)
    self.name = self.tree.model().fileName(self.index)

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
