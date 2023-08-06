""" find class elements in runtime"""
import inspect


def get_pos_to_keyword_map(func):
    """ get the position of a keyword and return the mapping"""
    pos2kw = {}
    function_signature = inspect.signature(func)
    pos = 0
    for name, info in function_signature.items():
        if info.kind in info.POSITIONAL_OR_KEYWORD:
            pos2kw.update({pos: name})
        pos += 1
    return pos2kw


def get_keyword_to_default_map(func):
    """ get the keyword in the default mapping """
    kw2default = {}
    function_signatrue = inspect.signature(func)
    for name, info in function_signatrue.parameters.items():
        if info.kind is info.POSITIONAL_OR_KEYWORD:
            if info.default is not info.empty:
                kw2default.update({name: info.default})
    return kw2default
