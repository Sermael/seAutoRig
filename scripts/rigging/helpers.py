from PySide2 import QtGui, QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel
import pymel.core as pm

# QT WIndow!

Title = 'Corrective Joints'
Folder = 'correctives'
UI_File = 'CorrectiveJoints.ui'
ResourcesPath = Folder + '/Resources/'


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class UIName(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(UIName, self).__init__(parent)

        self.setWindowTitle(Title)
        self.setFixedSize(229, 271)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):

        UIPath = cmds.internalVar(usd=True) + Folder + '/'
        f = QtCore.QFile(UIPath + UI_File)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):

        '''
        self.ui.layout().setContentsMargins(3, 3, 3, 3)'''

        imagePath = cmds.internalVar(usd=True) + ResourcesPath
        self.ui.CreateCorrectiveJoint.setIcon(QtGui.QIcon(imagePath + 'CCJ_Buton.png'))

    def create_connections(self):

        self.ui.CreateCorrectiveJoint.clicked.connect(
            lambda: self.CorrectiveJoints(direction=self.ui.Direction.currentText(), axis=self.ui.Axis.currentText(),
                                          distance=self.ui.Distance.value(), amount=self.ui.Amount.value()))

        # self.ui.ButtonName.clicked.connect(self.Demo)
        # self.ui.ButtonName.clicked.connect(lambda: print 'this is lambda')

    import maya.cmds as cmds

    # selection = cmds.ls(selection=True)
    # get_position = cmds.xform(selection[0], q=1, t=True, ws=True)

    def CorrectiveJoints(self, direction, axis, distance, amount):

        selection = cmds.ls(selection=True)
        name = selection[0] + '_' + direction + axis
        get_position = cmds.xform(selection[0], q=1, t=True, ws=True)

        # Create Groups, Locators, Control and Joint

        global_grp = cmds.group(n=name + '_Corrective_Grp', em=True, w=True)
        local_grp = cmds.group(n=name + '_Loc_Grp', em=True, w=True)
        global_ctl_grp = cmds.group(n=name + '_Ctl_Grp', em=True, w=True)
        local_ctl_grp = cmds.group(n=name + '_Ctl_Off_Grp', em=True, w=True)
        surface_grp = cmds.group(n=name + '_Surf_Grp', em=True, w=True)
        create_ctl = cmds.circle(n=name + '_Corrective_Ctl', r=0.5)
        cmds.setAttr(create_ctl[0] + ".overrideEnabled", 1)
        cmds.setAttr(create_ctl[0] + ".overrideColor", 17)

        corrective_joint = cmds.joint(n=name + '_Corrective_Jnt', co=True)

        deselect = cmds.select(cl=True)
        base_loc = cmds.spaceLocator(n=name + '_Corrective_Base_Loc')
        front_loc = cmds.spaceLocator(n=name + '_Corrective_Front_Loc')
        up_loc = cmds.spaceLocator(n=name + '_Corrective_Up_Loc')

        # Parent Groups

        parent_ctl = cmds.parent(name + '_Corrective_Ctl', name + '_Ctl_Off_Grp')
        parent_ctl_grp = cmds.parent(local_ctl_grp, global_ctl_grp)
        parent_setup_grp = cmds.parent(local_grp, global_ctl_grp, global_grp)

        # Parent loc

        p_base_group = cmds.parent(base_loc, local_grp)
        p_locators = cmds.parent(front_loc, up_loc, base_loc)

        # create and connect angle between

        angle_between = cmds.createNode('angleBetween', n=name + '_angleBetween')
        conn_front_loc = cmds.connectAttr(name + '_Corrective_Front_Loc' + '.translate', angle_between + '.vector1')
        conn_up_loc = cmds.connectAttr(name + '_Corrective_Up_Loc' + '.translate', angle_between + '.vector2')

        # create and connect remap value

        create_remap_value_node = cmds.createNode('remapValue', n=selection[0] + '_' + direction + axis + '_remapValue')
        connect_remap = cmds.connectAttr(angle_between + '.angle', create_remap_value_node + '.inputValue')
        set_input_max = cmds.setAttr(create_remap_value_node + '.inputMax', 90)
        set_input_min = cmds.setAttr(create_remap_value_node + '.inputMin', 0)
        set_output_max = cmds.setAttr(create_remap_value_node + '.outputMax', 0)
        set_output_min = cmds.setAttr(create_remap_value_node + '.outputMin', 1)

        create_multiply_divide = cmds.shadingNode('multiplyDivide', asUtility=True,
                                                  n=selection[0] + '_' + direction + axis + '_multiplyDivide')

        connect_remap_to_multiplay = cmds.connectAttr(create_remap_value_node + '.outValue',
                                                      create_multiply_divide + '.i1x')
        connect_multiplay_to_ctl_grp = cmds.connectAttr(create_multiply_divide + '.ox',
                                                        local_ctl_grp + '.translate' + axis)

        # position all

        pos_global_grp = cmds.delete(cmds.parentConstraint(selection[0], global_grp, mo=0))
        pos_jnt = cmds.delete(cmds.parentConstraint(selection[0], corrective_joint, mo=0))

        if direction == 'Neg':

            if axis == 'X':
                move_global_ctl_grp = cmds.move(get_position[0] - distance, get_position[1], get_position[2],
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0] - distance, get_position[1], get_position[2], up_loc)
                move_front_locator = cmds.move(get_position[0], get_position[1] + distance, get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0] - distance, get_position[1], get_position[2],
                                                corrective_joint)

            if axis == 'Y':
                move_global_ctl_grp = cmds.move(get_position[0], get_position[1] - distance, get_position[2],
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0], get_position[1] - distance, get_position[2], up_loc)
                move_front_locator = cmds.move(get_position[0] + distance, get_position[1], get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0], get_position[1] - distance, get_position[2],
                                                corrective_joint)

            if axis == 'Z':
                move_global_ctl_grp = cmds.move(get_position[0], get_position[1], get_position[2] - distance,
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0], get_position[1], get_position[2] + distance, up_loc)
                move_front_locator = cmds.move(get_position[0] + distance, get_position[1], get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0], get_position[1], get_position[2] - distance,
                                                corrective_joint)

            set_multiplay = cmds.setAttr(create_multiply_divide + '.i2x', - amount)


        else:

            if axis == 'X':
                move_global_ctl_grp = cmds.move(get_position[0] + distance, get_position[1], get_position[2],
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0] + distance, get_position[1], get_position[2], up_loc)
                move_front_locator = cmds.move(get_position[0], get_position[1] + distance, get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0] + distance, get_position[1], get_position[2],
                                                corrective_joint)

            if axis == 'Y':
                move_global_ctl_grp = cmds.move(get_position[0], get_position[1] + distance, get_position[2],
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0], get_position[1] + distance, get_position[2], up_loc)
                move_front_locator = cmds.move(get_position[0] + distance, get_position[1], get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0], get_position[1] + distance, get_position[2],
                                                corrective_joint)

            if axis == 'Z':
                move_global_ctl_grp = cmds.move(get_position[0], get_position[1], get_position[2] + distance,
                                                global_ctl_grp)
                move_up_locator = cmds.move(get_position[0], get_position[1], get_position[2] - distance, up_loc)
                move_front_locator = cmds.move(get_position[0] + distance, get_position[1], get_position[2], front_loc)
                move_global_jnt_grp = cmds.move(get_position[0], get_position[1], get_position[2] + distance,
                                                corrective_joint)

            set_multiplay = cmds.setAttr(create_multiply_divide + '.i2x', amount)

        constraint_front_loc = cmds.parentConstraint(selection[0], front_loc, mo=1)
        # constraint_crorrective_jnt = cmds.parentConstraint(create_ctl, corrective_joint, mo=1)

        # create rivet

        create_nurb = cmds.nurbsPlane(n=name + '_Nurb', ax=(0, 0, 1))
        cmds.setAttr(create_nurb[0] + '.v', 0)
        move_nurb = cmds.delete(cmds.pointConstraint(selection[0], create_nurb, mo=0))
        freez_nurb = cmds.makeIdentity(create_nurb, apply=True, t=1, r=1, s=1, n=0)
        del_hist_nurb = cmds.delete(create_nurb, constructionHistory = True)
        create_locator = cmds.spaceLocator(n=selection[0] + '{}_Rivet_Loc'.format(name), a=True)
        point_on_surf_inf = cmds.shadingNode('pointOnSurfaceInfo', n=selection[0] + '_POSI', au=True)
        connect_surf = cmds.connectAttr((create_nurb[0]) + '.worldSpace', (point_on_surf_inf) + '.inputSurface',
                                        f=True)
        set_U = cmds.setAttr((point_on_surf_inf) + '.parameterU', 0.5)
        set_v = cmds.setAttr((point_on_surf_inf) + '.parameterV', 0.5)
        create_FBFM = cmds.shadingNode('fourByFourMatrix', n=selection[0] + '_FBFM', au=True)

        conn_tangentVx = cmds.connectAttr((point_on_surf_inf) + '.tangentVx', (create_FBFM) + '.in00', f=True)
        conn_tangentVy = cmds.connectAttr((point_on_surf_inf) + '.tangentVy', (create_FBFM) + '.in01', f=True)
        conn_tangentVz = cmds.connectAttr((point_on_surf_inf) + '.tangentVz', (create_FBFM) + '.in02', f=True)

        conn_tangentUx = cmds.connectAttr((point_on_surf_inf) + '.tangentUx', (create_FBFM) + '.in10', f=True)
        conn_tangentUy = cmds.connectAttr((point_on_surf_inf) + '.tangentUy', (create_FBFM) + '.in11', f=True)
        conn_tangentUz = cmds.connectAttr((point_on_surf_inf) + '.tangentUz', (create_FBFM) + '.in12', f=True)

        conn_normalX = cmds.connectAttr((point_on_surf_inf) + '.normalX', (create_FBFM) + '.in20', f=True)
        conn_normalY = cmds.connectAttr((point_on_surf_inf) + '.normalY', (create_FBFM) + '.in21', f=True)
        conn_normalZ = cmds.connectAttr((point_on_surf_inf) + '.normalZ', (create_FBFM) + '.in22', f=True)

        conn_positionX = cmds.connectAttr((point_on_surf_inf) + '.positionX', (create_FBFM) + '.in30', f=True)
        conn_positionY = cmds.connectAttr((point_on_surf_inf) + '.positionY', (create_FBFM) + '.in31', f=True)
        conn_positionZ = cmds.connectAttr((point_on_surf_inf) + '.positionZ', (create_FBFM) + '.in32', f=True)

        create_DCM = cmds.shadingNode('decomposeMatrix', n=selection[0] + '_DCM', au=True)
        conn_DCM = cmds.connectAttr((create_FBFM) + '.output', (create_DCM) + '.inputMatrix', f=True)

        conn_Translate = cmds.connectAttr((create_DCM) + '.outputTranslate', (create_locator[0]) + '.translate',
                                          f=True)
        conn_Rotate = cmds.connectAttr((create_DCM) + '.outputRotate', (create_locator[0]) + '.rotate', f=True)

        parent_nurb = cmds.parent(name + '_Nurb', surface_grp)
        parent_loc_riv = cmds.parent(create_locator, surface_grp)

        # constraint rivet locator to setup

        constraint_local_grp = cmds.parentConstraint(create_locator, local_grp, mo=1)
        constraint_global_ctl_grp = cmds.parentConstraint(create_locator, global_ctl_grp, mo=1)

        #skin surf

        get_parent = cmds.listRelatives(selection[0], p=True)
        get_children = cmds.listRelatives(selection[0], c=True)
        bind_surf = cmds.skinCluster(get_parent, get_children, name + '_Nurb', tsb = True, sm = 1, bm =1)

        for i in cmds.ls("*_Loc"):
            cmds.setAttr(i + ".v", 0)

        cmds.select(selection)

if __name__ == "__main__":

    try:
        UIName_ui.close()  # pylint: disable=E0601
        UIName_ui.deleteLater()
    except:
        pass
    UIName_ui = UIName()
    UIName_ui.show()