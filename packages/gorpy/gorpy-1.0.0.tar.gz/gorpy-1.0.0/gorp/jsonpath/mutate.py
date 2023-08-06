from gorp.jsonpath.aggregate import *

def mutate_json(obj, path, func, ask_permission = False, **kwargs):
    '''Mutates a nested iterable object in-place by applying func to obj[path].

*obj*: an object containing arbitrarily nested iterables.

*path*: a tuple of keys or indices to follow through the object.

*func*: a function to apply to the child found at the end of the path, OR a 
non-function that everything should be replaced by, regardless of its value.

*ask_permission*: if True, ask before changing the node. Useful when this is 
called repeatedly by other functions.

**Returns:** None.'''
    level = kwargs.get('level', 0)
    if level == len(path):
        if not hasattr(func, '__call__'):
            out = func
        else:
            out = func(obj)
        if ask_permission:
            print("At path {p},\n{obj_short}\n    would be replaced by\n{out_short}.".format(p=path, obj_short=compressed_obj_repr(obj), out_short=compressed_obj_repr(out)))
            decision = input("Do you want to do this? (y/n) ")
            if decision == 'y':
                return out
            else:
                next_decision = input("Do you want to quit? (y/n) ")
                if next_decision == 'y':
                    raise JsonPathError("mutate_json halted at user request.")
                return obj
        return out
    obj[path[level]] = mutate_json(obj[path[level]], 
                                   path, 
                                   func, 
                                   ask_permission,
                                   level = level+1)
    if (level != 0):
        return obj


def mutate_json_repeatedly(obj, paths, func, ask_permission = False):
    '''See mutate_json. This applies the func to obj[path] for each path in paths.'''
    for ii, p in enumerate(paths):
        if not is_iterable(p):
            p = (p,)
        try:
            mutate_json(obj, p, func, ask_permission)
        except Exception as ex:
            if 'halted at user request' in repr(ex):
                return
            raise JsonPathError(ex)
        if ask_permission and ii < len(paths)-1:
            ask_permission = (input("There are {numpaths} nodes remaining that may be replaced. Do you still want to be asked permission? (y/n) ".format(numpaths= len(paths)-ii-1)) == 'y')


class Mutator:
    '''Intended as the last "layer" in a filter path. These are used by JsonPath
    objects' sub method and also by json_extract to mutate json at the paths 
    found by the other filters in the path.
If "fun" is the replacement_func of Mutator "mut", mut.mutate(json, paths) 
    will replace the values {v1, ..., vn} that are json's children of every 
    path in paths with {fun(v1), ..., fun(vn)}.'''
    def __init__(self, replacement_func):
        '''replacement_func: a function of one variable,
OR a string that math_eval.compute() can parse as a function of one variable.'''
        if isinstance(replacement_func, str):
            self.replacement_funcname = "compute({})".format(replacement_func)
            self.replacement_func = compute(replacement_func)
        else:
            self.replacement_funcname = replacement_func.__name__
            self.replacement_func = replacement_func
        
    def __repr__(self):
        return "Mutator(replacement_func = '{}')".format(self.replacement_funcname)
    __str__ = __repr__
        
    def mutate(self, json, paths, ask_permission = False):
        mutate_json_repeatedly(json, paths, self.replacement_func, ask_permission)