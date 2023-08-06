'''Implements the Filter and GlobalConstraint classes, the two types of filters
used by json_extract and JsonPath to find paths through json.'''
from gorp.jsonpath.aggregate import * 
# includes math_eval imports, aggregation funcs


def _convert_to_filterfunc(x, fuzzy):
    '''Used by the Filter class to convert user-supplied arguments into functions that
    compare keys and values to those arguments. fuzzy is the fuzzy_keys 
    parameter of Filters.'''
    if not fuzzy and (not isinstance(x, (IntRange, int, str))):
        raise JsonPathError("When not in fuzzy_keys mode, only IntRange slicers and ints are allowed as key tests.")
    if isinstance(x, (list, tuple)):
        # a list or tuple within the keys_in/vals_in tuple; bundles conditions together.
        funclist = [_convert_to_filterfunc(elt, fuzzy) for elt in x]
        return lambda val: all(func(val) for func in funclist)
    elif isinstance(x, function):
        return x
    elif isinstance(x, (int, float, IntRange, complex)):
        return lambda val: val == x
    elif isinstance(x, str):
        if fuzzy: # x is a regex; the appropriate function tests if val contains that
                  # regex
            return lambda val: has_pattern(val, x)
        else: # x is a non-regex; the appropriate function tests equality with x
            return lambda val: val == x
    raise TypeError("Expected inputs to _convert_to_filterfunc to be list, tuple, function, number, IntRange, or string, got {}".format(type(x)))

def _filter_layer_repr(filter_layer):
    '''Functions returned by math_eval.compute() have docstrings that 
    indicate what the function does. 
This recursively searches the keys_in and vals_in attributes of Filter and 
    GlobalConstraint objects and make it so that the string representation
    of those compute() functions looks like "compute('x**2 + 3')" instead of
    '<function compute.<locals>.outfunc at 0x000002EEE5AAC160>'.'''
    out = []
    for k in filter_layer:
        if isinstance(k, list):
            out.append(_filter_layer_repr(k))
            continue
        try:
            if 'compute.<locals>.outfunc' in repr(k):
                doc = k.__doc__.split('\n')[0]
                out.append('compute("{}")'.format(doc))
            else:
                out.append(k)
        except:
            out.append(k)
    return out


