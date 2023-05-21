from maya import cmds
import importlib

import seAutoRig.scripts.project as project
import seAutoRig.ui as ui
importlib.reload(ui)
importlib.reload(project)

if __name__ == "__main__":
    workspace_control_name = ui.AutoRig.get_workspace_control_name()
    print(workspace_control_name)
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)

    auto_rig = ui.AutoRig()
    auto_rig.show()