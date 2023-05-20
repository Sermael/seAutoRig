""" Constraint Matrix - Sergio Efigenio - 4/26/2022 - 2:37 """
import maya.cmds as cmds


class constraint:
    def __init__(self, node, mo, jnt, point, orient, scale):

        """
        This function get minimum of 2 selected nodes in order to work

        node = ['node', 'node']        First node of list will be the driver
        mo = True                      Will maintain the offset of the constrained nodes
        jnt = True                     Create multMatrix to drive the joint orient
        :rtype: object
        """

        self.node = node
        self.mo = mo
        self.jnt = jnt
        self.point = point
        self.orient = orient
        self.scale = scale

        driver = node[0]
        targets = node[1:]

        if not self.jnt:
            if not self.mo:
                for item in targets:
                    parent = cmds.listRelatives(item, p=True)
                    multMatrix = cmds.createNode('multMatrix', name='%s_MM' % item)
                    decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_DM' % item)
                    cmds.connectAttr(driver + '.worldMatrix', multMatrix + '.matrixIn[0]', force=True)
                    cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix + '.matrixIn[1]', force=True)
                    cmds.connectAttr(multMatrix + '.matrixSum', decomposeMatrix + '.inputMatrix', force=True)
                    # -- Connect item
                    if self.point:
                        cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                    if self.orient:
                        cmds.connectAttr(decomposeMatrix + '.or', item + '.r')
                    if self.scale:
                        cmds.connectAttr(decomposeMatrix + '.os', item + '.s')
            else:
                for item in targets:
                    parent = cmds.listRelatives(item, p=True)
                    if cmds.objExists(parent[0] + '.offsetAttr'):
                        attr = parent[0] + '.offsetAttr'
                    else:
                        attr = cmds.addAttr(parent[0], ln='offsetAttr', at='matrix')

                    # -- Create nodes
                    multMatrixTemp = cmds.createNode('multMatrix', name='%s_MMTemp' % item)
                    multMatrix = cmds.createNode('multMatrix', name='%s_MM' % item)
                    decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_DM' % item)

                    # -- Connect temp nodes
                    cmds.connectAttr(item + '.worldMatrix', multMatrixTemp + '.matrixIn[0]', force=True)
                    cmds.connectAttr(driver + '.worldInverseMatrix', multMatrixTemp + '.matrixIn[1]', force=True)
                    cmds.connectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr', force=True)
                    cmds.disconnectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr')

                    # -- Connect nodes
                    cmds.connectAttr(parent[0] + '.offsetAttr', multMatrix + '.matrixIn[0]', force=True)
                    cmds.connectAttr(driver + '.worldMatrix', multMatrix + '.matrixIn[1]', force=True)
                    cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix + '.matrixIn[2]', force=True)
                    cmds.connectAttr(multMatrix + '.matrixSum', decomposeMatrix + '.inputMatrix', force=True)

                    # -- Connect item
                    if self.point:
                        cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                    if self.orient:
                        cmds.connectAttr(decomposeMatrix + '.or', item + '.r')
                    if self.scale:
                        cmds.connectAttr(decomposeMatrix + '.os', item + '.s')

                    # -- Delete temp nodes
                    cmds.delete(multMatrixTemp)

        else:
            for item in targets:
                parent = cmds.listRelatives(item, p=True)

                # -- Create nodes
                multMatrix = cmds.createNode('multMatrix', name='%s_MM' % item)
                multMatrixO = cmds.createNode('multMatrix', name='%s_Orient_MM' % item)
                multMatrixR = cmds.createNode('multMatrix', name='%s_Rotate_MM' % item)
                composeMatrixO = cmds.createNode('composeMatrix', name='%s_CM' % item)
                inverseMatrix = cmds.createNode('inverseMatrix', name='%s_IM' % item)
                decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_DM' % item)
                decomposeMatrixO = cmds.createNode('decomposeMatrix', name='%s_Orient_DM' % item)

                # -- Connect translate and scale nodes
                cmds.connectAttr(driver + '.worldMatrix', multMatrix + '.matrixIn[0]')
                cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix + '.matrixIn[1]')
                cmds.connectAttr(multMatrix + '.matrixSum', decomposeMatrix + '.inputMatrix')

                # -- Connect Orient nodes
                cmds.connectAttr(item + '.jointOrient', composeMatrixO + '.inputRotate')
                cmds.disconnectAttr(item + '.jointOrient', composeMatrixO + '.inputRotate')
                cmds.connectAttr(composeMatrixO + '.outputMatrix', multMatrixO + '.matrixIn[0]')
                cmds.connectAttr(parent[0] + '.worldMatrix', multMatrixO + '.matrixIn[1]')
                cmds.connectAttr(multMatrixO + '.matrixSum', inverseMatrix + '.inputMatrix')
                cmds.connectAttr(driver + '.worldMatrix', multMatrixR + '.matrixIn[0]')
                cmds.connectAttr(inverseMatrix + '.outputMatrix', multMatrixR + '.matrixIn[1]')
                cmds.connectAttr(multMatrixR + '.matrixSum', decomposeMatrixO + '.inputMatrix')

                # -- Connect Joint
                if self.point:
                    cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                if self.orient:
                    cmds.connectAttr(decomposeMatrixO + '.or', item + '.r')
                if self.scale:
                    cmds.connectAttr(decomposeMatrix + '.os', item + '.s')


