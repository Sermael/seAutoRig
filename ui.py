# -*- coding: utf-8 -*-
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

from .scripts import guides
from .scripts import builder
from .scripts import project

importlib.reload(guides)
importlib.reload(builder)
importlib.reload(project)

main_path = project.main_path
assets_path = '{}/assets/'.format(main_path)


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):

        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            if sys.version_info.major >= 3:
                workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
                widget_ptr = int(getCppPointer(self.widget)[0])
            else:
                workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
                widget_ptr = long(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self):
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label):
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self):
        return cmds.workspaceControl(self.name, q=True, collapse=True)


class AutoRig(QtWidgets.QWidget):
    WINDOW_TITLE = 'Character Manager'
    UI_NAME = 'CharacterManager'
    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    selected_filter = "All Files (*.*)"

    @classmethod
    def get_workspace_control_name(cls):
        return "{}WorkspaceControl".format(cls.UI_NAME)

    def __init__(self):
        super(AutoRig, self).__init__()

        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setMinimumWidth(426)
        self.setMinimumHeight(750)
        self.setAutoFillBackground(True)

        # set qss file
        qss_file = QtCore.QFile(
            'C:/Users/e_che/Documents/maya/2020/scripts/seAutoRig/templates/manjaroMix.qss')
        if not qss_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return
        qss = QtCore.QTextStream(qss_file)
        # setup stylesheet
        self.setStyleSheet(qss.readAll())

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.create_workspace_control()

    def create_widgets(self):
        self.name_lab = QtWidgets.QLabel()
        self.name_lab.setText('Character Manager')
        self.name_lab.setFont(QtGui.QFont('Arial Black', 13))
        # self.name_lab.setStyleSheet("font-weight: bold; color: white;")
        # self.name_lab.move(200, 0)
        # self.name_lab.resize(60, 60)
        self.name_lab.setAlignment(QtCore.Qt.AlignCenter)

        self.tree = QtWidgets.QTreeView()
        self.tree.setMinimumWidth(400)
        self.tree.setMinimumHeight(50)

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(assets_path)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(assets_path))
        # self.tree.setSortingEnabled(True)

        self.thumbnail = QtWidgets.QLabel()
        self.thumbnail.setAlignment(QtCore.Qt.AlignBottom)
        self.img = "{}/templates/header.jpg".format(main_path)
        self.pix_map = QtGui.QPixmap(self.img)
        self.thumbnail.setPixmap(self.pix_map.scaled(400, 225))
        self.thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.thumbnail.setScaledContents(True)

        self.new_scene_btn = QtWidgets.QPushButton('New Scene')
        self.open_btn = QtWidgets.QPushButton('Open')
        self.import_btn = QtWidgets.QPushButton('Import')
        self.reference_btn = QtWidgets.QPushButton('Reference')
        self.delete_btn = QtWidgets.QPushButton('Delete')

        self.line = QtWidgets.QFrame()
        self.line.setGeometry(QtCore.QRect(150, 150, 118, 3))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.line_end = QtWidgets.QFrame()
        self.line_end.setGeometry(QtCore.QRect(150, 150, 118, 3))
        self.line_end.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_end.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_end.setObjectName("line_end")

        self.char_lab = QtWidgets.QLabel()
        self.char_lab.setText('Auto Rig')
        self.char_lab.setFont(QtGui.QFont('Arial Black', 13))
        # self.char_lab.setStyleSheet("font-weight: bold; color: white;")
        self.char_lab.setAlignment(QtCore.Qt.AlignCenter)
        self.spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self.new_btn = QtWidgets.QPushButton('Create')
        self.new_btn.setMinimumWidth(95)
        self.name_le = QtWidgets.QLineEdit()
        self.name_le.setText('New')
        self.geo_btn = QtWidgets.QPushButton('Geo')
        self.geo_btn.setMinimumWidth(300)
        self.save_geo_btn = QtWidgets.QPushButton('Save Geo')
        self.guides_btn = QtWidgets.QPushButton('Guides')
        self.guides_btn.setMinimumWidth(300)
        self.save_guides_btn = QtWidgets.QPushButton('Save Guides')
        self.rig_btn = QtWidgets.QPushButton('Rig')
        self.rig_btn.setMinimumWidth(300)
        self.save_rig_btn = QtWidgets.QPushButton('Save Rig')
        self.skin_btn = QtWidgets.QPushButton('Skin Selected Meshes')
        self.cancel_btn = QtWidgets.QPushButton('Close')

        self.autor = QtWidgets.QLabel()
        self.autor.setText("© 2023 Sergio Efigenio. All Rights Reserved.")
        self.autor.setAlignment(QtCore.Qt.AlignCenter)

        self.email = QtWidgets.QLabel()
        self.email.setText("sermael.efigenio@gmail.com")
        self.email.setAlignment(QtCore.Qt.AlignCenter)

    def create_layouts(self):
        title_layout = QtWidgets.QVBoxLayout()
        title_layout.addWidget(self.name_lab)

        tree_layout = QtWidgets.QHBoxLayout()
        tree_layout.addWidget(self.tree)

        img_layout = QtWidgets.QVBoxLayout()
        img_layout.addWidget(self.thumbnail)

        open_layout = QtWidgets.QHBoxLayout()
        open_layout.addWidget(self.new_scene_btn)
        open_layout.addWidget(self.open_btn)
        open_layout.addWidget(self.import_btn)
        open_layout.addWidget(self.reference_btn)
        open_layout.addWidget(self.delete_btn)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('Name: ', self.name_le)

        new_layout = QtWidgets.QHBoxLayout()
        new_layout.addLayout(form_layout)
        new_layout.addWidget(self.new_btn)

        button_layout = QtWidgets.QVBoxLayout()

        geo_layout = QtWidgets.QHBoxLayout()
        geo_layout.addWidget(self.geo_btn)
        geo_layout.addWidget(self.save_geo_btn)
        button_layout.addLayout(geo_layout)

        guides_layout = QtWidgets.QHBoxLayout()
        guides_layout.addWidget(self.guides_btn)
        guides_layout.addWidget(self.save_guides_btn)
        button_layout.addLayout(guides_layout)

        rig_layout = QtWidgets.QHBoxLayout()
        rig_layout.addWidget(self.rig_btn)
        rig_layout.addWidget(self.save_rig_btn)
        button_layout.addLayout(rig_layout)

        button_layout.addWidget(self.line_end)
        # button_layout.addWidget(self.skin_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(img_layout)

        main_layout.addLayout(tree_layout)
        main_layout.addLayout(open_layout)
        main_layout.addWidget(self.line)

        main_layout.addWidget(self.char_lab)
        main_layout.addLayout(new_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.autor)
        main_layout.addWidget(self.email)

    def create_connections(self):
        self.tree.clicked.connect(self.display_image)
        self.new_scene_btn.clicked.connect(self.new_scene)
        self.open_btn.clicked.connect(self.open_file)
        self.import_btn.clicked.connect(self.import_file)
        self.reference_btn.clicked.connect(self.reference_file)
        self.delete_btn.clicked.connect(self.delete)

        self.new_btn.clicked.connect(self.new_character)
        self.geo_btn.clicked.connect(self.new_geo)
        self.save_geo_btn.clicked.connect(self.save_geo)
        self.guides_btn.clicked.connect(self.guides)
        self.save_guides_btn.clicked.connect(self.save_guides)
        self.rig_btn.clicked.connect(self.builder)
        self.save_rig_btn.clicked.connect(self.save_rig)
        self.cancel_btn.clicked.connect(self.close)

    def create_workspace_control(self):
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        self.workspace_control_instance.create(self.WINDOW_TITLE, self)

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

    def snapshot(self):
        self.index = self.tree.selectedIndexes()[0]
        self.path = self.tree.model().filePath(self.index)
        self.name = self.tree.model().fileName(self.index)
        self.char = self.name_le.text()

        self.img = "{}{}/preview/{}".format(assets_path, self.char, self.name[:-3] + '_prev.jpg')

        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        cmds.playblast(st=1, et=1, v=0, fmt="image", qlt=100, p=100, w=1920, h=1080, cf=self.img)

        self.display_image()

    def open_file(self):
        scene_nodes = cmds.ls(type='transform', sl=True)
        rigs = []
        for rig in scene_nodes:
            if cmds.attributeQuery('rig', node=rig, ex=True):
                rigs.append(rig)

        index = self.tree.selectedIndexes()[0]
        info = self.tree.model().fileInfo(index)
        name = self.tree.model().fileName(index).split("_")[0]

        self.name_le.setText(name)
        save_scene = self.save_scene_msg()
        if save_scene == 'Save':
            gsf = self.get_save_file_name()
            if gsf:
                cmds.file(info.absoluteFilePath(), o=True, f=True)
        elif save_scene == 'NotSave':
            cmds.file(info.absoluteFilePath(), o=True, f=True)
        elif save_scene == 'Cancel':
            pass

    def import_file(self):
        index = self.tree.selectedIndexes()[0]
        info = self.tree.model().fileInfo(index)
        print(info.absoluteFilePath())
        cmds.file(info.absoluteFilePath(), i=True)

    def reference_file(self):
        index = self.tree.selectedIndexes()[0]
        info = self.tree.model().fileInfo(index)
        print(info.absoluteFilePath())
        cmds.file(info.absoluteFilePath(), r=True)

    def new_scene(self):
        save_scene = self.save_scene_msg()
        if save_scene == 'Save':
            gsf = self.get_save_file_name()
            if gsf:
                cmds.file(f=True, new=True)
        elif save_scene == 'NotSave':
            cmds.file(f=True, new=True)
        elif save_scene == 'Cancel':
            pass

    def delete(self):
        index = self.tree.selectedIndexes()[0]
        msg = QtWidgets.QMessageBox.question(
            self, "Delete Character", "Delete {}?".format(self.tree.model().fileName(index)))

        if msg == QtWidgets.QMessageBox.Yes:
            if not "." in self.tree.model().fileName(index):
                file = self.tree.model().filePath(index)
                shutil.rmtree(file)
            else:
                file = self.tree.model().filePath(index)
                os.remove(file)
        else:
            pass

    def new_character(self):
        char_name = self.name_le.text()
        char_dir = os.path.join(assets_path, char_name)
        char_model_dir = os.path.join(assets_path, char_name, 'geo')
        char_guides_dir = os.path.join(assets_path, char_name, 'guides')
        char_rig_dir = os.path.join(assets_path, char_name, 'rigs')
        preview = os.path.join(assets_path, char_name, 'preview')

        os.mkdir(char_dir)
        os.mkdir(char_model_dir)
        os.mkdir(char_guides_dir)
        os.mkdir(char_rig_dir)
        os.mkdir(preview)

        file_attr_hidden = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(preview, file_attr_hidden)

        self.tree.setCurrentIndex(self.model.index(assets_path + char_name))

    def new_geo(self):
        scene_nodes = cmds.ls(type='transform', sl=True)
        geos = []
        for geo in scene_nodes:
            if 'model_grp' in geo:
                geos.append(geo)

        save_scene = self.save_scene_msg()
        if save_scene == 'Save':
            gsf = self.get_save_file_name()
            if gsf:
                file = self.get_open_file_name()
                if file:
                    cmds.file(f=True, new=True)
                    cmds.file(file, i=True, f=True)
        elif save_scene == 'NotSave':
            cmds.file(f=True, new=True)
            file = self.get_open_file_name()
            cmds.file(file, i=True, f=True)
        elif save_scene == 'Cancel':
            pass

    def save_geo(self):
        name = self.name_le.text()
        geo = builder.Builder(moduleName=name)
        geo.save_geo()
        cmds.select(cl=True)

        self.tree.selectionModel().clear()
        selection_model = self.tree.selectionModel()
        path = '{}{}/geo/{}_geo.mb'.format(assets_path, name, name)
        index_model = self.model.index(path)

        selection = QtCore.QItemSelection(index_model, index_model)
        selection_model.select(selection, QtCore.QItemSelectionModel.Select)

        self.snapshot()

    def guides(self):
        name = self.name_le.text()
        default_guides = guides.Guides(characterName=name)
        default_guides.create_guides()
        cmds.select(cl=True)

    def save_guides(self):
        name = self.name_le.text()
        save_guides = guides.Guides(characterName=name)
        save_guides.save_guides()
        cmds.select(cl=True)

        self.tree.selectionModel().clear()
        selection_model = self.tree.selectionModel()
        path = '{}{}/guides/{}_guides.mb'.format(assets_path, name, name)
        index_model = self.model.index(path)

        selection = QtCore.QItemSelection(index_model, index_model)
        selection_model.select(selection, QtCore.QItemSelectionModel.Select)

        self.snapshot()

    def builder(self):
        name = self.name_le.text()
        char = builder.Builder(moduleName=name)
        char.rig()
        cmds.select(cl=True)

    def save_rig(self):
        name = self.name_le.text()
        char = builder.Builder(moduleName=name)
        char.save_rig()
        cmds.select(cl=True)

        self.tree.selectionModel().clear()
        selection_model = self.tree.selectionModel()
        path = '{}{}/rigs/{}_rig.mb'.format(assets_path, name, name)
        index_model = self.model.index(path)

        selection = QtCore.QItemSelection(index_model, index_model)
        selection_model.select(selection, QtCore.QItemSelectionModel.Select)

        self.snapshot()

    def save_model(self):
        name = self.name_le.text()
        char = builder.Builder(moduleName=name)
        char.save_geo()
        cmds.select(cl=True)

        self.tree.selectionModel().clear()
        selection_model = self.tree.selectionModel()
        path = '{}{}/geo/{}_rig.mb'.format(assets_path, name, name)
        index_model = self.model.index(path)

        selection = QtCore.QItemSelection(index_model, index_model)
        selection_model.select(selection, QtCore.QItemSelectionModel.Select)

    @staticmethod
    def save_scene_msg():
        name = cmds.file(q=True, sn=True)
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle('Warning: Scene Not Saved')
        msg_box.setText('save changes to scene {}?'.format(name))
        save_btn = msg_box.addButton('Save', QtWidgets.QMessageBox.YesRole)
        not_btn = msg_box.addButton("Don't Save", QtWidgets.QMessageBox.NoRole)
        cancel_btn = msg_box.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
        msg_box.exec_()
        save_scene = 'Save'
        if msg_box.clickedButton() == not_btn:
            save_scene = 'NotSave'
        elif msg_box.clickedButton() == cancel_btn:
            save_scene = 'Cancel'
        return save_scene

    def get_save_file_name(self):
        name = cmds.file(q=True, sn=True)
        file_path, self.selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File As", name, self.FILE_FILTERS, self.selected_filter)
        if file_path:
            return True

    def get_open_file_name(self):
        name = cmds.file(q=True, sn=True)
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open", name, self.FILE_FILTERS, self.selected_filter)
        if file_path:
            return file_path

# if __name__ == "__main__":
#     workspace_control_name = BipedRig.get_workspace_control_name()
#     if cmds.window(workspace_control_name, exists=True):
#         cmds.deleteUI(workspace_control_name)
#
#     biped_rig = BipedRig()
#     biped_rig.show()
