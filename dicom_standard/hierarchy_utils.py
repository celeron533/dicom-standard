'''
Utility functions for managing the hierarchy structure of
attributes in the module-attribute relationship tables
'''
from typing import Dict, List, Tuple
import re

from bs4 import Tag

from dicom_standard import parse_lib as pl


def get_hierarchy_markers(name: str) -> str:
    clean_name = name.strip().replace('\n', '')
    _, *split = re.split(r'^(>+)', clean_name)
    return '' if split == [] else split[0]


def get_hierarchy_level(name: str) -> int:
    return len(get_hierarchy_markers(name))


def clean_attribute_field(name: str) -> str:
    return re.sub(r'[>\s]', '', name).strip()


def record_hierarchy_for_module(table: Tag) -> Tag:
    last_id = [table['id']]
    current_level = -1
    for attr in table['attributes']:
        last_id, current_level = update_hierarchy_position(attr, last_id, current_level)
        format_attribute_fields(attr, last_id)
    return table


def update_hierarchy_position(attr: Dict[str, str], last_id: List[str], current_level: int) -> Tuple[List[str], int]:
    attr_id = pl.create_slug(clean_attribute_field(attr['tag']))
    attribute_level = get_hierarchy_level(attr['name'])
    delta_l = attribute_level - current_level
    if attr_id == 'none':
        print(attr)
        raise Exception('this shouldn\'t happen')
    if delta_l > 1:
        # Used for a now-fixed standard workaround; keeping in case of future
        # typo where more than one hierarchy marker is used
        delta_l = 1
    if delta_l == 0:
        last_id[-1] = attr_id
    elif delta_l == 1:
        last_id.append(attr_id)
        current_level += 1
    elif delta_l < 0:
        last_id = last_id[:(delta_l)]
        last_id[-1] = attr_id
        current_level += (delta_l)
    return last_id, current_level


def format_attribute_fields(attr: Dict[str, str], last_id: List[str]) -> None:
    attr['name'] = clean_attribute_field(attr['name'])
    attr['tag'] = clean_attribute_field(attr['tag'])
    attr['type'] = clean_attribute_field(attr['type'])
    attr['id'] = ':'.join(last_id)