class SwitchConstraint():
    def __init__(self, node, switch_ctl, switch_attr, mo, jnt, point, orient, scale):
        '''
        This function get minimum of 2 selected nodes in order to work

        node = ['driver1', 'driver2', 'driven']     First 2 nodeS of list will be the drivers
        switch = 'STR'                              Object to put switch attr
        mo = True                                   Will maintain the offset of the constrained nodes
        jnt = True                                  Create multMatrix to drive the joint orient
        :rtype: object'''

        self.node = node
        self.switch_ctl = switch_ctl
        self.switch_attr = switch_attr
        self.mo = mo
        self.jnt = jnt
        self.point = point
        self.orient = orient
        self.scale = scale

        if self.node == 3:
            print('Select exactly 2 drivers first, then targets.')
        else:
            driver = self.node[:2]
            targets = self.node[2:]

            if not self.jnt:
                if not self.mo:
                    for item in targets:
                        parent = cmds.listRelatives(item, p=True)
                        if not parent:
                            print('The targets needs to have parent to work')
                        else:
                            # -- Create Nodes
                            multMatrix_1 = cmds.createNode('multMatrix', name='{}_{}_Switch_MM'.format(item, driver[0]))
                            multMatrix_2 = cmds.createNode('multMatrix', name='{}_{}_Switch_MM'.format(item, driver[1]))
                            blendMatrix = cmds.createNode('blendMatrix', name='%s_Switch_BM' % item)
                            decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_Switch_DM' % item)

                            # -- Connect Nodes
                            cmds.connectAttr(driver[0] + '.worldMatrix', multMatrix_1 + '.matrixIn[0]', force=True)
                            cmds.connectAttr(driver[1] + '.worldMatrix', multMatrix_2 + '.matrixIn[0]', force=True)
                            cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_1 + '.matrixIn[1]', force=True)
                            cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_2 + '.matrixIn[1]', force=True)
                            cmds.connectAttr(multMatrix_2 + '.matrixSum', blendMatrix + '.inputMatrix')
                            cmds.connectAttr(multMatrix_1 + '.matrixSum', blendMatrix + '.target[0].targetMatrix')

                            # # -- Connect Switch
                            # cmds.addAttr(self.switch_ctl, ln='{}_Switch'.format(self.switch_attr), at='double', min=0, max=1, dv=1, k=True)
                            # cmds.connectAttr('{}.{}_Switch'.format(self.switch_ctl, self.switch_attr), blendMatrix + '.envelope')
                            # cmds.connectAttr(blendMatrix + '.outputMatrix', decomposeMatrix + '.inputMatrix', force=True)

                            # -- Connect switch
                            switch = '{}.{}'.format(self.switch_ctl, self.switch_attr)
                            if cmds.objExists(switch):
                                cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                                 blendMatrix + '.envelope')
                                cmds.connectAttr(blendMatrix + '.outputMatrix', decomposeMatrix + '.inputMatrix',
                                                 force=True)
                            else:
                                cmds.addAttr(self.switch_ctl, ln='{}'.format(self.switch_attr),
                                             at='double', min=0, max=1, dv=1, k=True)
                                cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                                 blendMatrix + '.envelope')
                                cmds.connectAttr(blendMatrix + '.outputMatrix', decomposeMatrix + '.inputMatrix',
                                                 force=True)

                            # -- Connect item
                            if self.point:
                                cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                            if self.orient:
                                cmds.connectAttr(decomposeMatrix + '.or', item + '.r')
                            if self.scale:
                                cmds.connectAttr(decomposeMatrix + '.os', item + '.s')
                else:
                    for item in targets:
                        parent = cmds.listRelatives(item, p=True)
                        attr_1 = cmds.addAttr(parent[0], ln='offsetAttr1', at='matrix')
                        attr_2 = cmds.addAttr(parent[0], ln='offsetAttr2', at='matrix')

                        # -- Create nodes
                        multMatrixTemp = cmds.createNode('multMatrix', name='%s_MMTemp' % item)
                        multMatrix_1 = cmds.createNode('multMatrix', name='%s_Switch_MM' % driver[0])
                        multMatrix_2 = cmds.createNode('multMatrix', name='%s_Switch_MM' % driver[1])
                        blendMatrix = cmds.createNode('blendMatrix', name='%s_Switch_BM' % item)
                        decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_Switch_DM' % item)

                        # -- Connect temp nodes
                        cmds.connectAttr(item + '.worldMatrix', multMatrixTemp + '.matrixIn[0]', force=True)
                        cmds.connectAttr(driver[0] + '.worldInverseMatrix', multMatrixTemp + '.matrixIn[1]', force=True)
                        cmds.connectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr1', force=True)
                        cmds.disconnectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr1')
                        cmds.connectAttr(driver[1] + '.worldInverseMatrix', multMatrixTemp + '.matrixIn[1]', force=True)
                        cmds.connectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr2', force=True)
                        cmds.disconnectAttr(multMatrixTemp + '.matrixSum', parent[0] + '.offsetAttr2')

                        # -- Connect nodes
                        cmds.connectAttr(parent[0] + '.offsetAttr1', multMatrix_1 + '.matrixIn[0]', force=True)
                        cmds.connectAttr(driver[0] + '.worldMatrix', multMatrix_1 + '.matrixIn[1]', force=True)
                        cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_1 + '.matrixIn[2]', force=True)
                        cmds.connectAttr(parent[0] + '.offsetAttr2', multMatrix_2 + '.matrixIn[0]', force=True)
                        cmds.connectAttr(driver[1] + '.worldMatrix', multMatrix_2 + '.matrixIn[1]', force=True)
                        cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_2 + '.matrixIn[2]', force=True)
                        cmds.connectAttr(multMatrix_2 + '.matrixSum', blendMatrix + '.inputMatrix')
                        cmds.connectAttr(multMatrix_1 + '.matrixSum', blendMatrix + '.target[0].targetMatrix')
                        cmds.connectAttr(blendMatrix + '.outputMatrix', decomposeMatrix + '.inputMatrix', force=True)

                        # -- Connect switch
                        switch = '{}.{}'.format(self.switch_ctl, self.switch_attr)
                        if cmds.objExists(switch):
                            cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                             blendMatrix + '.envelope')
                        else:
                            cmds.addAttr(self.switch_ctl, ln='{}'.format(self.switch_attr),
                                         at='double', min=0, max=1, dv=1,k=True)
                            cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                             blendMatrix + '.envelope')

                        # -- Connect item
                        if self.point:
                            cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                        if self.orient:
                            cmds.connectAttr(decomposeMatrix + '.or', item + '.r')
                        if self.scale:
                            cmds.connectAttr(decomposeMatrix + '.os', item + '.s')

                        # -- Delete temp nodes
                        cmds.delete(multMatrixTemp)

            else:
                for item in targets:
                    parent = cmds.listRelatives(item, p=True)

                    # -- Create nodes
                    multMatrix_1 = cmds.createNode('multMatrix', name='{}_{}_MM'.format(item, driver[0]))
                    multMatrix_2 = cmds.createNode('multMatrix', name='{}_{}_MM'.format(item, driver[1]))
                    multMatrixO = cmds.createNode('multMatrix', name='%s_Orient_MM' % item)
                    multMatrixR_1 = cmds.createNode('multMatrix', name='{}_{}_Rotate_MM'.format(item, driver[0]))
                    multMatrixR_2 = cmds.createNode('multMatrix', name='{}_{}_Rotate_MM'.format(item, driver[1]))
                    composeMatrixO = cmds.createNode('composeMatrix', name='%s_CM' % item)
                    inverseMatrix = cmds.createNode('inverseMatrix', name='%s_IM' % item)
                    decomposeMatrix = cmds.createNode('decomposeMatrix', name='%s_DM' % item)
                    decomposeMatrixO = cmds.createNode('decomposeMatrix', name='%s_Orient_DM' % item)
                    blendMatrix_1 = cmds.createNode('blendMatrix', name='{}_{}_Switch_BM'.format(item, driver[0]))
                    blendMatrix_2 = cmds.createNode('blendMatrix', name='{}_{}_Switch_BM'.format(item, driver[1]))

                    # -- Connect translate and scale nodes
                    cmds.connectAttr(driver[0] + '.worldMatrix', multMatrix_1 + '.matrixIn[0]')
                    cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_1 + '.matrixIn[1]')
                    cmds.connectAttr(driver[1] + '.worldMatrix', multMatrix_2 + '.matrixIn[0]')
                    cmds.connectAttr(parent[0] + '.worldInverseMatrix', multMatrix_2 + '.matrixIn[1]')
                    cmds.connectAttr(multMatrix_2 + '.matrixSum', blendMatrix_1 + '.inputMatrix')
                    cmds.connectAttr(multMatrix_1 + '.matrixSum', blendMatrix_1 + '.target[0].targetMatrix')
                    cmds.connectAttr(blendMatrix_1 + '.outputMatrix', decomposeMatrix + '.inputMatrix', force=True)

                    # -- Connect Orient nodes
                    cmds.connectAttr(item + '.jointOrient', composeMatrixO + '.inputRotate')
                    cmds.disconnectAttr(item + '.jointOrient', composeMatrixO + '.inputRotate')
                    cmds.connectAttr(composeMatrixO + '.outputMatrix', multMatrixO + '.matrixIn[0]')
                    cmds.connectAttr(parent[0] + '.worldMatrix', multMatrixO + '.matrixIn[1]')
                    cmds.connectAttr(multMatrixO + '.matrixSum', inverseMatrix + '.inputMatrix')
                    cmds.connectAttr(driver[0] + '.worldMatrix', multMatrixR_1 + '.matrixIn[0]')
                    cmds.connectAttr(inverseMatrix + '.outputMatrix', multMatrixR_1 + '.matrixIn[1]')
                    cmds.connectAttr(driver[1] + '.worldMatrix', multMatrixR_2 + '.matrixIn[0]')
                    cmds.connectAttr(inverseMatrix + '.outputMatrix', multMatrixR_2 + '.matrixIn[1]')
                    cmds.connectAttr(multMatrixR_2 + '.matrixSum', blendMatrix_2 + '.inputMatrix')
                    cmds.connectAttr(multMatrixR_1 + '.matrixSum', blendMatrix_2 + '.target[0].targetMatrix')
                    cmds.connectAttr(blendMatrix_2 + '.outputMatrix', decomposeMatrixO + '.inputMatrix', force=True)

                    # -- Connect switch
                    switch = '{}.{}'.format(self.switch_ctl, self.switch_attr)
                    if cmds.objExists(switch):
                        cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                         blendMatrix_1 + '.envelope')
                        cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                         blendMatrix_2 + '.envelope')
                    else:
                        cmds.addAttr(self.switch_ctl, ln='{}'.format(self.switch_attr),
                                     at='double', min=0, max=1, dv=1, k=True)
                        cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                         blendMatrix_1 + '.envelope')
                        cmds.connectAttr('{}.{}'.format(self.switch_ctl, self.switch_attr),
                                         blendMatrix_2 + '.envelope')

                    # -- Connect Joint
                    if self.point:
                        cmds.connectAttr(decomposeMatrix + '.ot', item + '.t')
                    if self.orient:
                        cmds.connectAttr(decomposeMatrixO + '.or', item + '.r')
                    if self.scale:
                        cmds.connectAttr(decomposeMatrix + '.os', item + '.s')

# sel = cmds.ls(sl=1)
# switch = 'switch_ctl'
# x = constraint(sel, mo=True, jnt=False, point=True, orient=True, scale=True)