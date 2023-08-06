__version__ = "0.1.2"
__author__ = "ilonachan"

import yaml
import logging
import os
import re

log = logging.getLogger(__name__)


class PathChainer:
    def __init__(self, parent, name=None, attr_access=False):
        self.__dict__['_name'] = name
        self.__dict__['_parent'] = parent
        self.__dict__['_attr_access'] = attr_access

    def __repr__(self):
        _, joined = self.__follow_path__(*self.__trace_path__())
        return f"PathChainer {joined}"

    def __getattr__(self, name):
        return PathChainer(self, name, attr_access=True)

    def __setattr__(self, key, value):
        root, path_components = PathChainer(self, key, attr_access=True).__trace_path__()

        cursor, _ = self.__follow_path__(root, path_components, create_if_missing=True)

        name, _ = path_components[-1]
        cursor[name] = value
        return

    def __getitem__(self, name):
        return PathChainer(self, name)

    def __setitem__(self, key, value):
        root, path_components = PathChainer(self, key, attr_access=False).__trace_path__()

        cursor, _ = self.__follow_path__(root, path_components, create_if_missing=True)

        name, _ = path_components[-1]
        cursor[name] = value
        return

    def __call__(self, *args, **kwargs):
        root, path_components = self.__trace_path__()

        try:
            cursor, joined = self.__follow_path__(root, path_components)
            if cursor == None:
                return root._parent

            name, attr_access = path_components[-1]

            if name not in cursor:
                raise KeyError(joined)
            return cursor[name]
        except KeyError:
            if 'default' in kwargs:
                return kwargs['default']
            if len(args) > 0:
                return args[0]
            raise

    def exists(self):
        try:
            self()
            return True
        except KeyError:
            return False

    def __trace_path__(self):
        newpath = []
        current = self
        while isinstance(current._parent, PathChainer):
            newpath.insert(0, (current._name, current._attr_access))
            current = current._parent
        return current, newpath

    @staticmethod
    def __follow_path__(root, path_components, create_if_missing=False):
        joined = root._name
        cursor = root._parent
        for name, attr_access in path_components[:-1]:
            joined += f'.{name}' if attr_access else f'[\'{name}\']'
            if name not in cursor:
                if create_if_missing:
                    cursor[name] = {}
                else:
                    raise KeyError(joined)
            cursor = cursor[name]
            if type(cursor) not in [dict, list]:
                raise TypeError(f'{joined}: not a dict or list')
        if len(path_components) > 0:
            name, attr_access = path_components[-1]
            joined += f'.{name}' if attr_access else f'[\'{name}\']'
            return cursor, joined
        return None, joined


cfg = PathChainer({}, 'cfg')


def merge_dicts(base, new):
    result = {**base}
    for key in new:
        if type(new[key]) == dict and key in base and type(base[key]) == dict:
            result[key] = merge_dicts(base[key], new[key])
        else:
            result[key] = new[key]
    return result


def from_dict(content):
    cfg.__dict__['_parent'] = merge_dicts(cfg._parent, content)


def map2dict(mapping, source):
    result = {}
    for key in mapping:
        if type(mapping[key]) is str and mapping[key] in source:
            result[key] = source[mapping[key]]
        if type(mapping[key]) is dict:
            result[key] = map2dict(mapping[key], source=source)
    return result


def from_env_mapping(mapping, source=os.environ):
    from_dict(map2dict(mapping, source=source))


def apply_prefix(file_content: dict, prefix: str) -> dict:
    if prefix is None or len(prefix) == 0:
        return file_content
    if '.' not in prefix:
        nextstep = prefix
        prefix = ""
    else:
        prefix, nextstep = prefix.rsplit('.', 1)
    if len(nextstep) == 0:
        log.warning(f"skipping double dot in prefix")
        return apply_prefix(file_content, prefix)
    return apply_prefix({nextstep: file_content}, prefix)


def from_file(path: str, type: str = None, prefix: str = None):
    if type is None:
        type = os.path.splitext(path)[1][1:]
    try:
        match type:
            case 'yaml':
                with open(path, 'r') as lf:
                    file_content = yaml.safe_load(lf.read())
            case _:
                log.info(f'file type "{type}" not implemented: skipping "{path}"')
                return

        if file_content is None or not isinstance(file_content, dict):
            log.info(f'{path}: skipping empty configuration')
            return

        from_dict(apply_prefix(file_content, prefix))
    except Exception:
        log.error(f'Failed to read "{path}" as a config file of type "{type}"')
        raise


# noinspection PyShadowingBuiltins
def from_path(path: str, filter: str = None, type: str = None,
              recursive: bool | int = False, prefix: str = None,
              dir_prefix: bool = False, file_prefix: bool = False, begin_prefix: bool = False) -> None:
    """
    Loads configuration from a provided file or from files in a provided directory.

    :param path: the path of the file/directory
    :param filter: regex pattern to match the file names against
    :param type: force the parser to read the files as a specific file types (for nonstandard extensions)
    :param recursive: if `True`, subdirectories will be explored as well. A number will limit recursion depth
    :param prefix: providing a python-like dotpath will place read configuration below that path in the config
    :param dir_prefix: if `True`, entering a subdirectory will append that directory's name to the `prefix`.
                       This will reflect directory structures in the config
    :param file_prefix: if `True`, appends any found file's name to the `prefix`.
                       This will reflect file separation in the config
    :param begin_prefix: if `False`, the initial file/directory's name will not be added to the `prefix`.
                       This is the default, assuming that the user has picked a specific file or neutral directory
                       and wants more control over the prefix. But since this is needed as internal state anyway,
                       might as well expose it for more dynamic use cases.
    """
    if os.path.isfile(path):
        log.info(f'Reading from file {path}')
        if begin_prefix and file_prefix:
            filename = os.path.splitext(os.path.split(path)[-1])[0]
            if prefix is None or len(prefix) == 0:
                prefix = filename
            else:
                prefix += f'.{filename}'
        from_file(path, type=type, prefix=prefix)
    if os.path.isdir(path) and (begin_prefix is False or
                                recursive is True or (isinstance(recursive, int) and recursive > 0)):
        log.info(f'Reading from directory {path}')
        if begin_prefix and dir_prefix:
            dirname = os.path.split(path)[-1]
            if prefix is None or len(prefix) == 0:
                prefix = dirname
            else:
                prefix += f'.{dirname}'
        for f in os.listdir(path):
            p = os.path.join(path, f)
            if filter and not re.match(filter, f):
                continue

            from_path(p, filter=filter, type=type, recursive=recursive - 1 if isinstance(recursive, int) else recursive,
                      prefix=prefix, dir_prefix=dir_prefix, file_prefix=file_prefix, begin_prefix=True)
