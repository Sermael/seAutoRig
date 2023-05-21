""" Create spine module - Sergio Efigenio - 05/02/2023"""
import importlib
from maya import cmds

from . import node
from . import offset

importlib.reload(node)
importlib.reload(offset)


class Spine(object):
    """
    A class used to represent an Spine rig

    :arg:
        jnt_chain (list): ['spine01_jnt', 'spine02_jnt', 'spine03_jnt'] a list of 3 joints to build the spine
        side (str): 'C' the side of the spine
        limb (str): 'Spine' the name of the spine

    :rtype:
        object

    Methods:
            rig()
            Build the spine system

    """

    def __init__(self, jnt_chain, side, limb):

        self.jnt_chain = jnt_chain
        self.side = side
        self.limb = limb

        # vars
        self.node = node.Node()
        self.ctlSize = 3

    def rig(self):
        # -- Calculate distance
        dist = cmds.shadingNode('distanceBetween', n='{}_{}_DB'.format(self.side, self.limb), asUtility=True)
        cmds.connectAttr(self.jnt_chain[0] + '.worldMatrix[0]', dist + '.inMatrix1', f=1)
        cmds.connectAttr(self.jnt_chain[2] + '.worldMatrix[0]', dist + '.inMatrix2', f=1)
        dist_val = cmds.getAttr(dist + '.distance')

        # -- Create Nurbs
        nrb = cmds.nurbsPlane(n='{}_{}_NRB'.format(self.side, self.limb), ch=1, d=3, v=2,
                              p=(0, 0, 0), u=1, w=1, ax=(0, 0, 1), lr=dist_val)
        cmds.delete(cmds.pointConstraint(self.jnt_chain[1], nrb, mo=False))
        cmds.select(nrb)
        cmds.makeIdentity(n=0, s=1, r=1, t=1, apply=True, pn=1)
        cmds.delete(nrb[0], constructionHistory=True)
        cmds.setAttr(nrb[0] + '.inheritsTransform', 0)

        spine_ctl = []
        spine_jnt = []
        num = 0
        for jnt in range(5):
            name = 'Spine0%s' % num

            posi = cmds.createNode('pointOnSurfaceInfo', n='{}_{}_POSI'.format(self.side, name))
            aim = cmds.createNode('aimConstraint', n='{}_{}_AIM'.format(self.side, name))
            cm = cmds.createNode('composeMatrix', n='{}_{}_CM'.format(self.side, name))
            mm = cmds.shadingNode('multMatrix', asUtility=True, n='{}_{}_MM'.format(self.side, name))
            dm = cmds.createNode('decomposeMatrix', n='{}_{}_DM'.format(self.side, name))
            off = cmds.createNode('transform', n='{}_{}_OFF'.format(self.side, name))
            sdk = cmds.createNode('transform', n='{}_{}_SDK'.format(self.side, name), p=off)
            vol = cmds.createNode('transform', n='{}_{}_VOL'.format(self.side, name), p=sdk)
            cmds.setAttr(off + '.inheritsTransform', 0)
            cmds.select(vol)
            bind = cmds.joint(name='{}_{}'.format(self.side, name))
            spine_jnt.append(bind)

            # -- Set pointOnSurfaceInfo
            pv = {
                '{}00'.format(self.limb): 0,
                '{}01'.format(self.limb): 0.25,
                '{}02'.format(self.limb): 0.5,
                '{}03'.format(self.limb): 0.75,
                '{}04'.format(self.limb): 1
            }

            cmds.setAttr(posi + '.parameterU', 0.5)
            cmds.setAttr(posi + '.parameterV', pv[name])

            cmds.connectAttr(nrb[0] + 'Shape.worldSpace[0]', posi + '.inputSurface', f=1)
            cmds.connectAttr(cm + '.outputMatrix', mm + '.matrixIn[0]', f=1)
            cmds.connectAttr(mm + '.matrixSum', dm + '.inputMatrix', f=1)

            for i in 'XYZ':
                cmds.connectAttr(posi + '.normal%s' % i, aim + '.target[0].targetTranslate%s' % i, f=1)
                cmds.connectAttr(posi + '.tangentV%s' % i.lower(), aim + '.worldUpVector%s' % i, f=1)
                cmds.connectAttr(posi + '.position%s' % i, cm + '.inputTranslate%s' % i, f=1)
                cmds.connectAttr(aim + '.constraintRotate%s' % i, cm + '.inputRotate%s' % i, f=1)
                cmds.connectAttr(dm + '.outputTranslate%s' % i, off + '.translate%s' % i, f=1)
                cmds.connectAttr(dm + '.outputRotate%s' % i, off + '.rotate%s' % i, f=1)

            if 0 < jnt < 4:
                ctl = cmds.circle(n='{}_{}_CTL'.format(self.side, name), nr=(0, 1, 0), r=self.ctlSize * 0.9, ch=False)
                spine_ctl.append(ctl[0])
            else:
                ctl = self.cube_ctl('{}_{}_CTL'.format(self.side, name), 2)
                spine_ctl.append(ctl)
                if jnt == 0:
                    ctl = cmds.select("C_Spine00_CTLShape.cv[0:18]")
                    cmds.scale(1.3, 0.5, 1, ctl, r=True, ocp=True)
                elif jnt == 4:
                    ctl = cmds.select("C_Spine04_CTLShape.cv[0:18]")
                    cmds.scale(1.1, 0.6, 1, ctl, r=True, ocp=True)

            cmds.setAttr('{}_{}_CTLShape'.format(self.side, name) + '.overrideEnabled', True)
            cmds.setAttr('{}_{}_CTLShape'.format(self.side, name) + '.overrideColor', 17)
            offset.offset_grp(['{}_{}_CTL'.format(self.side, name)], 'SDK')
            offset.offset_grp(['{}_{}_CTL'.format(self.side, name)], 'OFF')
            cmds.delete(cmds.pointConstraint(bind, '{}_{}_CTL_SDK'.format(self.side, name), mo=False))
            num = num + 1

        for jnt in spine_jnt:
            cmds.setAttr(jnt + '.overrideEnabled', True)
            cmds.setAttr(jnt + '.overrideColor', 22)

        cmds.parent(spine_ctl[4] + '_SDK', spine_ctl[3])
        cmds.parent(spine_ctl[3] + '_SDK', spine_ctl[1])
        cmds.parent(spine_ctl[2] + '_SDK', spine_ctl[1])
        cmds.parent(spine_ctl[1] + '_SDK', spine_ctl[0])
        cmds.parent(self.jnt_chain[0], spine_ctl[0])
        cmds.parent(self.jnt_chain[1], spine_ctl[2])
        cmds.parent(self.jnt_chain[2], spine_ctl[4])

        cmds.skinCluster(self.jnt_chain[0], self.jnt_chain[1], self.jnt_chain[2], nrb[0], mi=2, dr=1)

        # -- Chest ctl
        chest_ctl = cmds.circle(n='{}_Chest_CTL'.format(self.side), nr=(0, 1, 0), r=self.ctlSize * 0.8, ch=False)
        cmds.setAttr(chest_ctl[0] + 'Shape.overrideEnabled', True)
        cmds.setAttr(chest_ctl[0] + 'Shape.overrideColor', 18)
        # cmds.setAttr(chest_ctl[0] + 'Shape.lineWidth', 1.5)
        chest_jnt = cmds.joint(name='{}_Chest_JNT'.format(self.side))
        offset.offset_grp(chest_ctl, 'SDK')
        offset.offset_grp(chest_ctl, 'OFF')
        cmds.delete(cmds.pointConstraint(spine_ctl[4], chest_ctl[0] + '_SDK', mo=False))
        cmds.delete(cmds.pointConstraint(spine_ctl[4], chest_jnt, mo=False))
        cmds.parent(chest_ctl[0] + '_SDK', spine_ctl[4])

        # -- Pelvis ctl
        pelvis_ctl = cmds.circle(n='{}_Pelvis_CTL'.format(self.side), nr=(0, 1, 0), r=self.ctlSize, ch=False)
        cmds.setAttr(pelvis_ctl[0] + 'Shape.overrideEnabled', True)
        cmds.setAttr(pelvis_ctl[0] + 'Shape.overrideColor', 18)
        # cmds.setAttr(pelvis_ctl[0] + 'Shape.lineWidth', 1.5)
        offset.offset_grp(pelvis_ctl, 'SDK')
        offset.offset_grp(pelvis_ctl, 'OFF')
        cmds.delete(cmds.pointConstraint(spine_ctl[0], pelvis_ctl[0] + '_SDK', mo=False))
        cmds.parent(pelvis_ctl[0] + '_SDK', spine_ctl[0])
        cmds.parent(self.jnt_chain[0], pelvis_ctl[0])

        # -- Mid ctl pos
        for loc in ['Chest', self.limb, 'Pelvis']:
            locator = cmds.spaceLocator(n='{}_{}_LOC'.format(self.side, loc))
            cmds.setAttr(locator[0] + '.v', 0)
            offset.offset_grp(locator, 'OFF')
            offset.offset_grp(locator, 'SDK')
            cmds.parent('{}_{}_LOC_OFF'.format(self.side, loc), spine_ctl[0])

            if loc == 'Chest':
                cmds.delete(cmds.pointConstraint(chest_ctl[0], '{}_{}_LOC_OFF'.format(self.side, loc), mo=False))
                for i in 'xyz':
                    cmds.connectAttr(spine_ctl[4] + '.t{}'.format(i), '{}_{}_LOC.t{}'.format(self.side, loc, i))
            elif loc == 'Pelvis':
                cmds.delete(cmds.pointConstraint(spine_ctl[0], '{}_{}_LOC_OFF'.format(self.side, loc), mo=False))
                for i in 'xyz':
                    cmds.connectAttr(pelvis_ctl[0] + '.t{}'.format(i), '{}_{}_LOC.t{}'.format(self.side, loc, i))
                cmds.aimConstraint('C_Chest_LOC', 'C_Pelvis_LOC', aim=(0.0, 1.0, 0.0), wu=(0.0, 0.0, 1.0),
                                   u=(0.0, 0.0, 1.0), wut='objectrotation', wuo='C_Chest_LOC', mo=True)
            else:
                cmds.delete(cmds.pointConstraint(spine_ctl[2], '{}_{}_LOC_OFF'.format(self.side, loc)))
                self.node.create('blendColors', side='C', description=self.limb, skipSelect=True, parent=None)
                self.node.create('blendColors', side='C', description='{}_follow'.format(self.limb),
                                 skipSelect=True, parent=None)

        for i, c in zip('xyz', 'RGB'):
            cmds.connectAttr('C_Chest_LOC.t{}'.format(i), 'C_{}_BLC.color1{}'.format(self.limb, c))
            cmds.connectAttr('C_Pelvis_LOC.t{}'.format(i), 'C_{}_BLC.color2{}'.format(self.limb, c))
            cmds.connectAttr('C_{}_BLC.output{}'.format(self.limb, c),
                             'C_{}_LOC.translate{}'.format(self.limb, i.upper()))
            cmds.connectAttr('C_Pelvis_LOC.rotate{}'.format(i.upper()),
                             'C_{}_LOC.rotate{}'.format(self.limb, i.upper()))
            cmds.connectAttr('C_{}_LOC.rotate{}'.format(self.limb, i.upper()),
                             'C_{}_follow_BLC.color1{}'.format(self.limb, c))
            cmds.connectAttr('C_{}_follow_BLC.output{}'.format(self.limb, c),
                             spine_ctl[2] + '_OFF.rotate{}'.format(i.upper()))

        cmds.addAttr(spine_ctl[2], shortName='followRotation', longName='followRotation', defaultValue=1.0, minValue=0,
                     maxValue=1, k=True)
        cmds.connectAttr(spine_ctl[2] + '.followRotation', 'C_{}_follow_BLC.blender'.format(self.limb))
        cmds.setAttr('C_{}_follow_BLC.color2B'.format(self.limb), 0)
        cmds.parentConstraint(spine_ctl[4], 'C_Pelvis_CTL', spine_ctl[2] + '_SDK', mo=True)

        # -- Group Joints
        jnt_off_grp = cmds.group(n='{}_{}_JNT_OFF_GRP'.format(self.side, self.limb), em=True)
        cmds.parent(['C_{}0{}_OFF'.format(self.limb, i) for i in range(5)], jnt_off_grp)
        jnt_grp = cmds.group(n='{}_{}_JNT_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(spine_ctl[0], jnt_grp, mo=False))
        cmds.parent(jnt_off_grp, jnt_grp)

        # -- Create module grp
        module_ctl = cmds.group(n='{}_{}_GRP'.format(self.side, self.limb), em=True)
        cmds.delete(cmds.parentConstraint(spine_ctl[0], module_ctl, mo=False))

        # -- Define CV Points
        cvp0 = cmds.xform(spine_ctl[0], query=True, worldSpace=True, translation=True)
        cvp1 = cmds.xform(spine_ctl[1], query=True, worldSpace=True, translation=True)
        cvp2 = cmds.xform(spine_ctl[2], query=True, worldSpace=True, translation=True)
        cvp3 = cmds.xform(spine_ctl[3], query=True, worldSpace=True, translation=True)
        cvp4 = cmds.xform(spine_ctl[4], query=True, worldSpace=True, translation=True)

        # -- Create Curve
        for i in ['Start', 'End']:
            cv = cmds.curve(p=[cvp0, cvp1, cvp2, cvp3, cvp4], k=[0, 0, 0, 1, 2, 2, 2], d=3,
                            n='{}_{}{}_CV'.format(self.side, self.limb, i))
            cmds.setAttr(cv + '.v', 0)
            cv_inf = cmds.shadingNode('curveInfo', n='{}_{}{}_INF'.format(self.side, self.limb, i), au=True)
            cmds.connectAttr(cv + '.worldSpace[0]', cv_inf + '.inputCurve')

            if i == 'End':
                for channel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
                    cmds.setAttr(cv + '.' + channel, lock=True)
                cmds.skinCluster(self.jnt_chain[0], self.jnt_chain[1], self.jnt_chain[2], cv, mi=2, dr=1)

        vol_mdv = cmds.shadingNode('multiplyDivide', n='{}_{}_VOL_MDV'.format(self.side, self.limb), au=True)
        cmds.setAttr(vol_mdv + '.operation', 2)
        cmds.connectAttr('{}_{}Start_INF.arcLength'.format(self.side, self.limb), vol_mdv + '.input1.input1X.')
        cmds.connectAttr('{}_{}End_INF.arcLength'.format(self.side, self.limb), vol_mdv + '.input2.input2X.')

        cmds.move(cvp0[0], cvp0[1], cvp0[2], '{}_{}Start_CV.scalePivot'.format(self.side, self.limb),
                  '{}_{}Start_CV.rotatePivot'.format(self.side, self.limb), absolute=True)

        cmds.aimConstraint('C_Chest_LOC', '{}_{}Start_CV'.format(self.side, self.limb),
                           aim=(0.0, 1.0, 0.0), wu=(1.0, 0.0, 0.0), u=(1.0, 0.0, 0.0),
                           wut='objectrotation', wuo=pelvis_ctl[0], mo=True)

        plus_add = cmds.shadingNode('plusMinusAverage', n='{}_Distance_ADD'.format(self.limb), au=True)
        dist_md = cmds.shadingNode('multiplyDivide', n='{}_Distance_MDV'.format(self.limb), au=True)
        cmds.setAttr(dist_md + '.operation', 2)
        dist = cmds.getAttr(dist + '.distance')
        cmds.setAttr(dist_md + '.i2x', dist)
        cmds.connectAttr(spine_ctl[1] + '_SDK.ty', plus_add + '.input1D[0]')
        cmds.connectAttr(spine_ctl[3] + '_SDK.ty', plus_add + '.input1D[1]')
        cmds.connectAttr(spine_ctl[4] + '_SDK.ty', plus_add + '.input1D[2]')
        cmds.connectAttr(plus_add + '.output1D', dist_md + '.input1X')
        cmds.connectAttr(dist_md + '.outputX', '{}_{}Start_CV.sx'.format(self.side, self.limb))
        cmds.connectAttr(dist_md + '.outputX', '{}_{}Start_CV.sy'.format(self.side, self.limb))
        cmds.connectAttr(dist_md + '.outputX', '{}_{}Start_CV.sz'.format(self.side, self.limb))
        cmds.connectAttr('{}_{}Start_CV.s'.format(self.side, self.limb), self.jnt_chain[0] + '.s')
        stretch_cnd = cmds.shadingNode('condition', n='{}_{}_AutoStretch_CND'.format(self.side, self.limb), au=True)
        stretch_bc = cmds.shadingNode('blendColors', n='{}_{}_Stretch_BC'.format(self.side, self.limb), au=True)
        cmds.addAttr(spine_ctl[4], shortName='AutoStretch', longName='AutoStretch',
                     defaultValue=1.0, minValue=0, maxValue=1, k=True)
        cmds.addAttr(spine_ctl[4], shortName='Stretch', longName='Stretch',
                     defaultValue=10, minValue=0, maxValue=10, k=True)

        stretch_md = cmds.shadingNode('multiplyDivide', n='{}_{}_stretch_MDV'.format(self.side, self.limb), au=True)
        cmds.setAttr(stretch_md + '.i2x', 0.1)
        cmds.connectAttr(spine_ctl[4] + '.Stretch', stretch_md + '.i1x')
        cmds.connectAttr(stretch_md + '.ox', stretch_bc + '.blender')
        cmds.setAttr(stretch_cnd + '.secondTerm', 1)
        cmds.connectAttr(spine_ctl[4] + '.AutoStretch', stretch_cnd + '.firstTerm')
        cmds.connectAttr(vol_mdv + '.outputX', stretch_bc + '.color1.color1R')
        cmds.connectAttr(stretch_bc + '.outputR', stretch_cnd + '.colorIfTrue.colorIfTrueR')

        stretch_rv = cmds.shadingNode('remapValue', n='{}_{}_stretch_RV'.format(self.side, self.limb), au=True)
        cmds.connectAttr(stretch_cnd + '.outColor.outColorR', stretch_rv + '.inputValue')

        # anim_curve = cmds.createNode('animCurveUU', name='{}_{}_stretch_ACUU'.format(side, limb))
        #
        # cmds.setKeyframe(anim_curve, t=0, v=0, itt='flat', ott='flat')
        # cmds.setKeyframe(anim_curve, t=1, v=1, itt='flat', ott='flat')
        # cmds.setKeyframe(anim_curve, t=(1 / 2), v=amplitude, itt='flat', ott='flat')
        #
        # # cmds.animCurveEditor('graphEditor1GraphEd', exists=True)
        #
        # # -- SDK Stretch
        # sdk = pm.setDrivenKeyframe(smooth_bc + '.color1R', currentDriver=distance_md + '.outputX')
        # pm.keyframe(smooth_bc + '_color1R', floatChange=1, valueChange=1, index=0, option='over', absolute=1)
        # pm.currentTime(1)
        # pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        # pm.keyTangent(itt='spline', ott='spline')
        # pm.copyKey()
        # pm.currentTime(2)
        # cmds.pasteKey(floatOffset=0, option='merge', float=(2.0, 2.0), copies=1, valueOffset=1, connect=0,
        # time=(1, 1),timeOffset=0, an='objects')
        # pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        # pm.setInfinity(poi='linear')
        #
        # pm.selectKey(smooth_bc + '_color1R', add=1, k=1, f=(1.0, 1.0))
        # pm.setInfinity(poi='linear')

        for axis in 'xz':
            for jnt in range(1, 5):
                cmds.connectAttr(stretch_cnd + '.outColor.outColorR', 'C_{}0{}_VOL.s{}'.format(self.limb, jnt, axis))
                # cmds.connectAttr(stretch_rv + '.outValue', 'C_{}0{}_VOL.s{}'.format(limb, jnt, axis))

        # -- Cleanup
        bend_grp = cmds.createNode('transform', n='{}_{}_BendSystem_GRP'.format(self.side, self.limb))
        cmds.parent(bend_grp, module_ctl)
        cmds.setAttr('{}_{}_BendSystem_GRP.v'.format(self.side, self.limb), 0)
        cmds.parent('{}_{}End_CV'.format(self.side, self.limb), '{}_{}_BendSystem_GRP'.format(self.side, self.limb))
        cmds.setAttr('{}_{}End_CV.inheritsTransform'.format(self.side, self.limb), 0)
        cmds.parent(nrb[0], bend_grp)

        cmds.parent(spine_ctl[0] + '_SDK', module_ctl)
        cmds.parent('C_{}_JNT_GRP'.format(self.limb), module_ctl)
        cmds.parent('{}_{}Start_CV'.format(self.side, self.limb), 'C_Pelvis_CTL')

        for i in range(5):
            cmds.parent('{}_{}0{}_AIM'.format(self.side, self.limb, i), 'C_{}_GRP'.format(self.limb))
            cmds.connectAttr(spine_ctl[0] + '.s', '{}_{}0{}_SDK.s'.format(self.side, self.limb, i))
            cmds.parent('{}_{}0{}_AIM'.format(self.side, self.limb, i), bend_grp)

        # hide joints
        for jnt in self.jnt_chain:
            if cmds.objExists(jnt):
                cmds.setAttr('{}.drawStyle'.format(jnt), 2)

        root_ctl = cmds.circle(n='C_root_CTL', nr=(0, 1, 0), r=self.ctlSize * 1.5, d=1, s=15, ch=False)
        cmds.setAttr('C_root_CTLShape' + '.overrideEnabled', True)
        cmds.setAttr('C_root_CTLShape' + '.overrideColor', 17)
        # cmds.setAttr('C_root_CTL.lineWidth', 1.5)
        cmds.delete(cmds.parentConstraint(spine_ctl[0], root_ctl, mo=False))
        offset.offset_grp(root_ctl, 'GRP')
        offset.offset_grp(root_ctl, 'OFF')
        # cmds.parent('root', 'C_Pelvis_CTL')
        cmds.parent('C_root_CTL_GRP', 'C_Spine_GRP')
        cmds.parent('C_Spine00_CTL_SDK', 'C_root_CTL')

        # for ctl in spine_ctl:
        #     cmds.setAttr(ctl + 'Shape.lineWidth', 1.5)

        # print('Module: {}_{} Done.'.format(self.side, self.limb))

    @staticmethod
    def cube_ctl(name, size):
        """Create a cube control control.

        :param:
            name (str): Name of cube control.
            size (float): Size of cube control.
        """
        cmds.curve(n=name, d=1,
                   p=[(-size, -size, -size), (size, -size, -size), (size, -size, size), (-size, -size, size),
                      (-size, -size, -size), (-size, size, -size), (size, size, -size), (size, size, size),
                      (-size, size, size), (-size, size, -size), (size, size, -size), (size, -size, -size),
                      (size, size, -size), (size, size, size), (size, -size, size), (-size, -size, size),
                      (-size, size, size), (-size, size, -size), (-size, -size, -size)])
        shape = cmds.listRelatives(name, s=True)
        cmds.rename(shape, name + 'Shape')

        return name

    @staticmethod
    def lineWidth(controls, width):
        """
        To modify the line width of any control shape.

        :param controls: (list)
        :param width:
        :return:
        """
        for ctl in controls:
            cmds.setAttr(ctl + '.lineWidth', width)