class Filter:
    '''Used to check keys, array indices, and values in nested Python objects.
    Note that in this context "keys" means both dict keys and array indices.

**Arguments**:

*keys_in*: Function that performs a comparison, IntRange, number, string, or 
tuple that contains any number of nums, strings, comparison funcs, 
:class:`math_eval.IntRange`, or tuples.
If this is a tuple, a key that matches *anything* in the tuple is a match.
Any tuple within the tuple represents a set of conditions that are 
bundled and must be simultaneously satisfied.
If this is empty, all keys are matched.

*vals_in*: Same as keys_in, but tests values in a key-value pair.

*key_or_val*: Bool, default False. If true, any key-value pair where the key 
    matches keys_in OR vals_in is considered a match.

*action*: str: {'check', 'down', 'stay', 'up'+str(integer)} 
This determines how json_extract treats key-value pairs that are matched 
by this filter.
    * If the action is 'check', there must be another filter in the filter 
    layer. This filter only makes assertions.
    * If the action is 'down', json_extract will search downwards (to the
    children) of any keys that are matched by this filter.
    * If the action is 'stay', json_extract will return the container holding 
    the keys that match this filter.
    * If the action is 'up'+str(integer), json_extract will search the 
    integer^th ancestor (e.g., 1 = parent, 3 = great-grandparent) of the 
    key matched by this filter.

*fuzzy_keys*: bool. If False, IntRanges match array indices but not dict keys
and numbers and strings in keys_in must match keys and indices exactly.
If this is True, keys can be tested "fuzzily" by comparison functions and 
IntRanges, and all strings are treated as regular expressions.
Value testing is "fuzzy" regardless of the value of fuzzy_keys.

**Other attributes**:
    
*keyfuncs*: List of functions that perform key matching based on keys_in.
*valfuncs*: List of functions that perform value matching based on vals_in.

**Methods**:
    
*in*: The test "(k, v) in filt" will return True if the key-value 
pair k,v matches the filter "filt".

*callable*: "filt(k, v)" returns the same thing as "(k, v) in filt".
    '''
    def __init__(self, 
                 keys_in = tuple(), 
                 vals_in = tuple(), 
                 key_or_val = False,
                 action = 'down',
                 fuzzy_keys = False):
        if not is_iterable(keys_in) and not isinstance(keys_in, IntRange):
            self.keys_in = [keys_in]
        else:
            self.keys_in = keys_in
        
        if not is_iterable(vals_in) and not isinstance(vals_in, IntRange):
            self.vals_in = [vals_in]
        else:
            self.vals_in = vals_in
        
        self.keyfuncs = [_convert_to_filterfunc(k, fuzzy = fuzzy_keys) for k in self.keys_in]
        self.valfuncs = [_convert_to_filterfunc(v, True) for v in self.vals_in]
        self.key_or_val = key_or_val
        self.action = action
        self.fuzzy_keys = fuzzy_keys
    
    def filter(self, arr, reverse_selectivity = False):
        '''arr: a dict or array.
reverse_selectivity: If True, return only those key-value pairs that do NOT 
    satisfy the value filters of this Filter, and also NOT the key filters, 
    unless this Filter has fuzzy_keys = False, in which case the keys must 
    still be matched.
Returns a dict mapping the paths to all key-value pairs that satisfy this 
    Filter's keyfuncs and valfuncs (or keyfuncs OR valfuncs if self.key_or_val)
        '''
        out = {}
        if self.fuzzy_keys:
            if isinstance(arr, dict):
                iterator = arr.items()
            else:
                iterator = enumerate(arr)
            for k, v in iterator:
                if ((k, v) in self) ^ reverse_selectivity:
                    out[k] = v
        else: # non-fuzzy matching
            # reverse_selectivity cannot be implemented for non-fuzzy matching, because
            # reverse_selectivity would require linear-time exhaustive search of arr,
            # and that's not what fuzzy_keys is about.
            if isinstance(arr, dict):
                keys = arr
            else:
                keys = range(len(arr))
            if self.keys_in:
                keysin = self.keys_in
            else:
                if not self.valfuncs: 
                    # no keyfuncs or valfuncs; filtering will return the original itbl
                    if isinstance(arr, dict):
                        return arr
                    else:
                        # Other functions in this module need to work with dicts
                        # rather than arrays, so map e.g. [1, 2, 3] to {0:1, 1:2, 2:3}
                        return dict(enumerate(arr))
                keysin = keys
            for k in keysin:
                if isinstance(k, IntRange):
                    if isinstance(arr, dict):
                        continue
                        # IntRanges cannot be used to search for keys in dicts in 
                        # non-fuzzy mode, 
                        # because the IntRange could contain a huge number of 
                        # elements and that would make an exhaustive search prohibitive
                    else:
                        for ii in k.indices_from(arr):
                            if self.key_or_val:
                                out[ii] = arr[ii]
                            valmatch = len(self.vals_in) == 0
                            for valopt in self.valfuncs:
                                try:
                                    valmatch |= valopt(arr[ii])
                                except:
                                    pass
                            if valmatch ^ reverse_selectivity:
                                # TODO: maybe more intuitive for reverse_selectivity to
                                # be COMPLETELY disabled when fuzzy_keys is off than
                                # for it to reverse selectivity on values but not keys.
                                # I may decide to comment out the "^reverse_selectivity"
                                out[ii] = arr[ii]
                else:
                    if k in keys:
                        if self.key_or_val:
                            out[k] = arr[k]
                        valmatch = len(self.vals_in) == 0
                        for valopt in self.valfuncs:
                            try:
                                valmatch |= valopt(arr[k])
                            except:
                                pass
                        if valmatch ^ reverse_selectivity:
                            out[k] = arr[k]
        return out
    
    def filter_dataframe(self, df, reverse_selectivity = False):
        '''df: a pandas.DataFrame.
reverse_selectivity: Return all columns and rows that DON'T satisfy 
    constraints instead.
**Returns:** (
    boolean pandas.Series (True for each row satisfying vals_in constraints),
    list(names of columns satisfying keys_in constraints)
)'''
        import pandas as pd
        if self.valfuncs:
            rows = pd.Series([False]*df.shape[0])
        else:
            rows = pd.Series([True]*df.shape[0])
        if self.keyfuncs:
            cols = pd.Series([False]*df.shape[1])
            for keyfunc in self.keyfuncs:
                # each keyfunc applies an elementwise regex match to column names, or an
                # exact string match if not self.fuzzy_keys, returning a boolean array
                # of same length as columns
                new_cols = keyfunc(df.columns) ^ reverse_selectivity
                cols |= new_cols
                for col in df.columns[new_cols]:
                    for valfunc in self.valfuncs:
                        try:
                            new_rows = (valfunc(df[col]) ^ reverse_selectivity)
                            rows |= new_rows
                        except Exception as ex: 
                            # probably the valfunc was trying an invalid operation
                            # for that column's dtype 
                            pass
        else:
            cols = pd.Series([True]*df.shape[1])
            for col in df.columns:
                for valfunc in self.valfuncs:
                    try:
                        rows |= (valfunc(df[col]) ^ reverse_selectivity)
                    except:
                        pass
        return rows, list(df.columns[cols])
                
    
    def __contains__(self, key_val):
        k, v = key_val
        keymatch = len(self.keys_in) == 0
        valmatch = len(self.vals_in) == 0
        if not keymatch:
            for keyopt in self.keyfuncs:
                try:
                    keymatch |= keyopt(k)
                except:
                    pass
        if keymatch and self.key_or_val:
            return True
        if not valmatch:
            for valopt in self.valfuncs:
                try:
                    valmatch |= valopt(v)
                except:
                    pass
        if (self.key_or_val and valmatch) or (valmatch and keymatch):
            return True
        return False
    
    def __call__(self, key, val):
        return (key, val) in self
            
    def __repr__(self):
        keysin = _filter_layer_repr(self.keys_in)
        valsin = _filter_layer_repr(self.vals_in)
        return "Filter(keys_in = {}, vals_in = {}, key_or_val = {}, action = '{}', fuzzy_keys = {})".format(keysin, valsin, bool(self.key_or_val), self.action, bool(self.fuzzy_keys))
    __str__ = __repr__



