""" Create extremity module - Sergio Efigenio - 05/02/2023"""
import importlib
import pymel.core as pm
from maya import cmds, OpenMaya
from maya.api import OpenMaya

from . import node
from . import offset
from . import matrix

importlib.reload(node)
importlib.reload(offset)
importlib.reload(matrix)


class Extremity(object):
    """A class used to represent an Extremity.

    :arg:
        jnt_chain (list): ['shoulder_jnt', 'elbow_jnt', 'wrist_jnt'] a list of 3 joints to build the extremity
        side (str): 'L' or 'R' the side of the extremity
        limb (str): 'Arm' or 'Leg'  the type of limb

    :rtype:
        object

    Methods:
        rig()
        Build the extremity system

    """

    def __init__(self, jnt_chain, side, limb):

        self.jnt_chain = jnt_chain
        self.side = side
        self.limb = limb

        # vars
        self.ctlSize = 1.3

    def rig(self):
        # -- Duplicate Joints
        fk = cmds.duplicate(self.jnt_chain[0], rc=True)

        # -- Rename Joint Lists
        for jnt in range(3):
            cmds.rename(fk[jnt], '{}_FK_CTL'.format(self.jnt_chain[jnt]))

        # -- Setup fingers
        if self.limb == 'Arm':
            fingers = cmds.listRelatives(self.jnt_chain[2], c=True)
            cmds.parent(fingers, '{}_FK_CTL'.format(self.jnt_chain[2]))
            cmds.select(fingers, hi=True)
            for finger in cmds.ls(sl=True):
                cmds.rename(finger, finger + '_FK_CTL')

        # -- Lists fk ik Chain
        cmds.select('{}_FK_CTL'.format(self.jnt_chain[0]), hi=True)
        fk_chain = cmds.ls(sl=1)

        # -- Create fk controls
        for i, jnt in enumerate(fk_chain):
            if self.limb == 'Arm':
                if i > 2:
                    cmds.circle(n='{0}Shape'.format(jnt), nr=(1, 0, 0), r=self.ctlSize * 0.2, ch=False)
                else:
                    cmds.circle(n='{0}Shape'.format(jnt), nr=(1, 0, 0), r=self.ctlSize * 1.2, ch=False)
            elif self.limb == 'Leg':
                if i > 2:
                    cmds.circle(n='{0}Shape'.format(jnt), nr=(1, 0, 0), r=self.ctlSize * 0.8, ch=False)
                else:
                    cmds.circle(n='{0}Shape'.format(jnt), nr=(1, 0, 0), r=self.ctlSize * 1.2, ch=False)
                    
            color = 6 if self.side == 'L' else 13
            cmds.setAttr('{}.overrideEnabled'.format(jnt), True)
            cmds.setAttr('{}.overrideColor'.format(jnt), color)
            cmds.parent('{}ShapeShape'.format(jnt), jnt, r=True, s=True)
            cmds.delete(jnt + 'Shape')

        # -- Create fk fingers
        if self.limb == 'Arm':
            cmds.select(cl=True)
            fingers_grp = cmds.group(n='{}_{}_Fingers_CTL_GRP'.format(self.side, self.limb), em=True)
            cmds.delete(cmds.parentConstraint(self.jnt_chain[2], fingers_grp))
            fingers = cmds.listRelatives(self.jnt_chain[2] + '_FK_CTL', c=True)
            for f in fingers:
                if 'CTL' in f:
                    if not cmds.objectType(f, i='shape'):
                        if '{}'.format(self.jnt_chain[2]) in f:
                            pass
                        else:
                            cmds.parent(f, fingers_grp)
                else:
                    cmds.delete(f)
            # cmds.parent(self.jnt_chain[2] + '_FK_CTL', self.jnt_chain[1] + '_FK_CTL')

        # -- Lists fk ik Chain
        fk_chain = ['{}_FK_CTL'.format(self.jnt_chain[0]), '{}_FK_CTL'.format(self.jnt_chain[1]),
                    '{}_FK_CTL'.format(self.jnt_chain[2])]

        # -- Color joints
        if self.side == 'L':
            for jnt in self.jnt_chain:
                cmds.setAttr(jnt + '.overrideEnabled', True)
                cmds.setAttr(jnt + '.overrideColor', 15)
        if self.side == 'R':
            for jnt in self.jnt_chain:
                cmds.setAttr(jnt + '.overrideEnabled', True)
                cmds.setAttr(jnt + '.overrideColor', 4)

        # -- Create IK Ctl
        orient = (1, 0, 0) if self.limb == 'Leg' else (1, 0, 0)
        ik_ctl = cmds.circle(n='{}_IK_CTL'.format(self.jnt_chain[2]), nr=orient, r=self.ctlSize * 1.1, d=1, s=8,
                             ch=False)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[2], ik_ctl, mo=False))
        offset.offset_grp(ik_ctl, 'GRP')
        offset.offset_grp(ik_ctl, 'OFF')
        offset.offset_grp(ik_ctl, 'SDK')

        # -- Create PV Ctl
        pv_ctl = cmds.circle(n='{}_{}_PV_CTL'.format(self.side, self.limb), nr=(1, 0, 0), r=self.ctlSize * 0.5, 
                             d=1, s=4, ch=False)
        offset.offset_grp(pv_ctl, 'GRP')
        offset.offset_grp(pv_ctl, 'OFF')
        offset.offset_grp(pv_ctl, 'SDK')

        # # -- Position PV
        self.place_pole_vector_ctrl(
            start=self.jnt_chain[0],
            mid=self.jnt_chain[1],
            end=self.jnt_chain[2],
            pv_ctrl=pv_ctl[0] + '_GRP',
            shift_factor=40,
        )

        # # -- Position PV (Other method)
        # cmds.xform('{}_{}_PV_CTL_GRP'.format(self.side, self.limb), worldSpace=True, translation=pole_vector_pos)
        # pv_pos = -self.ctlSize * 10 if limb == 'Arm' else self.ctlSize * 10
        # cmds.setAttr('{}_{}_PV_CTL_GRP'.format(self.side, self.limb) + '.translateZ', pv_pos)

        # -- Create IK Setup
        ik_handle = cmds.ikHandle(n='{}_{}_IkHandleRP'.format(self.side, self.limb),
                                  sj=self.jnt_chain[0], ee=self.jnt_chain[2], sol='ikRPsolver')
        grp = cmds.group(n='{0}_GRP'.format(ik_handle[0]), em=True)
        cmds.delete(cmds.parentConstraint(ik_handle[0], grp))
        cmds.parent(ik_handle[0], grp)
        cmds.setAttr(grp + '.visibility', 0)
        cmds.setAttr(grp + '.visibility', 0)

        # matrix.constraint([ik_ctl[0], ik_handle[0]], mo=True, jnt=False, point=True, orient=True, scale=True)
        cmds.poleVectorConstraint(pv_ctl, ik_handle[0])

        # -- Create Switch Ctl
        switch = cmds.circle(n='{}_{}_Switch_CTL'.format(self.side, self.limb), nr=(0, 1, 0),
                             r=self.ctlSize * 0.5, d=1, s=3, ch=False)
        cmds.delete(cmds.pointConstraint(self.jnt_chain[2] + '_FK_CTL', '{}_{}_Switch_CTL'.format(self.side, self.limb),
                                         mo=False))
        offset.offset_grp(switch, 'GRP')
        offset.offset_grp(switch, 'OFF')

        cmds.xform(switch[0], query=True, t=True, ws=True)
        cmds.addAttr(switch[0], ln='space', nn='----------', at='enum', enumName='----------', k=True)
        cmds.addAttr(switch[0], ln='IKSwitch', nn='IK Switch', at='float', max=1, min=0, dv=0, k=True)
        cmds.setAttr(switch[0] + '.space', lock=True)

        cmds.connectAttr(switch[0] + '.IKSwitch', '{}.ikBlend'.format(ik_handle[0]))
        cmds.connectAttr(switch[0] + '.IKSwitch', ik_ctl[0] + '.visibility')
        cmds.connectAttr(switch[0] + '.IKSwitch', pv_ctl[0] + '.visibility')

        reverse_node = cmds.shadingNode('reverse', asUtility=1, n='IK_Switch_Rev')
        cmds.connectAttr(switch[0] + '.IKSwitch', reverse_node + '.ix')
        cmds.connectAttr(reverse_node + '.ox', '{}_FK_CTL.visibility'.format(self.jnt_chain[0]))

        cmds.connectAttr('{}_FK_CTL.rx'.format(self.jnt_chain[0]), self.jnt_chain[0] + '.rx')
        cmds.connectAttr('{}_FK_CTL.ry'.format(self.jnt_chain[0]), self.jnt_chain[0] + '.ry')
        cmds.connectAttr('{}_FK_CTL.rz'.format(self.jnt_chain[0]), self.jnt_chain[0] + '.rz')

        cmds.connectAttr('{}_FK_CTL.rx'.format(self.jnt_chain[1]), self.jnt_chain[1] + '.rx')
        cmds.connectAttr('{}_FK_CTL.ry'.format(self.jnt_chain[1]), self.jnt_chain[1] + '.ry')
        cmds.connectAttr('{}_FK_CTL.rz'.format(self.jnt_chain[1]), self.jnt_chain[1] + '.rz')

        # -- Twist Setup
        first_pos = cmds.xform(self.jnt_chain[1], t=True, query=True)
        sec_pos = cmds.xform(self.jnt_chain[2], t=True, query=True)
        # third_pos = cmds.xform(self.jnt_chain[2], t=True, query=True)
        upper_twist = []
        lower_twist = []

        for twist in ['Upper', 'Lower', 'Hand']:
            if twist == 'Upper':
                num = 0
            elif twist == 'Lower':
                num = 1
            elif twist == 'Hand':
                num = 2

            cmds.select(clear=True)

            for target in range(2):
                target_jnt = cmds.joint(n='{0}_{1}{2}_Target_0{3}'.format(self.side, twist, self.limb, target))
                cmds.delete(cmds.parentConstraint(self.jnt_chain[num], target_jnt, mo=False))
                cmds.makeIdentity(target_jnt, a=True)
                cmds.setAttr(target_jnt + '.drawStyle', 2)
                if twist == 'Upper':
                    cmds.connectAttr(self.jnt_chain[0] + '.scale', target_jnt + '.scale')
                    if target == 1:
                        cmds.setAttr(target_jnt + '.translateX', first_pos[0])
                elif twist == 'Lower':
                    cmds.connectAttr(self.jnt_chain[1] + '.scale', target_jnt + '.scale')
                    if target == 1:
                        cmds.setAttr(target_jnt + '.translateX', sec_pos[0])
                elif twist == 'Hand':
                    cmds.connectAttr(self.jnt_chain[2] + '.scale', target_jnt + '.scale')
                    if target == 1:
                        cmds.setAttr(target_jnt + '.translateX', 2)

            # --Create twist target ikRp
            ikh_rp, effector = cmds.ikHandle(
                name='{0}_{1}{2}_ikRp'.format(self.side, twist, self.limb), solver='ikRPsolver',
                startJoint='{0}_{1}{2}_Target_00'.format(self.side, twist, self.limb),
                endEffector='{0}_{1}{2}_Target_01'.format(self.side, twist, self.limb))
            cmds.rename(effector, '{0}_{1}{2}_Tgt_eff'.format(self.side, twist, self.limb))
            cmds.setAttr('{0}_{1}{2}_ikRp.visibility'.format(self.side, twist, self.limb), 0)

            for axis in ('x', 'y', 'z'):
                cmds.setAttr('{0}.pv{1}'.format(ikh_rp, axis), 0)
            if twist == 'Upper':
                cmds.parent(ikh_rp, self.jnt_chain[1])
            elif twist == 'Lower':
                cmds.parent(ikh_rp, self.jnt_chain[2])
            elif twist == 'Hand':
                cmds.parent(ikh_rp, self.jnt_chain[2])
            if twist == 'Hand':
                pass
            else:
                for joints in range(6):
                    twist_joint = cmds.joint(n='{0}_{1}{2}_Twist_0{3}'.format(self.side, twist, self.limb, joints))
                    cmds.delete(cmds.parentConstraint(self.jnt_chain[num], twist_joint, mo=False))
                    cmds.makeIdentity(twist_joint, a=True)

                    if self.side == 'L':
                        cmds.setAttr(twist_joint + '.overrideEnabled', True)
                        cmds.setAttr(twist_joint + '.overrideColor', 15)
                    if self.side == 'R':
                        cmds.setAttr('.overrideEnabled', True)
                        cmds.setAttr('.overrideColor', 4)

                    if twist == 'Upper':
                        cmds.connectAttr(self.jnt_chain[0] + '.scale', twist_joint + '.scale')
                        upper_twist.append(twist_joint)
                        if joints > 0:
                            cmds.setAttr(twist_joint + '.translateX', first_pos[0] / 4)
                        if joints >= 4:
                            cmds.setAttr(twist_joint + '.translateX', first_pos[0] / 8)

                    elif twist == 'Lower':
                        cmds.connectAttr(self.jnt_chain[1] + '.scale', twist_joint + '.scale')
                        lower_twist.append(twist_joint)
                        if joints > 0:
                            cmds.setAttr(twist_joint + '.translateX', sec_pos[0] / 4)
                        if joints >= 4:
                            cmds.setAttr(twist_joint + '.translateX', sec_pos[0] / 8)

                # --Create the twist ikSph
                ikh, effector, curve = cmds.ikHandle(
                    name='{0}_{1}{2}_ikSpn'.format(self.side, twist, self.limb),
                    solver='ikSplineSolver',
                    startJoint='{0}_{1}{2}_Twist_00'.format(self.side, twist, self.limb),
                    endEffector='{0}_{1}{2}_Twist_05'.format(self.side, twist, self.limb),
                    rootOnCurve=True,
                    parentCurve=False,
                    createCurve=True,
                    simplifyCurve=True,
                    numSpans=1)

                cmds.rename(effector, '{0}_{1}{2}_eff'.format(self.side, twist, self.limb))
                cmds.rename(curve, '{0}_{1}{2}_CRV'.format(self.side, twist, self.limb))

                # -- Twist Values
                twist_value = cmds.group(name='{0}_{1}{2}_TwistValue'.format(self.side, twist, self.limb), em=True)
                mdl = cmds.createNode('multDoubleLinear', n='{0}_{1}{2}_MDL'.format(self.side, twist, self.limb))

                value = -1 if self.side == 'L' else 1

                if twist == 'Upper':
                    cmds.delete(cmds.parentConstraint(self.jnt_chain[1], twist_value, mo=False))
                    cmds.parent(twist_value, self.jnt_chain[1])
                    cmds.connectAttr(twist_value + '.rx', mdl + '.i1')
                    cmds.setAttr(mdl + '.i2', value)
                    cmds.connectAttr(mdl + '.o', '{0}_Upper{1}_ikSpn.twist'.format(self.side, self.limb))

                elif twist == 'Lower':
                    cmds.delete(cmds.parentConstraint(self.jnt_chain[2], twist_value, mo=False))
                    cmds.parent(twist_value, self.jnt_chain[2])
                    cmds.connectAttr(twist_value + '.rx', mdl + '.i1')
                    cmds.setAttr(mdl + '.i2', value)
                    cmds.connectAttr(mdl + '.o', '{0}_Lower{1}_ikSpn.twist'.format(self.side, self.limb))

        for twist in ['Upper', 'Lower']:
            if twist == 'Upper':
                aim = (-1, 0, 0) if self.side == 'R' else (1, 0, 0)
                u = (0, 0, -1) if self.side == 'R' else (0, 0, 1)
                wu = (0, 0, -1) if self.side == 'R' else (0, 0, 1)

                cmds.aimConstraint(self.jnt_chain[2],
                                   '{0}_Upper{1}_TwistValue'.format(self.side, self.limb),
                                   aim=aim,
                                   u=u,
                                   wu=wu,
                                   wut='objectrotation',
                                   wuo='{0}_Lower{1}_Target_00'.format(self.side, self.limb))

            elif twist == 'Lower':
                u = (0, 0, -1) if self.side == 'R' else (0, 0, 1)
                wu = (0, 0, -1) if self.side == 'R' else (0, 0, 1)

                cmds.aimConstraint('{0}_Hand{1}_ikRp'.format(self.side, self.limb),
                                   '{0}_Lower{1}_TwistValue'.format(self.side, self.limb),
                                   aim=(1, 0, 0),
                                   u=u,
                                   wu=wu,
                                   wut='objectrotation',
                                   wuo='{0}_Hand{1}_Target_00'.format(self.side, self.limb))

        cmds.parent('{0}_Lower{1}_Target_00'.format(self.side, self.limb),
                    '{0}_Upper{1}_Target_00'.format(self.side, self.limb))
        cmds.parent('{0}_Hand{1}_Target_00'.format(self.side, self.limb), self.jnt_chain[1])
        cmds.parent('{}_Upper{}_Twist_00'.format(self.side, self.limb),
                    '{}_Upper{}_Target_00'.format(self.side, self.limb))
        cmds.parent('{}_Lower{}_Twist_00'.format(self.side, self.limb), self.jnt_chain[1])

        # -- Create twist curves
        for curve in ['Hard', 'Smooth']:
            cvp1 = cmds.xform(self.jnt_chain[0], query=True, worldSpace=True, translation=True)
            cvp2 = cmds.xform(upper_twist[2], query=True, worldSpace=True, translation=True)
            cvp3 = cmds.xform(self.jnt_chain[1], query=True, worldSpace=True, translation=True)
            cvp4 = cmds.xform(lower_twist[2], query=True, worldSpace=True, translation=True)
            cvp5 = cmds.xform(self.jnt_chain[2], query=True, worldSpace=True, translation=True)

            if curve == 'Hard':
                hcv = cmds.curve(n='{0}_{1}_Hard_CRV'.format(self.side, self.limb),
                                 d=1, p=[cvp1, cvp2, cvp3, cvp4, cvp5])
                for c in range(5):
                    cmds.select('{0}.cv[{1}]'.format(hcv, c))
                    cmds.cluster(n='{}_{}_CLS_0{}'.format(self.side, self.limb, c))
            else:
                cmds.curve(n='{0}_{1}_Smooth_CRV'.format(self.side, self.limb),
                           d=3, p=[cvp1, cvp2, cvp3, cvp4, cvp5])

        cv_bs = cmds.blendShape('{0}_{1}_Hard_CRV'.format(self.side, self.limb),
                                '{0}_{1}_Smooth_CRV'.format(self.side, self.limb),
                                en=1, n='{0}_{1}_Smooth_CRV_BS'.format(self.side, self.limb))
        cmds.setAttr(cv_bs[0] + '.{}_{}_Hard_CRV'.format(self.side, self.limb), 1)

        for i in range(3):
            ctl = cmds.circle(n='{0}_{1}_Bend_0{2}_CTL'.format(self.side, self.limb, i),
                              nr=(1, 0, 0), r=self.ctlSize, d=1, s=4, ch=False)
            offset.offset_grp(ctl, 'GRP')
            offset.offset_grp(ctl, 'OFF')

        ctl1 = '{0}_{1}_Bend_01_CTL'.format(self.side, self.limb)
        ctl2 = '{0}_{1}_Bend_00_CTL'.format(self.side, self.limb)
        ctl3 = '{0}_{1}_Bend_02_CTL'.format(self.side, self.limb)
        ctl_grp_1 = '{0}_{1}_Bend_01_CTL_OFF'.format(self.side, self.limb)
        ctl_grp_2 = '{0}_{1}_Bend_00_CTL_OFF'.format(self.side, self.limb)
        ctl_grp_3 = '{0}_{1}_Bend_02_CTL_OFF'.format(self.side, self.limb)

        matrix.Constraint([self.jnt_chain[1], ctl_grp_1], mo=False, jnt=False, point=True, orient=True, scale=False)

        # matrix.SwitchConstraint([jnt_chain[1], fk_chain[1], ctl_grp_1], switch_ctl=switch[0], switch_attr='IKSwitch',
        #                  mo=False, jnt=False, point=True, orient=True, scale=False)

        matrix.Constraint([self.jnt_chain[0], ctl_grp_2], mo=False, jnt=False, point=False, orient=True, scale=False)
        matrix.Constraint([self.jnt_chain[1], ctl_grp_3], mo=False, jnt=False, point=False, orient=True, scale=False)

        cmds.pointConstraint(self.jnt_chain[0], ctl1, ctl_grp_2, mo=False)
        cmds.pointConstraint(ctl1, self.jnt_chain[2], ctl_grp_3, mo=False)

        cmds.parent('{}_{}_CLS_00Handle'.format(self.side, self.limb), self.jnt_chain[0])
        cmds.parent('{}_{}_CLS_01Handle'.format(self.side, self.limb), ctl2)
        cmds.parent('{}_{}_CLS_02Handle'.format(self.side, self.limb), ctl1)
        cmds.parent('{}_{}_CLS_03Handle'.format(self.side, self.limb), ctl3)
        cmds.parent('{}_{}_CLS_04Handle'.format(self.side, self.limb), self.jnt_chain[2])

        for cls in cmds.ls('{}_{}_CLS_0*HandleShape'.format(self.side, self.limb)):
            cmds.setAttr(cls + '.visibility', False)

        # -- wire twist curves
        cmds.addAttr('{}_{}_Bend_01_CTL'.format(self.side, self.limb),
                     ln='tension', nn='Tension', at='bool', dv=1, k=True)
        rev = cmds.shadingNode('reverse', asUtility=1, n='{}_{}_Bend_01_REV'.format(self.side, self.limb))
        cmds.connectAttr('{}_{}_Bend_01_CTL.tension'.format(self.side, self.limb), rev + '.ix')

        for crv in ['Upper', 'Lower']:
            for mode in ['Hard', 'Smooth']:
                duplicate = cmds.duplicate('{}_{}{}_CRV'.format(self.side, crv, self.limb))
                rename = cmds.rename(duplicate, '{}_{}{}_Twist_{}_CRV'.format(self.side, crv, self.limb, mode))
                cmds.select(rename)
                cmds.wire(w='{}_{}_{}_CRV'.format(self.side, self.limb, mode),
                          gw=False, en=1, ce=0, li=0, dds=[(0, 100)])

                bs = cmds.blendShape('{}_{}{}_Twist_{}_CRV'.format(self.side, crv, self.limb, mode),
                                     '{}_{}{}_CRV'.format(self.side, crv, self.limb),
                                     en=1, n='{}_{}{}_{}_BS'.format(self.side, crv, self.limb, mode))

                cmds.setAttr(bs[0] + '.{}_{}{}_Twist_{}_CRV'.format(self.side, crv, self.limb, mode), 1)

                if mode == 'Hard':
                    cmds.connectAttr('{}_{}_Bend_01_CTL.tension'.format(self.side, self.limb),
                                     bs[0] + '.{}_{}{}_Twist_{}_CRV'.format(self.side, crv, self.limb, mode))
                else:
                    cmds.connectAttr(rev + '.ox',
                                     bs[0] + '.{}_{}{}_Twist_{}_CRV'.format(self.side, crv, self.limb, mode))

        # -- Clean Up
        bend_sys_grp = cmds.group(n='{}_{}_BendSystem_GRP'.format(self.side, self.limb), em=True)
        cmds.parent('{}_Upper{}_ikSpn'.format(self.side, self.limb),
                    '{}_Lower{}_ikSpn'.format(self.side, self.limb),
                    '{}_Upper{}_CRV'.format(self.side, self.limb),
                    '{}_Lower{}_CRV'.format(self.side, self.limb),
                    '{}_{}_Hard_CRV'.format(self.side, self.limb),
                    '{}_{}_Smooth_CRV'.format(self.side, self.limb),
                    '{}_Upper{}_Twist_Hard_CRV'.format(self.side, self.limb),
                    '{}_Lower{}_Twist_Hard_CRV'.format(self.side, self.limb),
                    '{}_Upper{}_Twist_Smooth_CRV'.format(self.side, self.limb),
                    '{}_Lower{}_Twist_Smooth_CRV'.format(self.side, self.limb),
                    '{}_{}_Hard_CRVBaseWire*'.format(self.side, self.limb),
                    '{}_{}_Smooth_CRVBaseWire*'.format(self.side, self.limb),
                    bend_sys_grp)
        cmds.setAttr(bend_sys_grp + '.visibility', 0)

        bend_ctl_grp = cmds.group(n='{}_{}_Bend_CTL_GRP'.format(self.side, self.limb), em=True)
        for part in range(3):
            cmds.parent('{}_{}_Bend_0{}_CTL_GRP'.format(self.side, self.limb, part), bend_ctl_grp)

        cmds.addAttr(ik_ctl[0], ln='autoStretch', nn='Auto Stretch', at='float', min=0, max=1, dv=1, k=True)
        cmds.addAttr(ik_ctl[0], ln='%sStretch' % self.jnt_chain[0], nn='%s Stretch' % self.jnt_chain[0],
                     at='float', min=0.1, dv=1, k=True)
        cmds.addAttr(ik_ctl[0], ln='%sStretch' % self.jnt_chain[1], nn='%s Stretch' % self.jnt_chain[1],
                     at='float', min=0.1, dv=1, k=True)
        cmds.addAttr(ik_ctl[0], ln='smoothStretch', nn='Smooth Stretch', at='float', min=0, max=1, dv=0, k=True)
        cmds.addAttr(switch[0], ln='compensateVolume', nn='Compensate Volume', at='float', min=0, max=1, dv=1, k=True)

        for ctl in fk_chain:
            cmds.addAttr(ctl, ln='Stretch', nn='Stretch', at='float', min=0, dv=1, k=True)

        # -- Group Joints
        jnt_grp = cmds.group(n='{}_{}_JNT_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], jnt_grp, mo=False))
        hook_grp = cmds.group(n='{}_{}_JNT_OFF_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], hook_grp, mo=False))
        cmds.parent(hook_grp, jnt_grp)
        cmds.parent(self.jnt_chain[0], hook_grp)

        # -- Distance
        start_pos = cmds.createNode('decomposeMatrix', name='{}_{}_POS_DM'.format(self.side, self.jnt_chain[0]))
        cmds.connectAttr(jnt_grp + '.worldMatrix', start_pos + '.inputMatrix', force=True)
        end_pos = cmds.createNode('decomposeMatrix', name='{}_{}_POS_DM'.format(self.side, self.jnt_chain[2]))
        null_grp = cmds.group(n='{}_Null'.format(self.jnt_chain[2]), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[2], null_grp))
        cmds.parent(null_grp, ik_ctl[0])
        cmds.connectAttr(null_grp + '.worldMatrix', end_pos + '.inputMatrix', force=True)

        distance = cmds.createNode('distanceBetween', name='{}_{}_DB'.format(self.side, self.limb))
        cmds.connectAttr(start_pos + '.ot', distance + '.p1')
        cmds.connectAttr(end_pos + '.ot', distance + '.p2')
        dist_normal_md = cmds.shadingNode('multiplyDivide', au=True,
                                          name='{}_{}_Normalized_MD'.format(self.side, self.limb))
        distance_md = cmds.shadingNode('multiplyDivide', au=True, name='{}_{}_Stretch_MD'.format(self.side, self.limb))
        cmds.setAttr(distance_md + '.operation', 2)
        cmds.setAttr(dist_normal_md + '.operation', 2)

        cmds.connectAttr(distance + '.d', dist_normal_md + '.i1x')
        cmds.connectAttr(dist_normal_md + '.ox', distance_md + '.i1x')

        # -- Scale Switch
        scale_bc = cmds.shadingNode('blendColors', au=True, name='{}_{}_Scale_BC'.format(self.side, self.limb))
        cmds.connectAttr(fk_chain[0] + '.Stretch', scale_bc + '.color2.color2R.')
        cmds.connectAttr(fk_chain[1] + '.Stretch', scale_bc + '.color2.color2G.')
        cmds.connectAttr(switch[0] + '.IKSwitch', scale_bc + '.blender')

        # -- Voloume
        for part in ['Upper', 'Lower']:
            volume_md = cmds.shadingNode('multiplyDivide', au=True,
                                         name='{}_{}{}_Volume_MD'.format(self.side, part, self.limb))
            volume_bc = cmds.shadingNode('blendColors', au=True,
                                         name='{}_{}{}_Volume_BC'.format(self.side, part, self.limb))
            cmds.connectAttr(switch[0] + '.compensateVolume', volume_bc + '.blender')
            cmds.setAttr(volume_md + '.i1x', 1)
            cmds.setAttr(volume_md + '.operation', 2)
            cmds.setAttr(volume_bc + '.color2R', 1)
            cmds.setAttr(volume_bc + '.color2G', 1)
            cmds.setAttr(volume_bc + '.color2B', 1)

            # Twist Scale Nodes
            cv_inf = cmds.shadingNode('curveInfo', n='{}_{}{}_CINF'.format(self.side, part, self.limb), au=True)
            cv_mdv = cmds.shadingNode('multiplyDivide', n='{}_{}{}_Dist_MD'.format(self.side, part, self.limb), au=True)
            global_mdv = cmds.shadingNode('multiplyDivide',
                                          n='{}_{}{}_GlobalScale_MD'.format(self.side, part, self.limb), au=True)
            sum_pma = cmds.shadingNode('plusMinusAverage', n='{}_{}{}_SumScale_PMA'.format(self.side, part, self.limb),
                                       au=True)
            subtract_pma = cmds.shadingNode('plusMinusAverage',
                                            n='{}_{}{}_SubtractScale_PMA'.format(self.side, part, self.limb), au=True)
            scale_mdv = cmds.shadingNode('multiplyDivide', n='{}_{}{}_Scale_MD'.format(self.side, part, self.limb),
                                         au=True)
            cmds.setAttr(cv_mdv + '.operation', 2)
            cmds.setAttr(global_mdv + '.operation', 2)
            cmds.setAttr(subtract_pma + '.operation', 2)

            cmds.connectAttr('{}_{}{}_CRVShape.worldSpace'.format(self.side, part, self.limb), cv_inf + '.inputCurve')
            cmds.connectAttr(cv_inf + '.arcLength', cv_mdv + '.i1x')
            cmds.connectAttr(cv_mdv + '.outputX', global_mdv + '.i1x')
            cmds.connectAttr(global_mdv + '.output.outputX', sum_pma + '.input1D[0]', force=True)
            cmds.connectAttr('{}.scaleX'.format(self.jnt_chain[0]), sum_pma + '.input1D[1]')
            cmds.connectAttr(sum_pma + '.output1D', subtract_pma + '.input1D[0]')
            cmds.connectAttr('{}.scaleX'.format(self.jnt_chain[0]), subtract_pma + '.input1D[1]')
            cmds.connectAttr(subtract_pma + '.output1D', scale_mdv + '.i1x')

            cv_dist = cmds.getAttr(cv_inf + '.arcLength')
            cmds.setAttr(cv_mdv + '.i2x', cv_dist)

            if part == 'Upper':
                cmds.connectAttr(scale_bc + '.output.outputR', volume_md + '.i2x')
                cmds.connectAttr(volume_md + '.ox', volume_bc + '.color1.color1R.')
                cmds.connectAttr(volume_bc + '.output.outputR', self.jnt_chain[0] + '.scaleY')
                cmds.connectAttr(volume_bc + '.output.outputR', self.jnt_chain[0] + '.scaleZ')
                cmds.connectAttr(self.jnt_chain[0] + '.scaleY', scale_mdv + '.i1y')
                cmds.connectAttr(self.jnt_chain[0] + '.scaleZ', scale_mdv + '.i1z')
                for jnt in upper_twist:
                    cmds.connectAttr(scale_mdv + '.o', jnt + '.s', force=True)
            else:
                cmds.connectAttr(scale_bc + '.output.outputG', volume_md + '.i2x')
                cmds.connectAttr(volume_md + '.ox', volume_bc + '.color1.color1R.')
                cmds.connectAttr(volume_bc + '.output.outputR', self.jnt_chain[1] + '.scaleY')
                cmds.connectAttr(volume_bc + '.output.outputR', self.jnt_chain[1] + '.scaleZ')
                cmds.connectAttr(self.jnt_chain[1] + '.scaleY', scale_mdv + '.i1y')
                cmds.connectAttr(self.jnt_chain[1] + '.scaleZ', scale_mdv + '.i1z')
                for jnt in lower_twist:
                    cmds.connectAttr(scale_mdv + '.o', jnt + '.s', force=True)

        # -- Connect FK Scale
        cmds.connectAttr(scale_bc + '.output.outputR', self.jnt_chain[0] + '.scaleX')
        cmds.connectAttr(scale_bc + '.output.outputG', self.jnt_chain[1] + '.scaleX')
        cmds.connectAttr(fk_chain[0] + '.Stretch', fk_chain[0] + '.scaleX')
        cmds.connectAttr(fk_chain[1] + '.Stretch', fk_chain[1] + '.scaleX')
        stretch_md = cmds.shadingNode('multiplyDivide', au=True,
                                      name='{}_{}_Manual_Stretch_MD'.format(self.side, self.limb))
        cmds.connectAttr(ik_ctl[0] + '.%sStretch' % self.jnt_chain[0], stretch_md + '.i1x')
        cmds.connectAttr(ik_ctl[0] + '.%sStretch' % self.jnt_chain[1], stretch_md + '.i1y')
        jnt1 = cmds.getAttr(self.jnt_chain[1] + '.tx')
        jnt2 = cmds.getAttr(self.jnt_chain[2] + '.tx')
        value1 = jnt1 if self.side == 'L' else jnt1 * -1
        value2 = jnt2 if self.side == 'L' else jnt2 * -1
        cmds.setAttr(stretch_md + '.i2x', value1)
        cmds.setAttr(stretch_md + '.i2y', value2)
        add = cmds.shadingNode('addDoubleLinear', au=True, name='{}_{}_Stretch_ADL'.format(self.side, self.limb))
        cmds.connectAttr(stretch_md + '.ox', add + '.i1')
        cmds.connectAttr(stretch_md + '.oy', add + '.i2')
        cmds.connectAttr(add + '.output', distance_md + '.i2x')

        manual_md = cmds.shadingNode('multiplyDivide', au=True,
                                     name='{}_{}_Manual_Stretch_Result_MD'.format(self.side, self.limb))
        cmds.connectAttr(distance_md + '.ox', manual_md + '.i1x')
        cmds.connectAttr(distance_md + '.ox', manual_md + '.i1y')
        cmds.connectAttr(ik_ctl[0] + '.%sStretch' % self.jnt_chain[0], manual_md + '.i2x')
        cmds.connectAttr(ik_ctl[0] + '.%sStretch' % self.jnt_chain[1], manual_md + '.i2y')
        cmds.connectAttr(manual_md + '.ox', scale_bc + '.color1.color1R.')
        cmds.connectAttr(manual_md + '.oy', scale_bc + '.color1.color1G.')

        smooth_bc = cmds.shadingNode('blendColors', au=True, name='{}_{}_Smooth_Scale_BC'.format(self.side, self.limb))
        cmds.setAttr(smooth_bc + '.blender', 1)

        # -- SDK Stretch
        pm.setDrivenKeyframe(smooth_bc + '.color1R', currentDriver=distance_md + '.outputX')
        pm.keyframe(smooth_bc + '_color1R', floatChange=1, valueChange=1, index=0, option='over', absolute=1)
        pm.currentTime(1)
        pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        pm.keyTangent(itt='spline', ott='spline')
        pm.copyKey()
        pm.currentTime(2)
        cmds.pasteKey(floatOffset=0, option='merge', float=(2.0, 2.0), copies=1, valueOffset=1, connect=0, time=(1, 1),
                      timeOffset=0, an='objects')
        pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        pm.setInfinity(poi='linear')

        pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        pm.setInfinity(poi='linear')

        cmds.connectAttr(smooth_bc + '.outputR', manual_md + '.input1X', f=1)
        cmds.connectAttr(smooth_bc + '.outputR', manual_md + '.input1Y', f=1)

        linear_scale = cmds.select('{}_{}_Smooth_Scale_BC_color1R'.format(self.side, self.limb))
        cmds.rename(linear_scale, '{}_{}_Linear_Scale_SDK'.format(self.side, self.limb))
        cmds.duplicate(rr=1)
        smooth_scale = cmds.select('{}_{}_Linear_Scale_SDK1'.format(self.side, self.limb))
        cmds.rename(smooth_scale, '{}_{}_Smooth_Scale_SDK'.format(self.side, self.limb))

        linear_sdk = '{}_{}_Linear_Scale_SDK'.format(self.side, self.limb)
        smooth_sdk = '{}_{}_Smooth_Scale_SDK'.format(self.side, self.limb)

        cmds.connectAttr(distance_md + '.outputX', smooth_sdk + '.input')
        cmds.disconnectAttr(linear_sdk + '.output', smooth_bc + '.color1.color1R.')
        cmds.connectAttr(linear_sdk + '.output', smooth_bc + '.color2.color2R.')
        cmds.connectAttr(smooth_sdk + '.output', smooth_bc + '.color1.color1R.')
        cmds.connectAttr(ik_ctl[0] + '.smoothStretch', smooth_bc + '.blender')

        pm.currentTime(1)
        pm.selectKey(smooth_sdk, add=1, k=1, f=(1.0, 1.0))
        pm.copyKey()
        pm.currentTime(0)
        pm.pasteKey(floatOffset=0, option='merge', float=(0.0, 0.0), copies=1, valueOffset=1, connect=0, time=1,
                    timeOffset=0)
        pm.selectKey(smooth_sdk, add=1, k=1, f=(0.0, 0.0))
        pm.keyTangent(itt='fixed', ott='fixed')
        pm.keyframe(smooth_sdk, floatChange=0.75, valueChange=1, index=0, option='over', absolute=1)
        pm.keyTangent(smooth_sdk, a=1, outWeight=1, e=1, t=0.75, outAngle=-0.85)

        pm.selectKey(smooth_sdk, add=1, ot=True, f=(1.0, 1.0))
        pm.keyTangent(itt='linear', ott='linear')

        auto_bc = cmds.shadingNode('blendColors', au=True, name='{}_{}_Auto_Scale_BC'.format(self.side, self.limb))
        cmds.connectAttr(distance_md + '.outputX', auto_bc + '.color1.color1R.')
        cmds.setAttr(auto_bc + '.color2.color2R.', 1)
        cmds.disconnectAttr(distance_md + '.outputX', linear_sdk + '.input')
        cmds.disconnectAttr(distance_md + '.outputX', smooth_sdk + '.input')
        cmds.connectAttr(auto_bc + '.output.outputR', linear_sdk + '.input')
        cmds.connectAttr(auto_bc + '.output.outputR', smooth_sdk + '.input')
        cmds.connectAttr(ik_ctl[0] + '.autoStretch', auto_bc + '.blender')

        # -- Clean up module
        module_grp = cmds.group(n='{}_{}_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], module_grp, mo=False))
        setup_grp = cmds.group(n='{}_{}_Rig_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], setup_grp, mo=False))
        ctl_group = cmds.group(name='{}_{}_CTL_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], ctl_group, mo=False))
        fk_group = cmds.group(name='{}_{}_FK_CTL_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], fk_group, mo=False))

        cmds.parent(setup_grp, module_grp)
        cmds.parent(bend_sys_grp, module_grp)
        cmds.parent(ctl_group, setup_grp)
        cmds.parent(fk_group, ctl_group)

        cmds.parent(jnt_grp, setup_grp)
        cmds.parent(fk_chain[0], fk_group)
        cmds.parent('{}_IK_CTL_GRP'.format(self.jnt_chain[2]), ctl_group)
        cmds.parent('{}_{}_PV_CTL_GRP'.format(self.side, self.limb), ctl_group)
        cmds.parent('{}_{}_Bend_CTL_GRP'.format(self.side, self.limb), ctl_group)
        cmds.parent('{}_Upper{}_Target_00'.format(self.side, self.limb), jnt_grp)
        cmds.parent('{}_{}_IkHandleRP_GRP'.format(self.side, self.limb).format(self.side),
                    '{}_Null'.format(self.jnt_chain[2]))
        if self.limb == 'Arm':
            cmds.parent('{}_{}_Fingers_CTL_GRP'.format(self.side, self.limb), ctl_group)

        # --- PV position
        for i in 'XYZ':
            cmds.setAttr('{}_{}_PV_CTL_GRP.rotate{}'.format(self.side, self.limb, i), 0)
        pos = cmds.getAttr(distance + '.d') / 4 if self.side == 'L' else (cmds.getAttr(distance + '.d') / 4) * -1
        rot = 180 if self.side == 'R' else 0
        cmds.setAttr('{}_{}_PV_CTL_GRP.translateX'.format(self.side, self.limb), pos)
        cmds.setAttr('{}_{}_PV_CTL_GRP.rotateX'.format(self.side, self.limb), rot)
        if self.limb == 'Leg':
            cmds.setAttr('{}_{}_PV_CTL_GRP.rotateZ'.format(self.side, self.limb), 90)

        # -- Switch position and parent
        sw_pos = -self.ctlSize * 2 if self.side == 'L' else -self.ctlSize * 2
        cmds.setAttr('{}_{}_Switch_CTL_OFF'.format(self.side, self.limb) + '.translateZ', sw_pos)
        matrix.Constraint([self.jnt_chain[2], '{}_{}_Switch_CTL_OFF'.format(self.side, self.limb)],
                          mo=True, jnt=False, point=True, orient=True, scale=True)
        cmds.parent('{}_{}_Switch_CTL_GRP'.format(self.side, self.limb), ctl_group)
        cmds.setAttr(switch[0] + '.IKSwitch', 1)

        self.limb_ctl()

        matrix.SwitchConstraint([ik_ctl[0], fk_chain[2], self.jnt_chain[2]], switch_ctl=switch[0],
                                switch_attr='IKSwitch', mo=True, jnt=True, point=False, orient=True, scale=False)

        if self.limb == 'Leg':
            cmds.parent('{}_foot_GRP'.format(self.side), '{}_IK_CTL'.format(self.jnt_chain[2]))
            cmds.duplicate('{}_bankIn_CTL'.format(self.side), name='{}_ball_CTL'.format(self.side))
            cmds.delete(cmds.parentConstraint('{}_ball'.format(self.side), '{}_ball_CTL'.format(self.side)))
            cmds.parent('{}_ball_CTL'.format(self.side), '{}_bankIn_CTL'.format(self.side))

            cmds.parent('{}_Null'.format(self.jnt_chain[2]), '{}_ball_CTL'.format(self.side))

            cmds.ikHandle(sj='{}_ankle'.format(self.side), ee='{}_ball'.format(self.side), sol='ikSCsolver',
                          name='{}_ankle_IKH_RP'.format(self.side))
            cmds.ikHandle(sj='{}_ball'.format(self.side), ee='{}_ball_end'.format(self.side), sol='ikSCsolver',
                          name='{}_ball_IKH_RP'.format(self.side))

            offset.offset_grp(['{}_ankle_IKH_RP'.format(self.side)], 'GRP')
            offset.offset_grp(['{}_ball_IKH_RP'.format(self.side)], 'GRP')
            cmds.parent('{}_ankle_IKH_RP_GRP'.format(self.side), '{}_bankIn_CTL'.format(self.side))
            cmds.parent('{}_ball_IKH_RP_GRP'.format(self.side), '{}_bankIn_CTL'.format(self.side))
            cmds.setAttr('{}_ankle_IKH_RP_GRP.visibility'.format(self.side), 0)
            cmds.setAttr('{}_ball_IKH_RP_GRP.visibility'.format(self.side), 0)
            cmds.connectAttr(switch[0] + '.IKSwitch', '{}_ankle_IKH_RP.ikBlend'.format(self.side))
            cmds.connectAttr(switch[0] + '.IKSwitch', '{}_ball_IKH_RP.ikBlend'.format(self.side))
            cmds.rename('{}_ball1'.format(self.side), '{}_ball_FK_CTL'.format(self.side))
            cmds.rename('{}_ball_end1'.format(self.side), '{}_ball_end_FK_CTL'.format(self.side))
            matrix.Constraint(['{}_ball_FK_CTL'.format(self.side), '{}_ball'.format(self.side)],
                              mo=True, jnt=True, point=False, orient=True, scale=False)
            cmds.setAttr('{}_ball.overrideEnabled'.format(self.side), 1)
            cmds.setAttr('{}_ball_end.overrideEnabled'.format(self.side), 1)
            color = 15 if self.side == 'L' else 4
            cmds.setAttr('{}_ball.overrideColor'.format(self.side), color)
            cmds.setAttr('{}_ball_end.overrideColor'.format(self.side), color)
            # cmds.setAttr('{}_ball_FK_CTL.visibility'.format(self.side), 0)
            cmds.delete('{}_ball_end_FK_CTL'.format(self.side))

        elif self.limb == 'Arm':
            matrix.SwitchConstraint([ik_ctl[0], fk_chain[2], '{}_{}_Fingers_CTL_GRP'.format(self.side, self.limb)],
                                    switch_ctl=switch[0], switch_attr='IKSwitch', mo=True, jnt=False, point=False,
                                    orient=True, scale=False)

            matrix.Constraint([self.jnt_chain[2], '{}_{}_Fingers_CTL_GRP'.format(self.side, self.limb)],
                              mo=False, jnt=False, point=True, orient=False, scale=False)

        # -- Color controls
        ctls = cmds.ls('{}_*CTLShape'.format(self.side))
        for i in ctls:
            cmds.setAttr(i + '.overrideEnabled', True)
            if self.side == 'L':
                cmds.setAttr(i + '.overrideColor', 6)
            elif self.side == 'R':
                cmds.setAttr(i + '.overrideColor', 13)
        # self.lineWidth(ctls, 1.5)

        # -- hide fk control jnts
        for ctl in fk_chain:
            cmds.setAttr(ctl + '.drawStyle', 2)
        if self.limb == 'Arm':
            for jnt in ['pinky', 'ring', 'middle', 'index', 'thumb']:
                count = 4 if jnt == 'thumb' else 5
                for i in range(count):
                    cmds.setAttr('{}_{}_0{}_FK_CTL'.format(self.side, jnt, i) + '.drawStyle', 2)
        # self.lineWidth(fk_chain, 1.5)
        for jnt in self.jnt_chain:
            cmds.setAttr(jnt + '.overrideDisplayType', 1)

    def limb_ctl(self):
        """Create Main control."""
        main_ctl = cmds.circle(n='{}_{}_Main_CTL'.format(self.side, self.limb), nr=(1, 0, 0), r=self.ctlSize * 1.1, d=1,
                               s=20, ch=False)
        offset.offset_grp(main_ctl, 'GRP')
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], main_ctl[0] + '_GRP', mo=False))
        cmds.parent('{}_GRP'.format(main_ctl[0]), '{}_{}_CTL_GRP'.format(self.side, self.limb))
        cmds.parent('{}_{}_FK_CTL_GRP'.format(self.side, self.limb), main_ctl[0])
        matrix.Constraint([main_ctl[0], self.jnt_chain[0]], mo=True, jnt=False, point=True, orient=False, scale=False)
        matrix.Constraint([main_ctl[0], '{}_{}_JNT_OFF_GRP'.format(self.side, self.limb)],
                          mo=True, jnt=False, point=True, orient=True, scale=True)

        if self.limb == 'Arm':
            clavicle_ctl = cmds.circle(n='{}_Clavicle_CTL'.format(self.side), nr=(1, 0, 0), r=self.ctlSize * 1.6, d=1,
                                       s=4, ch=False)
            offset.offset_grp(clavicle_ctl, 'GRP')
            cmds.delete(cmds.parentConstraint('{}_clavicle'.format(self.side), clavicle_ctl[0] + '_GRP', mo=False))
            cmds.parent('{}_Clavicle_CTL_GRP'.format(self.side), '{}_{}_CTL_GRP'.format(self.side, self.limb))
            cmds.parent('{}_{}_Main_CTL_GRP'.format(self.side, self.limb), clavicle_ctl)
            cmds.setAttr('{}_clavicle.overrideEnabled'.format(self.side), True)
            color = 15 if self.side == 'L' else 4
            cmds.setAttr('{}_clavicle.overrideColor'.format(self.side), color)

    # def bindJoints(self):
    #     bind_joints = []
    #     for part in ['Upper', 'Lower']:
    #         for i in range(4):
    #             bind_joints.append('{}_{}{}_Twist_0{}'.format(self.side, part, self.limb, i))
    #
    #     if self.limb == 'Leg':
    #         bind_joints.append('{}_Ankle'.format(self.side))
    #         bind_joints.append('{}_ball'.format(self.side))
    #     else:
    #         bind_joints.append('{}_Wrist'.format(self.side))
    #         bind_joints.append()
    #
    #     return bind_joints

    @staticmethod
    def get_pos_as_mvector(pv_node):
        """Get a transform position as an MVector instance.

        :arg:
            node (str): Name of transform.

        :returns:
            MVector: Position of given transform node.
        """
        pos = cmds.xform(pv_node, query=True, translation=True, worldSpace=True)
        return OpenMaya.MVector(pos)

    def place_pole_vector_ctrl(self, pv_ctrl, start, mid, end, shift_factor=2):
        """Position and orient the given poleVector control to avoid popping.

        :arg:
            pv_ctrl (str): Name of transform to be used as poleVector.
            start (str): Name of start joint.
            mid (str): Name of mid joint.
            end (str): Name of end joint.
            shift_factor (float): How far ctrl should be moved away from mid joint.
            side (str): Side L or R
        :returns:
            pv position (tuple): (0.0, 0.0, 0.0)
        """
        # Find mid-point between start and end joint
        start_pos = self.get_pos_as_mvector(start)
        end_pos = self.get_pos_as_mvector(end)
        center_pos = (start_pos + end_pos) / 2

        # Use vector from mid-point to mid joint...
        mid_pos = self.get_pos_as_mvector(mid)
        off = mid_pos - center_pos
        # Place the poleVector control
        pv_pos = center_pos + off * shift_factor
        cmds.xform(pv_ctrl, translation=pv_pos, worldSpace=True)

        # Orient ctrl so that the XY-plane coincides with plane of joint chain.
        aim_constraint = cmds.aimConstraint(
            mid,
            pv_ctrl,
            aimVector=(-1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType="object",
            worldUpObject=start,
        )
        cmds.delete(aim_constraint)

    @staticmethod
    def customControl(name):
        """Create a custom control node.

        :arg:
            name (str): Name of custom node.

        :returns:
            name (str): Name of custom node.
        """
        custom_control = '../templates/CustomControl.ma'
        cmds.file(custom_control, i=1)
        cmds.rename('Custom_CTL', name)
        cmds.rename('Custom_CTL_SC', name + 'CTL_SC')
        return name

    @staticmethod
    def cube_ctl(name, size):
        """Create a cube control control.

        :arg:
            name (str): Name of cube control.
            size (float): The Size of cube control.
        :returns:
            name of cube control

        """
        cmds.curve(n=name, d=1,
                   p=[(-size, -size, -size), (size, -size, -size), (size, -size, size), (-size, -size, size),
                      (-size, -size, -size), (-size, size, -size),
                      (size, size, -size), (size, size, size), (-size, size, size), (-size, size, -size),
                      (size, size, -size), (size, -size, -size),
                      (size, size, -size), (size, size, size), (size, -size, size), (-size, -size, size),
                      (-size, size, size), (-size, size, -size),
                      (-size, -size, -size)])
        shape = cmds.listRelatives(name, s=True)
        cmds.rename(shape, name + 'Shape')

        return name

    @staticmethod
    def lineWidth(ctl, width):
        """Modify line width of control curve.

        :arg:
            ctl (str): Name of control curve to be modified.
            width (float): The width of control curve.
        :returns:
            None
        """
        for i in ctl:
            cmds.setAttr(i + '.lineWidth', width)
