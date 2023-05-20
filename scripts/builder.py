"""
auto rig utils module
"""
import importlib
from maya import cmds
from .project import assets_path

from .rigging import extremity
from .rigging import spine
from .rigging import head
from .rigging import main
from .rigging import skin
from .rigging import fingers

importlib.reload(extremity)
importlib.reload(spine)
importlib.reload(head)
importlib.reload(main)
importlib.reload(skin)
importlib.reload(fingers)

model_file_path = '%s/%s/geo/%s_model.mb'
guides_scene_path = '%s/%s/guides/%s_guides.mb'
rigs_scene_path = '%s/%s/rigs/%s_rig.mb'
geo_scene_path = '%s/%s/geo/%s_geo.mb'
skin_file_path = '%s/%s/weights/'


class Builder(object):
    def __init__(self, moduleName):
        self.moduleName = moduleName

    @staticmethod
    def scene():
        cmds.file(f=True, new=True)

    def rig(self):

        cmds.mirrorJoint('L_clavicle', mirrorYZ=True, mirrorBehavior=True, searchReplace=['L_', 'R_'])
        cmds.mirrorJoint('L_leg', mirrorYZ=True, mirrorBehavior=True, searchReplace=['L_', 'R_'])

        cmds.duplicate('L_foot_GRP', name='R_foot_GRP', rc=True)
        cmds.setAttr('R_foot_GRP.scaleX', -1)

        for item in ['L_hell_CTL1', 'L_bankOut_CTL1', 'L_bankIn_CTL1', 'L_tip_CTL1']:
            cmds.rename(item, 'R' + item[1:-1])

        l_arm = extremity.Extremity(['L_shoulder', 'L_elbow', 'L_wrist'], 'L', 'Arm')
        l_arm.rig()
        r_arm = extremity.Extremity(['R_shoulder', 'R_elbow', 'R_wrist'], 'R', 'Arm')
        r_arm.rig()
        l_leg = extremity.Extremity(['L_leg', 'L_knee', 'L_ankle'], 'L', 'Leg')
        l_leg.rig()
        r_leg = extremity.Extremity(['R_leg', 'R_knee', 'R_ankle'], 'R', 'Leg')
        r_leg.rig()
        c_spine = spine.Spine(['spine_01', 'spine_02', 'spine_03', 'spine_04', 'spine_05'], 'C', 'Spine')
        c_spine.rig()
        c_head = head.Head(['neck_01', 'neck_02', 'head'], 'C')
        c_head.rig()
        c_main = main.Main(self.moduleName)
        c_main.rig(self.moduleName)

        # Get a list of all the groups in the scene
        group_list = cmds.ls(type="transform")

        # Loop through the group list and lock and hide all attributes
        for group in group_list:
            if "GRP" in group:
                cmds.setAttr(group + ".translateX", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".translateY", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".translateZ", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".rotateX", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".rotateY", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".rotateZ", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".scaleX", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".scaleY", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(group + ".scaleZ", lock=True, keyable=False, channelBox=False)

        print('Done: L_Arm_Module'.format(self.moduleName))
        print('Done: R_Arm_Module'.format(self.moduleName))
        print('Done: L_Leg_Module'.format(self.moduleName))
        print('Done: R_Leg_Module'.format(self.moduleName))
        print('Done: Spine_Module'.format(self.moduleName))
        print('Done: Head_Module'.format(self.moduleName))
        print('Done: Main_Module'.format(self.moduleName))

        c_skin = skin.SkinWeights(self.moduleName)
        c_skin.checkSkin()
        print('Skinning: {} Done.'.format(self.moduleName))

    def save_rig(self):
        rig_file = rigs_scene_path % (assets_path, self.moduleName, self.moduleName)
        cmds.select(self.moduleName)
        cmds.file(rig_file, force=True, type='mayaBinary', es=True)

    def save_geo(self):
        geo_file = geo_scene_path % (assets_path, self.moduleName, self.moduleName)
        cmds.select(self.moduleName + '_model_grp')
        cmds.file(geo_file, force=True, type='mayaBinary', es=True)
