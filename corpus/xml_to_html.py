#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.
# coding=utf-8
"""Common functions for data processing."""

from anytree import AnyNode
# import episode_pb2


def any_tree_to_html(node, layer, clickable_label):
    """Turns an AnyTree representation of view hierarchy into HTML.
    Args:
    node: an AnyTree node.
    layer: which layer is the node in.

    Returns:
    results: output HTML.
    """
    results = ''
    if 'ImageView' in node.type:
        node_type = 'img'
    elif 'IconView' in node.type:
        node_type = 'img'
    elif 'Button' in node.type:
        node_type = 'button'
    elif 'Image' in node.type:
        node_type = 'img'
    elif 'MenuItemView' in node.type:
        node_type = 'button'
    elif 'EditText' in node.type:
        node_type = 'input'
    elif 'TextView' in node.type:
        node_type = 'p'
    else:
        node_type = 'div'

    if node.clickable == "true":
        clickable_label = "true"
    elif clickable_label == "true":
        node.clickable = "true"
    if node.text:
        node.text = node.text.replace('\n', '')
    if node.content_desc:
        node.content_desc = node.content_desc.replace('\n', '')

    #  or node.class_label == 'android.widget.EditText'
    if node.is_leaf and node.visible:
        html_close_tag = node_type
        if node.scrollable == "true":
            html_close_tag = node_type
            results = '<{}{}{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',
                ' package="{}"'.format(node.package)
                if node.package
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',
                ' description="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',
                ' scrollable="{}"'.format(node.scrollable) if node.scrollable else '',
                ' bounds="{}"'.format(node.bounds) if node.bounds else '',
                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )
        else:
            results = '<{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',
                ' package="{}"'.format(node.package)
                if node.package
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',

                ' description="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',

                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )

    else:
        if node.scrollable == "true":
            html_close_tag = node_type
            results = '<{}{}{}{}{}{}{}> {} </{}>\n'.format(
                node_type,
                ' id="{}"'.format(node.resource_id)
                if node.resource_id
                else '',

                ' class="{}"'.format(''.join(node.class_label))
                if node.class_label
                else '',

                ' descript  ion="{}"'.format(node.content_desc) if node.content_desc else '',
                ' clickable="{}"'.format(node.clickable) if node.clickable else '',
                ' scrollable="{}"'.format(node.scrollable) if node.scrollable else '',
                ' bounds="{}"'.format(node.bounds) if node.bounds else '',

                '{}'.format(node.text) if node.text else '',
                html_close_tag,
            )
        for child in node.children:
            results += any_tree_to_html(child, layer + 1, clickable_label)

    return results


# def parse_episode_proto(episode_proto_string):
#   """Parses an episode proto string.
#
#   Args:
#     episode_proto_string: the episode proto string.
#
#   Returns:
#     screen_html_list: html representation of the screen sequence in the episode.
#     node_list: AnyNode representation of the screen sequence in the episode.
#     id_to_leaf_id: mapping element indexes to leaf id. Used for grounding eval.
#   """
#   screen_html_list = []
#   screen_node_list = []
#   screen_id_map = []
#   screen_action_list = []
#   package_list = []
#   episode = episode_pb2.Episode()
#   episode.ParseFromString(episode_proto_string)
#
#   for t in episode.time_steps:
#     id_to_leaf_id = {}
#     objects = t.observation.objects
#     node_list = []
#     leaf_count = 0
#     for obj in objects:
#       package = obj.android_package
#       bbox = obj.bbox
#       dom = obj.dom_position
#
#       if '/' in obj.resource_id:
#         resource_id = obj.resource_id.split('/')[1].split('_')
#       else:
#         resource_id = obj.resource_id
#
#       if obj.is_leaf and obj.visible:
#         leaf_id = leaf_count
#         leaf_count += 1
#       else:
#         leaf_id = -1
#
#       a = AnyNode(
#           id=obj.index,
#           type=episode_pb2.ObjectType.Name(obj.type),
#           bbox=[bbox.left, bbox.top, bbox.right, bbox.bottom],
#           grid_location=episode_pb2.GridLocation.Name(obj.grid_location),
#           dom_position=[dom.depth, dom.pre_order_id, dom.post_order_id],
#           parent_id=obj.parent_index,
#           text=obj.text,
#           content_desc=obj.content_desc,
#           resource_id=resource_id,
#           selected=obj.selected,
#           clickable=obj.clickable,
#           visible=obj.visible,
#           enabled=obj.enabled,
#           is_leaf=obj.is_leaf,
#           leaf_id=leaf_id,
#           scrollable=obj.scrollable,
#           checkable=obj.checkable,
#           checked=obj.checked,
#           focusable=obj.focusable,
#           focused=obj.focused,
#       )
#       id_to_leaf_id[obj.index] = leaf_id
#       if a.parent_id != -1:
#         a.parent = node_list[a.parent_id]
#       node_list.append(a)
#     screen_action_list.append(id_to_leaf_id[t.action.object.index])
#     screen_html_list.append(any_tree_to_html(node_list[0], 0))
#     screen_node_list.append(node_list)
#     screen_id_map.append(id_to_leaf_id)
#     package_list.append(package)
#   return (
#       screen_html_list,
#       screen_node_list,
#       screen_action_list,
#       screen_id_map,
#       package_list,
#   )
#
# def build_proto_object(screen_info):
#     # 解析Appium XML格式的屏幕信息并存储在screen_info变量中
#
#     # 创建Episode Proto对象
#     episode = episode_pb2.Episode()
#
#     # 遍历屏幕信息节点
#     for node in screen_info:
#         # 创建TimeStep Proto对象
#         time_step = episode_pb2.TimeStep()
#
#         # 根据节点类型设置node_type
#         if '' in node.type:
#             node_type = 'img'
#         elif 'BUTTON' in node.type:
#             node_type = 'button'
#         elif 'EDITTEXT' in node.type:
#             node_type = 'input'
#         elif 'TEXTVIEW' in node.type:
#             node_type = 'p'
#         else:
#             node_type = 'div'
#
#         # 创建Element Proto对象
#         element = episode_pb2.Element()
#         element.node_type = node_type
#         element.node_text = node.text
#         element.node_id = node.id
#
#         # 将Element Proto对象添加到TimeStep Proto对象
#         time_step.elements.append(element)
#
#         # 将TimeStep Proto对象添加到Episode Proto对象
#         episode.time_steps.append(time_step)
#
#     # 将Episode Proto对象序列化为字符串
#     episode_proto_string = episode.SerializeToString()
