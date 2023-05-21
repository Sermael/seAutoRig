""" Create fingers module - Sergio Efigenio - 05/02/2023"""
from maya import cmds
from .offset import offset_grp


class Fingers(object):
    def __init__(self):
        self.ctlSize = 0.2

    def rig(self):
        for side in 'LR':
            module_grp = cmds.group(n='{}_Fingers_GRP'.format(side), em=True)
            cmds.parent(module_grp, '{}_wrist'.format(side))
            for jnt in ['pinky', 'ring', 'middle', 'index', 'thumb']:
                for i in range(4):
                    joint = '{}_{}_0{}'.format(side, jnt, i)
                    end_joint = '{}_{}_04'.format(side, jnt)
                    if i == 0:
                        offset_grp([joint], 'GRP')
                        cmds.parent(joint + '_GRP', module_grp)
                    offset_grp([joint], 'FIST')
                    cmds.circle(n='{}Shape'.format(joint), nr=(1, 0, 0), r=self.ctlSize, ch=False)
                    cmds.parent('{}ShapeShape'.format(joint), joint, r=True, s=True)
                    cmds.delete(joint + 'Shape')
                    cmds.setAttr(end_joint + '.drawStyle', 2)
                    cmds.setAttr(joint + '.drawStyle', 2)
                    color = 6 if side == 'L' else 13
                    cmds.setAttr('{}'.format(joint) + '.overrideEnabled', True)
                    cmds.setAttr('{}'.format(joint) + '.overrideColor', color)
