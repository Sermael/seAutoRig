from maya import cmds


def offset_grp(objects, sdk):
    for item in objects:
        # Create Offset Group
        offset = cmds.group(n='{}_{}'.format(item, sdk), empty=True)

        # Match Transforms and delete node
        pc = cmds.parentConstraint(item, offset, mo=False)
        cmds.delete(pc)

        # Find parent node
        up_node = cmds.listRelatives(item, p=True)
        # Parent to up node
        cmds.parent(item, offset)

        if up_node:
            cmds.parent(offset, up_node)
