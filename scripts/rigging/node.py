""" Create node - Sergio Efigenio - 05/02/2023"""
from maya import cmds


class Node(object):
    def __init__(self):
        self.availableNodes = {
            'addDoubleLinear': 'ADL',
            'addMatrix': 'ADM',
            'aimConstraint': 'ACN',
            'angleBetween': 'ABT',
            'animBlend': 'ABL',
            'angular': 'ANG',
            'audio': 'AUD',
            'blendColors': 'BLC',
            'blendTwoAttr': 'BTA',
            'blendWeighted': 'BWG',
            'blendShape': 'BLS',
            'choice': 'CHO',
            'condition': 'CND',
            'curveParam': 'CRP',
            'curveInfo': 'CIN',
            'closestPointOnSurface': 'CPS',
            'closestPointOnCurve': 'CPC',
            'closestPointOnMesh': 'CPM',
            'composeMatrix': 'COM',
            'cluster': 'CLS',
            'clamp': 'CLM',
            'curveFromSurfaceIso': 'CFS',
            'decomposeMatrix': 'DCM',
            'detachCurve': 'DTC',
            'distanceBetween': 'DBT',
            'frameCache': 'FCC',
            'follicle': 'FLC',
            'fourByFourMatrix': 'FFM',
            'joint': 'JNT',
            'lattice': 'LTC',
            'loft': 'LFT',
            'module': 'M',
            'multiplyDivide': 'MLT',
            'multDoubleLinear': 'MDL',
            'multMatrix': 'MMT',
            'motionPath': 'MNP',
            'normalConstraint': 'NCN',
            'n_choice': 'NCH',
            'n_curveToCurve': 'NCC',
            'n_distanceRatio': 'NDR',
            'n_addDoubleAngle': 'ADA',
            'n_multDoubleAngle': 'MDA',
            'n_fingerCurl': 'NFC',
            'n_limbFkIkScale': 'NLS',
            'n_locator': 'NLC',
            'n_meshRivet': 'NMR',
            'n_multiRivet': 'NML',
            'n_nurbsRivet': 'NNR',
            'n_rockAndRoll': 'RNR',
            'n_smoothChoice': 'NSC',
            'n_softAngle': 'NSA',
            'n_softIk': 'NSI',
            'n_softVector': 'NSV',
            'n_spaceSwitch': 'NSS',
            'n_tentacle': 'TNT',
            'n_volumePreservation': 'NVP',
            'nearestPointOnCurve': 'NPC',
            'nurbsSurface': 'NRB',
            'nurbsCurve': 'NRC',
            'orientConstraint': 'OCN',
            'pairBlend': 'PBL',
            'particle': 'PRT',
            'pointMatrixMult': 'PMM',
            'pointConstraint': 'PCN',
            'pointEmitter': 'PEM',
            'pointOnCurveInfo': 'PCI',
            'pointOnSurfaceInfo': 'PSI',
            'parentConstraint': 'PAC',
            'plusMinusAverage': 'PMA',
            'poseReader': 'PRD',
            'ramp': 'RMP',
            'rebuildCurve': 'RCV',
            'remapValue': 'RMV',
            'reverse': 'RVS',
            'rotateHelper': 'RHP',
            'samplerInfo': 'SMP',
            'setRange': 'SRN',
            'skinCluster': 'SKN',
            'n_slerp': 'SLP',
            'tangentConstraint': 'TCN',
            'transform': 'TRN',
            'trigonometric': 'TRG',
            'tweak': 'TWK',
            'vectorProduct': 'VPR',
            'wrap': 'WRP',
            'wtAddMatrix': 'WAM'}

        self._constraintTypes = {'pointConstraint': 'PCN',
                                 'orientConstraint': 'OCN',
                                 'aimConstraint': 'ACN',
                                 'tangentConstraint': 'TCN',
                                 'scaleConstraint': 'SCN',
                                 'parentConstraint': 'PAC',
                                 'poleVectorConstraint': 'PVC',
                                 'geometryConstraint': 'GCN',
                                 'normalConstraint': 'NCN'}

        self.side = ["c", "C", "l", "L", "r", "R"]

        # the created nodes list, in case we need it later
        self.createdNodes = []

    def create(self, node="transform", side="C", description="node", skipSelect=True, parent=None):

        if node == "module":
            node_name = side.upper() + "_" + description + "_M"
            # create the node
            nd = cmds.createNode("transform", name=node_name, skipSelect=skipSelect, parent=parent)

        else:
            node_name = (side.upper() + "_" + description + "_" + self.availableNodes[node])
            # create the node
            nd = cmds.createNode(node, name=node_name, skipSelect=skipSelect)

        # add it to the createdNode list, in case we need to run LockAndHide or the like on it
        self.createdNodes.append(nd)

    def createdNode(self):
        return self.createdNodes
