""" Skin Weights - Sergio Efigenio - 05/02/2023"""
import json
import maya.api.OpenMaya as om
import maya.cmds as cmds

from ..project import assets_path


class SkinWeights(object):
    def __init__(self, moduleName=None):
        self.moduleName = moduleName
        self.path = '%s%s/weights/' % (assets_path, self.moduleName)

        self.bindJoints = []
        self.mesh = []

        for i in cmds.ls('{}_model_grp'.format(self.moduleName), dag=True, type='mesh'):
            self.mesh.append(i[:-5])

        for jnt in ['C_head_FK_CTL', 'C_neck_01_FK_CTL', 'C_neck_02_FK_CTL', 'L_clavicle', 'R_clavicle']:
            self.bindJoints.append(jnt)
        for i in range(5):
            self.bindJoints.append('C_Spine0{}'.format(i))
        for side in 'LR':
            for part in ['Upper', 'Lower']:
                for limb in ['Leg', 'Arm']:
                    for i in range(6):
                        self.bindJoints.append('{}_{}{}_Twist_0{}'.format(side, part, limb, i))

        for side in 'LR':
            for limb in ['Leg', 'Arm']:
                if limb == 'Leg':
                    self.bindJoints.append('{}_ankle'.format(side))
                    self.bindJoints.append('{}_ball'.format(side))
                else:
                    self.bindJoints.append('{}_wrist'.format(side))

            for jnt in ['pinky', 'ring', 'middle', 'index', 'thumb']:
                for i in range(4):
                    self.bindJoints.append('{}_{}_0{}_FK_CTL'.format(side, jnt, i))

    def checkSkin(self):
        for mesh in self.mesh:
            file_path = self.path + mesh + '.json'
            self.applySkin(mesh)
            print('Skinned: ' + mesh)

            # if os.path.isfile(file_path):
            #     self.import_skin_weights(file_path)
            # else:
            #     self.export_skin_weights([mesh], self.bindJoints, file_path)

    def applySkin(self, mesh):
        skin_cluster_name = mesh + '_skinCluster'
        cmds.skinCluster(self.bindJoints, mesh, n=skin_cluster_name, tsb=True, sm=10, bm=0)

    # Define a function to get skin cluster from a mesh
    def get_skin_cluster(self, mesh):
        # Get the history of the mesh
        history = cmds.listHistory(mesh)
        # Find the skin cluster node in the history
        skin_cluster = None
        for node in history:
            if cmds.nodeType(node) == "skinCluster":
                skin_cluster = node
                break
            # Return the skin cluster node or None if not found
        return skin_cluster

    # Define a function to export skin weights to a json file
    def export_skin_weights(self, meshes, joints, file_path):
        # Create an empty dictionary to store the data
        data = {}
        # Loop through each mesh
        for mesh in meshes:
            # Get the skin cluster of the mesh
            skin_cluster = self.get_skin_cluster(mesh)
            # Check if the mesh has a valid skin cluster
            if not skin_cluster:
                print("No skin cluster found for {}".format(mesh))
                continue
            # Get the dag path of the mesh using OpenMaya API 2.0
            sel_list = om.MSelectionList()
            sel_list.add(mesh)
            dag_path = sel_list.getDagPath(0)
            # Get the MFnMesh function set of the mesh using OpenMaya API 2.0
            fn_mesh = om.MFnMesh(dag_path)
            # Get the number of vertices of the mesh
            num_verts = fn_mesh.numVertices

            # Create an empty list to store the weights for each vertex
            weights_list = []

            # Loop through each vertex
            for i in range(num_verts):
                # Create an empty dictionary to store the weights for each joint
                weights_dict = {}

                # Loop through each joint
                for joint in joints:
                    # Get the weight value of the joint for this vertex using Maya commands
                    weight_value = cmds.skinPercent(skin_cluster, "{}.vtx[{}]".format(mesh, i), query=True,
                                                    transform=joint)
                    # Store the weight value in the dictionary with joint name as key
                    weights_dict[joint] = weight_value

                # Append this dictionary to the list
                weights_list.append(weights_dict)

            # Store this list in another dictionary with mesh name as key
            data[mesh] = weights_list

        # Write this dictionary to a json file using Python's built-in json module
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    # Define a function to import skin weights from a json file
    def import_skin_weights(self, file_path):
        # Read data from json file using Python's built-in json module
        with open(file_path) as f:
            data = json.load(f)

            # Loop through each key-value pair in data (mesh name and weights list)
        for mesh, weights_list in data.items():

            # Check if this mesh exists in scene
            if not cmds.objExists(mesh):
                print("Mesh {} does not exist".format(mesh))
                continue

            # Get the skin cluster of the mesh
            skin_cluster = self.get_skin_cluster(mesh)
            # Check if the mesh has a valid skin cluster
            if not skin_cluster:
                print("No skin cluster found for {}".format(mesh))
                continue

            # Get number of vertices on this mesh
            num_verts = len(weights_list)

            # Loop through each vertex index
            for i in range(num_verts):

                # Get weight values for this vertex (dictionary with joint names and values)
                weights_dict = weights_list[i]

                # Loop through each key-value pair (joint name and value)
                for joint, value in weights_dict.items():
                    # Set weight value on corresponding joint using Maya commands
                    cmds.skinPercent(skin_cluster, "{}.vtx[{}]".format(mesh, i), transformValue=[(joint, value)])

    # def exportSkin(self, mesh, file_path):
    #     skin_cluster = cmds.listConnections(mesh + 'Shape', type="skinCluster")[0]
    #     vertex_num = cmds.polyEvaluate(mesh, vertex=True)
    #     skinning_data = {mesh: {}}
    #     for joint in self.bindJoints:
    #         for vertex in range(vertex_num):
    #             vertex_value = []
    #             vertex_value.append(cmds.getAttr(
    #                 '{0}.weightList[{1}].weights[0:{2}]'.format(skin_cluster, vertex, len(self.bindJoints))))
    #             vertex_ids = cmds.getAttr(mesh + '.vrts', multiIndices=True)
    #             skinning_data[str(mesh)][joint] = dict(zip(vertex_ids, vertex_value[0]))
    #
    #     with open(file_path, 'w') as f:
    #         json.dump(skinning_data, f)
    #     print("Skinning information exported to:", file_path)
    #
    # def importSkin(self, mesh, file_path):
    #     skin_cluster = cmds.listConnections(mesh + 'Shape', type="skinCluster")[0]
    #     vertex_num = cmds.polyEvaluate(mesh, vertex=True)
    #     print(vertex_num)
    #
    #     with open(file_path, 'r') as f:
    #         skinning_data = json.load(f)
    #
    #     for jnt in self.bindJoints:
    #         for vertex in range(vertex_num):
    #             weight = skinning_data[str(mesh)][str(jnt)][str(vertex)]
    #             print(weight)
    #             cmds.skinPercent(skin_cluster, '{}.vtx[{}]'.format(mesh, vertex), transformValue=[(jnt, weight)])
    #
    # import json
    # import maya.OpenMaya as om
    # import maya.OpenMayaAnim as oma
    #
    #
    #
    # meshes = [om.MFnMesh(m) for m in om.MSelectionList().getDagPath(i) for i in
    #           range(om.MGlobal.getActiveSelectionList().length())]
    #
    # joints = [om.MFnTransform(j) for j in om.MSelectionList().getDagPath(i) for i in
    #           range(om.MGlobal.getActiveSelectionList().length()) if
    #           om.MFnDependencyNode(om.MFnDagNode(j).child(0)).type() == om.MFn.kSkinClusterFilter]
    #
    # path = 'skin_weights.json'
    #
    # export_skin_weights(meshes, joints, path)
    #
    # def export_skin_weights(self, meshes, joints, path):
    #     skin_data = {}
    #     for mesh in meshes:
    #         mesh_data = {}
    #         for joint in joints:
    #             skin_cluster_name = om.MFnDependencyNode(joint).name() + 'Shape'
    #             skin_cluster_obj = om.MFnDependencyNode(om.MFnDagNode(skin_cluster_name).child(0)).object()
    #             skin_cluster = oma.MFnSkinCluster(skin_cluster_obj)
    #             weights = []
    #             vertex_it = om.MItMeshVertex(mesh)
    #             while not vertex_it.isDone():
    #                 weight_value = om.MDoubleArray()
    #                 influence_indices = om.MIntArray()
    #                 skin_cluster.getWeights(mesh, vertex_it.currentItem(), influence_indices, weight_value)
    #                 joint_index = -1
    #                 for i in range(influence_indices.length()):
    #                     if skin_cluster.getWeights(mesh, vertex_it.currentItem(), i) == 0.0:
    #                         continue
    #                     if om.MFnDependencyNode(skin_cluster.influenceObjects()[i]).name() == joint.name():
    #                         joint_index = i
    #                         break
    #                 if joint_index >= 0:
    #                     weights.append(weight_value[joint_index])
    #                 else:
    #                     weights.append(0.0)
    #                 vertex_it.next()
    #             mesh_data[joint.name()] = weights
    #         skin_data[mesh.name()] = mesh_data
    #     with open(path, 'w') as f:
    #         json.dump(skin_data, f)
    #
    # def import_skin_weights(self, meshes, joints, path):
    #     with open(path, 'r') as f:
    #         skin_data = json.load(f)
    #
    #     for mesh in meshes:
    #         mesh_data = skin_data.get(mesh.name(), {})
    #
    #         for joint in joints:
    #             weights = mesh_data.get(joint.name(), [])
    #             if not weights:
    #                 continue
    #
    #             skin_cluster_name = om.MFnDependencyNode(joint).name() + 'Shape'
    #             skin_cluster_obj = om.MFnDependencyNode(om.MFnDagNode(skin_cluster_name).child(0)).object()
    #             skin_cluster = oma.MFnSkinCluster(skin_cluster_obj)
    #
    #             vertex_it = om.MItMeshVertex(mesh)
    #             while not vertex_it.isDone():
    #                 skin_cluster.setWeights(mesh, vertex_it.currentItem(), [weights[vertex_it.index()]], False)
    #                 vertex_it.next()
