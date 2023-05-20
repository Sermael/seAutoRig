""" Create head module"""
from maya import cmds
from . import offset


class Head(object):
    def __init__(self, jnt_chain, side):

        self.jnt_chain = jnt_chain
        self.side = side

        # vars
        self.ctlSize = 1

    def rig(self):
        module_grp = cmds.group(n='{}_Head_GRP'.format(self.side), em=True)
        cmds.delete(cmds.parentConstraint(self.jnt_chain[0], module_grp, mo=False))

        head_extra = ['L_eye', 'head_end', 'jaw', 'jaw_end']
        for jnt in head_extra:
            cmds.parent(jnt, w=True)

        fk = cmds.duplicate(self.jnt_chain[0], rc=True)

        for jnt in range(3):
            cmds.rename(fk[jnt], '{}_{}_FK_CTL'.format(self.side, self.jnt_chain[jnt]))

        cmds.select('{}_{}_FK_CTL'.format(self.side, self.jnt_chain[0]), hi=True)
        fk_chain = cmds.ls(sl=1)

        # -- Color joints
        for jnt in self.jnt_chain:
            cmds.setAttr(jnt + '.overrideEnabled', True)
            cmds.setAttr(jnt + '.overrideColor', 17)

        for jnt in fk_chain:
            if jnt == 'C_head_FK_CTL':
                self.cube_ctl('{0}Shape'.format(jnt), 1.7)
                cmds.select('C_head_FK_CTLShapeShape.cv[0:18]')
                cmds.move(0, 1, 0, r=True, os=True, wd=True)
            else:
                cmds.circle(n='{0}Shape'.format(jnt), nr=(0, 1, 0), r=self.ctlSize * 1.8, ch=False)

            cmds.setAttr('{}'.format(jnt) + '.overrideEnabled', True)
            cmds.setAttr('{}'.format(jnt) + '.overrideColor', 17)
            cmds.parent('{}ShapeShape'.format(jnt), jnt, r=True, s=True)
            cmds.delete(jnt + 'Shape')

        offset.offset_grp(fk_chain, 'GRP')
        offset.offset_grp(fk_chain, 'OFF')
        offset.offset_grp(fk_chain, 'SDK')

        cmds.parent('{}_{}_FK_CTL_GRP'.format(self.side, self.jnt_chain[0]), module_grp)

        mdv1 = cmds.shadingNode('multiplyDivide', n="{}_{}_MDV".format(self.side, self.jnt_chain[0]), au=True)
        mdv2 = cmds.shadingNode('multiplyDivide', n="{}_{}_MDV".format(self.side, self.jnt_chain[1]), au=True)
        cmds.addAttr(fk_chain[2], shortName='NeckFollow', longName='NeckFollow', defaultValue=0.0, minValue=0,
                     maxValue=1.0, k=True)
        cmds.addAttr(fk_chain[0], shortName='SpineOrient', longName='SpineOrient', defaultValue=0.0, minValue=0,
                     maxValue=1.0, k=True)
        cmds.addAttr(fk_chain[2], shortName='SpineOrient', longName='SpineOrient', defaultValue=0.0, minValue=0,
                     maxValue=1.0, k=True)
        cmds.connectAttr(fk_chain[2] + '.r', mdv1 + '.i1')
        cmds.connectAttr(fk_chain[2] + '.r', mdv2 + '.i1')
        cmds.connectAttr(mdv1 + '.o', "{}_{}_FK_CTL_SDK.r".format(self.side, self.jnt_chain[0]))
        cmds.connectAttr(mdv2 + '.o', "{}_{}_FK_CTL_SDK.r".format(self.side, self.jnt_chain[1]))
        for axis in 'XYZ':
            cmds.connectAttr(fk_chain[2] + '.NeckFollow', mdv1 + '.input2.input2{}'.format(axis))
            cmds.connectAttr(fk_chain[2] + '.NeckFollow', mdv2 + '.input2.input2{}'.format(axis))

        head_extra = ['L_eye', 'head_end', 'jaw', 'jaw_end']
        for jnt in head_extra:
            cmds.parent(jnt, 'C_head_FK_CTL')

        cmds.setAttr('neck_01.v', 0)

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
