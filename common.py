#!/usr/bin/python3
import yaml


def load_yaml(yaml_file):
    return yaml.load(open(yaml_file, 'r'), yaml.SafeLoader)


def load_group(definition_file, group_name):
    definition = load_yaml(definition_file)
    if group_name not in definition:
        group = {}
    else:
        group = definition[group_name]
    return group


def load_boards(definition_file):
    return load_group(definition_file, "boards")


def load_types(definition_file):
    return load_group(definition_file, "types")