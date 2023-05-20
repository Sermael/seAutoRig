""" Create Main module"""
from maya import cmds
from .node import Node
from .offset import offset_grp
from .matrix import constraint


class Main(object):
    def __init__(self, characterName):
        self.characterName = characterName

        # vars
        self.node = Node()
        self.ctlSize = 2

    def rig(self, characterName):
        self.characterName = characterName

        # vars
        self.node = Node()
        self.ctlSize = 2

        global_ctl = cmds.circle(n='{}_Global_CTL'.format(self.characterName), nr=(0, 1, 0), r=self.ctlSize * 3.3, d=1,
                                 s=15, ch=False)

        # global_ctl = self.customControl('{}_Global_CTL'.format(characterName))
        cmds.setAttr('{}_Global_CTLShape'.format(self.characterName) + '.overrideEnabled', True)
        cmds.setAttr('{}_Global_CTLShape'.format(self.characterName) + '.overrideColor', 17)
        # cmds.setAttr('{}_Global_CTLShape'.format(characterName) + '.lineWidth', 1.5)
        # cmds.addAttr(global_ctl, shortName='GlobalScale', longName='globalScale', defaultValue=1.0, minValue=0,
        # k=True)
        offset_grp(global_ctl, 'GRP')

        main_ctl = cmds.circle(n='{}_Main_CTL'.format(self.characterName), nr=(0, 1, 0), r=self.ctlSize * 3, d=1, s=15,
                               ch=False)
        cmds.setAttr('{}_Main_CTLShape'.format(self.characterName) + '.overrideEnabled', True)
        cmds.setAttr('{}_Main_CTLShape'.format(self.characterName) + '.overrideColor', 17)
        # cmds.setAttr('{}_Main_CTLShape'.format(characterName) + '.lineWidth', 1.5)
        offset_grp(main_ctl, 'GRP')

        cmds.parent('{}_Main_CTL_GRP'.format(self.characterName), '{}_Global_CTL'.format(self.characterName))

        # -- Limbs Scale
        for axis in 'xyz':
            cmds.setAttr("{}.s{}".format(main_ctl[0], axis), lock=True, k=False, channelBox=False)
            for limb in ['Arm', 'Leg']:
                for side in 'LR':
                    cmds.connectAttr('{}.s{}'.format(global_ctl[0], axis),
                                     '{}_{}_Normalized_MD.i2{}'.format(side, limb, axis))
        for side in 'LR':
            for limb in ['Arm', 'Leg']:
                for part in ['Upper', 'Lower']:
                    cmds.connectAttr(global_ctl[0] + '.sx', '{}_{}{}_GlobalScale_MD.i2x'.format(side, part, limb))

        for jnt in range(5):
            cmds.connectAttr(global_ctl[0] + '.sx', 'C_Spine0{}_OFF.sz'.format(jnt))
            cmds.connectAttr(global_ctl[0] + '.sy', 'C_Spine0{}_OFF.sy'.format(jnt))
            cmds.connectAttr(global_ctl[0] + '.sz', 'C_Spine0{}_OFF.sx'.format(jnt))

        global_grp = cmds.createNode('transform', n=self.characterName)
        cmds.addAttr(global_grp, ln='rig', at='bool', dv=True, k=False, hidden=True)
        rig_grp = cmds.createNode('transform', n='RIG_GRP')

        if cmds.objExists('{}_model_grp'.format(self.characterName)):
            cmds.parent('{}_model_grp'.format(self.characterName), self.characterName)
        else:
            model_grp = cmds.group(n='{}_model_grp'.format(self.characterName), em=True)
            cmds.parent(model_grp, self.characterName)

        cmds.parent('{}_Guides_GRP'.format(self.characterName), main_ctl)
        cmds.parent('{}_Global_CTL_GRP'.format(self.characterName), global_grp)
        # cmds.parent('C_Spine_GRP', rig_grp)
        cmds.parent(rig_grp, global_grp)

        cmds.parent('C_Spine_GRP', main_ctl)

        # constraint([root_ctl[0], 'C_Spine_GRP'], mo=True, jnt=False, point=True, orient=True, scale=True)
        im = cmds.shadingNode('inverseMatrix', n='C_Spine_IM', au=True)
        dm = cmds.createNode('decomposeMatrix', n='C_Spine_DM')
        cmds.connectAttr(main_ctl[0] + '.worldMatrix', im + '.inputMatrix')
        cmds.connectAttr(im + '.outputMatrix', dm + '.inputMatrix')
        cmds.connectAttr(dm + '.outputTranslate', 'C_Spine_JNT_GRP.translate')
        cmds.connectAttr(dm + '.outputRotate', 'C_Spine_JNT_GRP.rotate')
        cmds.connectAttr(dm + '.outputScale', 'C_Spine_JNT_GRP.scale')

        cmds.parent('C_Head_GRP', main_ctl)
        cmds.parent('L_Arm_GRP', main_ctl)
        cmds.parent('R_Arm_GRP', main_ctl)
        cmds.parent('L_Leg_GRP', main_ctl)
        cmds.parent('R_Leg_GRP', main_ctl)

        cmds.parent('C_Spine_BendSystem_GRP', rig_grp)
        cmds.parent('L_Arm_BendSystem_GRP', rig_grp)
        cmds.parent('R_Arm_BendSystem_GRP', rig_grp)
        cmds.parent('L_Leg_BendSystem_GRP', rig_grp)
        cmds.parent('R_Leg_BendSystem_GRP', rig_grp)

        constraint(['C_Chest_CTL', 'L_Clavicle_CTL_GRP'], mo=True, jnt=False, point=True, orient=True, scale=False)
        constraint(['C_Chest_CTL', 'R_Clavicle_CTL_GRP'], mo=True, jnt=False, point=True, orient=True, scale=False)
        constraint(['C_Pelvis_CTL', 'L_Leg_Main_CTL_GRP'], mo=True, jnt=False, point=True, orient=True, scale=False)
        constraint(['C_Pelvis_CTL', 'R_Leg_Main_CTL_GRP'], mo=True, jnt=False, point=True, orient=True, scale=False)

        # --- Head effects
        cmds.parent('C_head_FK_CTL_GRP', 'C_Head_GRP')

        constraint(['C_neck_02_FK_CTL', 'C_head_FK_CTL_OFF'], mo=True, jnt=False, point=True, orient=True, scale=False)
        constraint(['C_Chest_CTL', 'C_neck_01_FK_CTL_OFF'], mo=True, jnt=False, point=True, orient=True, scale=False)

        mdv1 = cmds.shadingNode('multiplyDivide', n="C_Head_MDV", au=True)
        cmds.connectAttr('C_head_FK_CTL_OFF_DM.outputRotate', mdv1 + '.i1')
        cmds.disconnectAttr('C_head_FK_CTL_OFF_DM.outputRotate', 'C_head_FK_CTL_OFF.r')
        cmds.connectAttr(mdv1 + '.o', 'C_head_FK_CTL_OFF.r')

        mdv2 = cmds.shadingNode('multiplyDivide', n="C_Neck_MDV", au=True)
        cmds.connectAttr('C_neck_01_FK_CTL_OFF_DM.outputRotate', mdv2 + '.i1')
        cmds.disconnectAttr('C_neck_01_FK_CTL_OFF_DM.outputRotate', 'C_neck_01_FK_CTL_OFF.r')
        cmds.connectAttr(mdv2 + '.o', 'C_neck_01_FK_CTL_OFF.r')

        for axis in 'xyz':
            cmds.connectAttr('C_head_FK_CTL.SpineOrient', '{}.i2{}'.format(mdv1, axis))
            cmds.connectAttr('C_neck_01_FK_CTL.SpineOrient', '{}.i2{}'.format(mdv2, axis))

        # -- joints radius
        cmds.select(self.characterName)
        joints = cmds.ls(selection=True, dag=True, type='joint')
        for joint in joints:
            cmds.setAttr(joint + '.radius', 0.5)
        cmds.select(clear=True)

        skin_joints = [u'root', u'Spine00_JNT', u'Spine01_JNT', u'Spine02_JNT', u'Spine03_JNT', u'C_Chest_JNT',
                       u'L_clavicle', u'R_clavicle', u'C_neck_01_FK_CTL', u'C_neck_02_FK_CTL', u'C_head_FK_CTL',
                       u'L_UpperArm_Twist_01', u'L_UpperArm_Twist_00', u'L_UpperArm_Twist_02', u'L_UpperArm_Twist_03',
                       u'L_LowerArm_Twist_01', u'L_LowerArm_Twist_00', u'L_LowerArm_Twist_02', u'L_LowerArm_Twist_03',
                       u'L_LowerArm_Twist_05', u'L_UpperLeg_Twist_01', u'L_UpperLeg_Twist_00', u'L_UpperLeg_Twist_02',
                       u'L_UpperLeg_Twist_03', u'L_LowerLeg_Twist_01', u'L_LowerLeg_Twist_00', u'L_LowerLeg_Twist_02',
                       u'L_LowerLeg_Twist_03', u'L_LowerLeg_Twist_05', u'R_UpperLeg_Twist_01', u'R_UpperLeg_Twist_00',
                       u'R_UpperLeg_Twist_02', u'R_UpperLeg_Twist_03', u'R_LowerLeg_Twist_01', u'R_LowerLeg_Twist_00',
                       u'R_LowerLeg_Twist_02', u'R_LowerLeg_Twist_03', u'R_LowerLeg_Twist_05', u'L_ankle|L_ball',
                       u'R_ankle|R_ball', u'L_ankle|L_ball|L_ball', u'R_ankle|R_ball|R_ball', u'R_UpperArm_Twist_01',
                       u'R_UpperArm_Twist_00', u'R_UpperArm_Twist_02', u'R_UpperArm_Twist_03', u'R_LowerArm_Twist_01',
                       u'R_LowerArm_Twist_00', u'R_LowerArm_Twist_02', u'R_LowerArm_Twist_03', u'R_LowerArm_Twist_05']

    @staticmethod
    def customControl(name):
        custom_control = '../templates/CustomControl.ma'
        cmds.file(custom_control, i=1)
        cmds.rename('Custom_CTL', name)
        cmds.rename('Custom_CTL_SC', name + '_SC')
        custom_con = [name + '_SC']
        return custom_con