class GlobalConstraint:
    '''Whereas the :class:`Filter` class checks individual key-value pairs in an array or
dict, the GlobalConstraint is for applying constraints to the whole iterable.

keys_in: a list/tuple of strings, numbers, or IntRanges.
    As with a Filter object with fuzzy_keys = False, each string/num in 
    keys_in must exactly match at least one key or index in the iterable; no 
    regular expressions!

vals_in: a list of functions that each take a single iterable as an argument. 
    These can be generated by the compute() function (which supports array 
    and dict slicing and indexing) or they can just be normal Python functions.
    Unlike the keyfuncs and valfuncs of a Filter object, constraints can 
    operate on multiple key-value pairs in a single iterable, like 
    "itbl['b']>=itbl['a']" or "sum(itbl)>0".

action: See the description of the "action" argument for Filter objects.
    '''
    def __init__(self, 
                 keys_in = tuple(),
                 vals_in = tuple(),
                 action = 'down'):
        if not is_iterable(keys_in):
            self.keys_in = [keys_in]
        else:
            self.keys_in = keys_in
        if not is_iterable(vals_in):
            self.vals_in = [vals_in]
        else:
            self.vals_in = vals_in
        for ii, val in enumerate(self.vals_in):
            if isinstance(val, str):
                # most likely due to val coming from a query string without an "nn"
                # after the "vv" delimiter.
                self.vals_in[ii] = compute(val)
        if any(hasattr(k, '__call__') for k in self.keys_in):
            raise JsonPathError("GlobalConstraint keys_in arguments cannot be functions. They should be things like numbers and other normal dict keys/array indices.")
        self.action = action
        
    def filter(self, itbl, reverse_selectivity = False):
        out = {}
        if self.satisfied_by(itbl) ^ reverse_selectivity:
            if not self.keys_in:
                if isinstance(itbl, dict):
                    out.update(itbl)
                else:
                    out.update(enumerate(itbl))
            for k in self.keys_in:
                if not isinstance(k, IntRange):
                    try:
                        out[k] = itbl[k]
                    except:
                        pass
                elif not isinstance(itbl, dict):
                    out[k] = itbl[k.slice]
        return out
    
    def filter_dataframe(self, df, reverse_selectivity = False):
        '''df: a pandas.DataFrame.
reverse_selectivity: Return all columns and rows that DON'T satisfy 
    constraints instead.
**Returns:** (
    boolean pandas.Series (True for each row satisfying vals_in constraints),
    list(names of columns in self.keys_in)
)'''
        import pandas as pd
        if self.keys_in:
            if reverse_selectivity:
                cols = [x for x in df.columns if x not in set(self.keys_in)]
            else:
                cols = self.keys_in.copy()
        else:
            cols = df.columns
        rows = pd.Series([False]*len(df))
        if self.vals_in:
            for valfunc in self.vals_in:
                rows |= (valfunc(df) ^ reverse_selectivity)
        return rows, cols
    
    def satisfied_by(self, itbl):
        '''itbl: any iterable (array, dict, pandas DataFrame) that this
    GlobalConstraint can filter.
**Returns:** bool, True if itbl satisfies all constraints, else False.'''
        out = True
        for constraint in self.vals_in:
            try:
                out &= constraint(itbl)
            except:
                return False
        return out
    
    def __str__(self):
        return "GlobalConstraint(keys_in = {k}, vals_in = {valsin}, action = '{a}')".format(k=self.keys_in, valsin = _filter_layer_repr(self.vals_in), a=self.action)
    __repr__ = __str__
