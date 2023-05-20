from maya import cmds
from .project import assets_path

guides_scene_path = '%s/%s/guides/%s_guides.mb'
default_guides_scene_path = '%s/default/guides/default_guides_001.mb'


class Guides(object):
    def __init__(self, characterName):
        self.characterName = characterName

    def import_guides(self):
        # --- Import guides
        guides_file = guides_scene_path % (assets_path, self.characterName, self.characterName)
        cmds.file(guides_file, i=1)

    def create_guides(self):
        # --- Import guides
        guides_file = default_guides_scene_path % assets_path
        cmds.file(guides_file, i=1)
        # --- Rename guides
        cmds.rename('default_Guides_GRP', '{}_Guides_GRP'.format(self.characterName))

    def save_guides(self):
        guides_file = guides_scene_path % (assets_path, self.characterName, self.characterName)
        cmds.select('{}_Guides_GRP'.format(self.characterName))
        cmds.file(guides_file, force=True, type='mayaBinary', es=True)
