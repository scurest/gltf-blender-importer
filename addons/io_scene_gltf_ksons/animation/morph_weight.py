import bpy
from . import quote
from .curve import Curve

# Morph Weight Animations


def add_morph_weight_animation(op, anim_info, node_id):
    anim_id = anim_info.anim_id
    sampler = anim_info.morph_weight[node_id]
    animation = op.gltf['animations'][anim_id]

    vnodes = find_mesh_instances(op.node_id_to_vnode[node_id])
    for vnode in vnodes:
        blender_object = vnode.blender_object

        if not blender_object.data.shape_keys:
            # Can happen if the mesh has only non-POSITION morph targets so we
            # didn't create a shape key
            return

        # Create action
        name = '%s@%s (Morph)' % (
            animation.get('name', 'animations[%d]' % anim_id),
            blender_object.name,
        )
        action = bpy.data.actions.new(name)
        action.id_root = 'KEY'
        anim_info.morph_actions[blender_object.name] = action

        # Find out the number of morph targets
        mesh_id = op.gltf['nodes'][node_id]['mesh']
        mesh = op.gltf['meshes'][mesh_id]
        num_targets = len(mesh['primitives'][0]['targets'])

        curve = Curve.for_sampler(op, sampler, num_targets=num_targets)
        data_paths = [
            ('key_blocks[%s].value' % quote('Morph %d' % i), 0)
            for i in range(0, num_targets)
        ]

        curve.make_fcurves(op, action, data_paths)


def find_mesh_instances(vnode):
    """
    A mesh instance at a vnode may be moved and split-up into multiple vnodes
    during vtree creation. Find all the places it ended up.
    """
    if vnode.mesh:
        return [vnode]
    else:
        vnodes = []
        for moved_to in vnode.mesh_moved_to:
            vnodes += find_mesh_instances(moved_to)
        return vnodes
