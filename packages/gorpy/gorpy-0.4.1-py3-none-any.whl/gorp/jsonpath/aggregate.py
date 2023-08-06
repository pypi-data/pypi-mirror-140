'''Implements functions for aggregating iterables in JSON at varying levels
of granularity.'''
import math_eval
from math_eval import compute, IntRange, ComputeError, has_pattern, ufunctions, binops, safe_ufunctions, safe_binops
from gorp.utils import is_iterable
from gorp.gprint import bad_json, gprint, compressed_obj_repr

function = type(is_iterable)

class JsonPathError(Exception): pass


def group_by_path(path_vals, agg_level = slice(0), chain = True):
    '''Groups values by selected elements of the paths to those values.
path_vals: a dict mapping tuples (paths through a nested iterable to the 
children at the termini of those paths.

agg_level: int or slice, default slice(0). paths are grouped by whatever
    index or slice of indices of each path is exposed by path[agg_level].
    By default, aggregate everything regardless of path.

chain: bool, default True. If True, and the values associated with a given
    path are iterables, the iterables are blended into a single iterable
    (as by itertools.chain) rather than kept as separate iterables.

EXAMPLES:
__________
>>> path_vals = {(0, 'a'): 1, (0, 'b'): 2, (0, 'c'): 3, (1, 'd'): 4, (2, 'e'): 5}
>>> group_by_path(path_vals, 1) # group by the second element
{('a',): [1], ('b',): [2], ('c',): [3], ('d',): [4], ('e',): [5]}
>>> group_by_path(path_vals) # groups everything together regardless of path
{(): [1, 2, 3, 4, 5]}
>>> paths2 = {(5, 'z'): [1, 2], (5, 'a'): [3], (1, 'd'): [4], (2, 'e'): [5], (2, 'f'): 6}
>>> group_by_path(paths2, 0)
{(5,): [1, 2, 3], (1,): [4], (2,): [5, 6]}
>>> group_by_path(paths2, 0, chain = False)
{(5,): [[1, 2], [3]], (1,): [[4]], (2,): [[5], 6]}
    '''
    if isinstance(agg_level, int):
        agg_level = slice(agg_level, agg_level+1) 
        # this may be better than allowing integers because it assures that
        # the keys of the output of this function will always be tuples.
    out = {}
    for path, elt in path_vals.items():
        partial = path[agg_level]
        out.setdefault(partial, [])
        if chain:
            if is_iterable(elt):
                out[partial].extend(elt)
            else:
                out[partial].append(elt)
        else:
            out[partial].append(elt)
    return out

    
def agg_by_path(path_vals, agg_func, agg_level = slice(0), chain = True):
    '''Groups values by selected elements of the paths to those values,
and then applies an aggregate function to the values in each group.

path_vals, agg_level, chain: See the same arguments for group_by_path.

agg_func: a function that takes a single iterable as argument and returns a
number (e.g., sum, len).

EXAMPLES:
__________
>>> path_vals = {(0, 'a'): 1, (0, 'b'): 2, (0, 'c'): 3, (1, 'd'): 4, (2, 'e'): 5}
>>> agg_by_path(path_vals, sum, 0) # group by first element, then get the sum for each group
{(0,): 6, (1,): 4, (2,): 5}
>>> agg_by_path(path_vals, len, slice(0)) # get total count of everything
{(): 5}
>>> ragged_paths = {(0,):1, (0, 1, 2): 2, (0, 2, 3): 3, (1, 1): 4}
>>> agg_by_path(ragged_paths, sum, 1) # the (): 1 means that there is a path with no second element. It would probably be better to raise a ValueError in this case.
{(): 1, (1,): 6, (2,): 3}
>>> agg_by_path(ragged_paths, sum, slice(2))
{(0,): 1, (0, 1): 2, (0, 2): 3, (1, 1): 4}
    '''
    return {path: agg_func(vals) for path,vals in \
        group_by_path(path_vals, agg_level, chain).items()}
        
def avg(x): return sum(x)/len(x)

agg_funcs = {
    'sum': sum,
    'len': len,
    'count': len,
    'mean': avg,
    'avg': avg,
    'max': max,
    'min': min,
}


class Aggregator:
    '''Used by jsonpath.JsonPath and jsonpath.json_extract for aggregating the
values in JSON at different levels of coarseness.
See the documentation for Aggregator.aggregate for an understanding of how this
class works.

Initialization arguments:
func: a function that takes a single iterable as argument and returns a
number (e.g., sum, len).
    * func can also be a string representing such a function.
    * See agg_funcs for a list of such functions, currently 'sum', 'len', and
    'mean'. 'avg' is an alias for 'mean' and 'count' is an alias for 'len'.

agg_level: optional int or slice, default slice(0).
This controls the level granularity of aggregation by this aggregator.
The default is to aggregate everything together, regardless of path.
You could also choose and agg_level of slice(2), to group by the first two
elements in the path, or by 0, to group by only the first element in the
path.
    '''
    def __init__(self, func, agg_level = slice(0)):
        self.agg_level = agg_level
        if isinstance(self.agg_level, IntRange):
            self.agg_level = self.agg_level.slice
        if isinstance(func, str):
            if func.lower().strip() in agg_funcs: 
                self.func = agg_funcs[func.lower().strip()]
            else:
                # try using math_eval.compute to find the function;
                # func may be something like "sum(x[`hits`])/sum(x[`atbats`])"
                self.func = compute(func)
        else:
            self.func = func
    def aggregate(self, path_vals, agg_level = None, chain = True):
        if agg_level is None:
            agg_level = self.agg_level
        return agg_by_path(path_vals, self.func, agg_level, chain)
   
    agg_doc_lines = agg_by_path.__doc__.split('\n')
    aggregate.__doc__ = '\n'.join(agg_doc_lines[:4] + agg_doc_lines[7:])
    
    __call__ = aggregate
    
    def __str__(self):
        if "compute.<locals>.outfunc" in repr(self.func):
            funcrepr = self.func.__doc__.split('\n')[0]
        else:
            funcrepr = self.func.__name__
        return f"Aggregator(func = {funcrepr}, agg_level = {self.agg_level})"
    __repr__ = __str__