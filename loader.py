from maya import cmds
import importlib
import seAutoRig
importlib.reload(seAutoRig)
import seAutoRig.ui as ui
importlib.reload(ui)

if __name__ == "__main__":
    print("Loader File Updated")
    workspace_control_name = ui.AutoRig.get_workspace_control_name()
    if cmds.window(workspace_control_name, exists=True):
        cmds.deleteUI(workspace_control_name)

    biped_rig2 = ui.AutoRig()
    biped_rig2.show()
