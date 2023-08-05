'''Contains the JsonPath class and json_extract.
Those perform this package's actual work of searching JSON.
'''
from gorp.jsonpath.parser import *


def follow_abspath(json, abspath):
    '''json: an arbitrarily nested python object, where each layer 
    is a list, dict, or tuple.
abspath: a list of keys or array indices to be followed.
**Returns:** the child of json[abspath[0]][abspath[1]]...[abspath[-1]]'''
    out = json
    for elt in abspath:
        out = out[elt]
    return out


def json_find_matches(json,
                      graph,
                      filter_path, 
                      curpath = tuple(), 
                      get_full_path_also=False,
                      reverse_selectivity = False, 
                      recursive = False):
    '''See :func:`json_extract` for a description of how this works.
Recursively searches the nested iterable graph,
    using a pre-generated filter_path (which must be a list of filters and 
    not a query string).
Called by json_extract and other similar functions.
Returns a generator expression that yields the appropriate results.'''
    paths_to_action_filter = []
    new_filter_path = filter_path.copy()
    while isinstance(new_filter_path[0], str):
        if new_filter_path[0] == '..':
            recursive = True
            new_filter_path = new_filter_path[1:]
        if new_filter_path[0] == '!!':
            reverse_selectivity = not reverse_selectivity
            new_filter_path = new_filter_path[1:]
    
    current_filter = new_filter_path[0]
    if len(new_filter_path) == 1 \
        and len(current_filter) == 1 \
        and (current_filter[0].keys_in == [''] or (not current_filter[0].keys_in)) \
        and not current_filter[0].vals_in:
        # this is a filter with no specification for keys or values, which could
        # have been produced by terminating a parsed path with a path-separating 
        #pipe; just return the entire graph.
        if get_full_path_also:
            yield curpath, graph
        else:
            yield graph
        return
    satisfied = [False for elt in current_filter]
    paths_to_action_filter = []
    action = [filt.action for filt in current_filter if filt.action!='check'][0]
    if action[:2] == 'up':
        # "up" actions are of the form "up1", "up2", etc.
        if len(action) > 2:
            num_levels_up = int(action[2:])
        else:
            num_levels_up = 1 # if action is "up", assumed number is 1
        paths_to_action_filter = [curpath[:-num_levels_up]]
    elif action == 'stay':
        paths_to_action_filter = [curpath]
    
    for ii, filt in enumerate(current_filter):
        results = filt.filter(graph, reverse_selectivity)
        if results:
            satisfied[ii] = True
        if filt.action == 'down': # 'up' and 'stay' possibilites already covered
            paths_to_action_filter = set()
            for k in results:
                if isinstance(k, IntRange):
                    for k_ind in k.indices_from(graph):
                        paths_to_action_filter.add(curpath + (k_ind,))
                else:
                    paths_to_action_filter.add(curpath + (k,))
    
    if recursive:
        if type(graph)==dict:
            iterator = graph.items()
        else:
            iterator = enumerate(graph)
        for curnode, newgraph in iterator:
            if is_iterable(newgraph) and (curpath+(curnode,) not in paths_to_action_filter): 
                # we haven't matched all the filters yet, but we can descend
                # If we didn't match this node in the path, we don't
                # want to continue recursively searching this node's children
                # UNLESS we're in recursive mode.
                # i.e., if we have path = 
                # [[Filter(keys_in = '^a$')],[Filter(keys_in = (1,2)]], we want
                # paths like ['a',1,'b',3] or ['a',2], but not paths like
                # ['a', 3, 'b', 1].
                # If we're in recursive mode, paths like ['a',3,'b',1] are fine.
                yield from json_find_matches(json,
                        newgraph, 
                        new_filter_path, 
                        curpath + (curnode,),
                        get_full_path_also,
                        reverse_selectivity = reverse_selectivity,
                        recursive = recursive)
    if all(satisfied):
        # we matched all the filters on this layer, move forward in the path.
        for path_to_action_filter in sorted(paths_to_action_filter):
            nextgraph = follow_abspath(json, path_to_action_filter)
            if len(new_filter_path)==1:
                # print("Adding nextgraph: ", end = '')
                # gprint(nextgraph)
                if get_full_path_also:
                    yield (path_to_action_filter, nextgraph)
                else:
                    yield nextgraph
                continue
            elif is_iterable(nextgraph):
                # if we're in recursive mode, we already searched.
                # continue searching, this time for any paths that match
                # the rest of the path (not including the current node in the path,
                # which we already found).
                # print("(De/Asc)ending from path {} to path_to_action_filter {}".format(curpath, path_to_action_filter))
                yield from json_find_matches(json,
                        nextgraph, 
                        new_filter_path[1:], 
                        path_to_action_filter,
                        get_full_path_also,
                        reverse_selectivity = reverse_selectivity,
                        recursive = False) # Finding a match disables recursive mode
    return


def json_find_matches_dataframe(df, filter_path, reverse_selectivity = False):
    '''Iteratively filters a pandas.DataFrame df using the same sort of 
    filter_path used by json_extract.
Because of the tabular nature of pandas DataFrames, filters are treated as 
    being either 'down' or 'check'; a filter either refines both the rows and 
    columns returned (essentially a 'down' action) or refines only the rows 
    returned (essentially a 'check' action).'''
    import pandas as pd
    for layer in filter_path:
        if isinstance(layer, str):
            if layer == '!!':
                reverse_selectivity = not reverse_selectivity
            continue
        rows = pd.Series([True]*df.shape[0])
        for filt in layer:
            new_rows, new_cols = filt.filter_dataframe(df)
            rows &= new_rows
            if filt.action != 'check':
                cols = new_cols
            else:
                cols = df.columns
        df = df.loc[rows, cols]
    return df


def json_extract(filter_path, 
                 json,
                 get_full_path_also = False,
                 reverse_selectivity = False,
                 recursive = False,
                 fuzzy_keys = False,
                 sub_func = None,
                 ask_permission = True):
    '''*json*: an arbitrarily nested Python object, where each layer 
    is a tuple, list, dict, or subclass of dict.

*filter_path*: list of :class:`Filter` steps, or single string or number.
    The preferred form of filter_path is a query string that can be
    parsed into a list of Filter layers by parse_json_path.

*get_full_path_also*: bool, see "Returns".

*reverse_selectivity*: bool, see "Returns".

*recursive*: bool, see "Returns".

*fuzzy_keys*: If True, you can test keys with regular expressions and many 
kinds of mathematical tests.
The drawback of using fuzzy_keys is that arrays and dicts have to be searched
exhaustively in linear time, rather than just going straight to an exact 
index or key in constant time.
fuzzy_keys can be toggled by 'zz' in a filter_path query string.

*sub_func*: Function of one variable. 
If this is not None, after the JSON is extracted, the sub_func is applied to 
the terminal nodes by mutate_json.
You can also turn on "sub mode" in a query string by terminating the query 
string with "~~ss", followed by a string representing the sub_func
that can be parsed by math_eval.compute(). 

*ask_permission*: only relevant if sub_func is not None. When in "sub mode", if
ask_permission is True, create an interactive prompt.

**Returns:** a list of the children that can be found by paths matched by this 
function.

Notes on optional parameters:
    * If reverse_selectivity is True at a given filter layer, the matching
    changes as follows:
        * If fuzzy_keys is False, only the matching on values is reversed. 
        * If fuzzy_keys is True, the matching on both values and keys is 
        reversed.
    * If get_full_path_also is True, return instead a dict mapping 
    complete paths (tuples of keys and indices) to the children of those paths.
    * If recursive is True, we keep descending until we find a match, even if
    the match fails on the first level it's applied to.

**EXAMPLES**
___________

>>> bad_json = {'b': 3,
   '6': 7,
   'jub': {'uy': [1, 2, 3],
           'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}
>>> json_extract(json = bad_json,
    filter_path = '^\d+$') 
    # this is a regex match on keys; it doesn't work by default 
ALERT: It looks like you may have tried to match keys with regular expressions
['\\\\d'] while not in fuzzy_keys mode. Did you intend this?
[]
>>> json_extract(json = bad_json,
    filter_path = '^\d+$', fuzzy_keys=True) 
    # regexes on keys work with fuzzy_keys=True.
[7]
>>> json_extract(json = bad_json,
    filter_path = 'jub~~@yu~~uy') 
    # look for the children of key 'uy' that's a child of 
    # root-level 'jub', but only if 'jub' also has the child 'yu'.
    # This is non-fuzzy matching, but it works since 'jub', 'yu'
    # and 'uy' all match keys in json exactly.
[[1, 2, 3]]
>>> json_extract(json = bad_json,
    filter_path = '..~~@zz^[a-z]{2}$~~@zznn0') 
    # 'zz' toggles fuzzy_keys; the first use turned it on 
    # and the second turned it off
[1, 6]
>>> json_extract(json = bad_json,
    fuzzy_keys = True,
    filter_path = '[a-z]{2}~~@nn0') 
    # Matches 'jub', but then tries to find index 0 in graph['jub'] and can't
[]
>>> json_extract(json = bad_json,
    filter_path = '..~~@zz[5-8];;nn5:9', 
    get_full_path_also = True) 
    # recursively ('..') looks for keys with a substring in {'5','6','7','8'}
    # OR (';;') that have the numeric value in range(5,9) ('nn5:9')
{('jub', 'yu', 1, 'M8'): 9, ('6',): 7}
>>> json_extract(json = bad_json,
    filter_path = '[5-8];;nn5:9')
    # careful! you're trying to match an IntRange and a regex to keys when not 
    # fuzzy_keys. When fuzzy_keys = False, IntRanges only match array indices.
[]
>>> json_extract(json = bad_json,
    filter_path = '..~~@nnint(k)*2<4vvnnstr(v)>`8`', 
    get_full_path_also = True) 
    # If fuzzy_keys is False, we can't use functions like "int(k)*2 < 4"
    # to constrain keys. As a result, we get this error:
Traceback (most recent call last):
...
JsonPathError: When not in fuzzy_keys mode, only IntRange slicers and ints are allowed as key tests.
>>> small_json = [[1, 2, 3, 4, 5], {0: 'a', 1: 'b'},
        {2: 'c'}, [6, 7], {3: 'd'}]
>>> json_extract(json = small_json,
        filter_path = 'nn:3~~@..~~@ggnn1vvx[0]<x[1]', 
        get_full_path_also = True)
        # The 'gg' string before the third layer means that we create a 
        # GlobalConstraint that matches the key/index 1,
        # if itbl[0] < itbl[1].
{(0, 1): 2, (1, 1): 'b'}
>>> json_extract(json = small_json,  
        filter_path = 'nn:3~~@..~~@ggnn1:3vvnnx[0]<x[1]',
        get_full_path_also = True)
        # GlobalConstraints only match IntRanges to array indices.
        # IntRanges do not match numeric dict keys in a GlobalConstraint.
{(0, 1): 2, (0, 2): 3}
>>> json_extract(json = bad_json,
    filter_path = '..~~@zz(?i)^[M-Y]||vvnn1:10:2',
    get_full_path_also = True) 
    # The '||' means that at least one key-value pair must match the key
    # constraint OR the value constraint. It doesn't have to match both.
{('jub', 'uy'): [1, 2, 3],
 ('jub', 'yu'): [6, {'y': 'b', 'M8': 9, 1: (3, 0)}],
 ('6',): 7,
 ('b',): 3}
>>> json_extract(json = bad_json,
    filter_path = 'zz!!\d~~@!!yu',
    get_full_path_also = True) 
    # in this case, '!!' toggles reverse_selectivity on and then off again.
{('jub', 'yu'): [6, {'y': 'b', 'M8': 9, 1: (3, 0)}]}
>>> json_extract(json = bad_json,
    fuzzy_keys = True,
    filter_path = '..~~@(?i)[a-z]+\d~~^^', 
    get_full_path_also = True)
    # '~~^^' means "find the grandparents of the current container".
    # You could also get the parents with '~~^' or the great-grandparents 
    # with '~~^^^', and so on.
{('jub',): {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3, 0)}]}}
>>> json_extract(json = {'a':17, 'b':2, 'c': 4, 'd': 31}, 
    filter_path = 'zz^[a-z]vvnnx>3&&str(x)<`3`', 
    get_full_path_also=True)
    # Each value must satisfy BOTH constraints separated by the '&&'.
    # So the key has to start with a lowercase ASCII letter,
    # and the value has to have a numeric value greater than 3 ("x>3") AND
    # a string value less than '3' ("str(x)<`3`).
{('a',): 17}
>>> json_extract(json = {'b': 3,  'g6': 2,  '6': 7},
    filter_path = "ggvvnnstr(x[`b`]) =~ `^\d`~~zz\dvvnnx<4")
    # The "=~" operator allows regex matching within a compute expression.
[2]
>>> baseball = {'foo': 
...    {'alice': {'hits': [3, 4, 2, 5], 'at-bats': [4, 3, 3, 6]},
...     'bob': {'hits': [-2, 0, 4, 6], 'at-bats': [1, 3, 5, 6]}},
... 'bar': 
...    {'carol': {'hits': [7, 3, 0, 5], 'at-bats': [8, 4, 6, 6]},
...     'dave': {'hits': [1, 0, 4, 10], 'at-bats': [1, 3, 6, 11]}}}
>>> json_extract(json = baseball, 
...              filter_path = "zz~~@~~@.*AGGsumBY0",
...              # get the sum of everything, grouped by the first level
...              # of organization (in this case the team)
...              get_full_path_also = True)
{('bar',): 75, ('foo',): 53}
>>> json_extract(json = baseball, 
...              filter_path = "zz~~@~~@.*AGGsumBY1:",
...              get_full_path_also = True)
{('carol', 'at-bats'): 24, ('carol', 'hits'): 15, ('dave', 'at-bats'): 21, ('dave', 'hits'): 15, ('alice', 'at-bats'): 16, ('alice', 'hits'): 14, ('bob', 'at-bats'): 15, ('bob', 'hits'): 8}
    '''
    if isinstance(filter_path, str):
        filter_path = parse_json_path(filter_path, fuzzy_keys = fuzzy_keys)
    elif not isinstance(filter_path, (tuple, list)):
        filter_path = [Filter(keys_in = filter_path)]
    if len(filter_path)==0:
        return []
    mutator = False
    aggregator = False
    if isinstance(filter_path[-1], Mutator):
        filter_path, mutator = filter_path[:-1], filter_path[-1]
    if isinstance(filter_path[-1], Aggregator):
        filter_path, aggregator = filter_path[:-1], filter_path[-1]
    # gprint(filter_path)
    
    if type(json).__name__ != 'DataFrame':
        if get_full_path_also or mutator or aggregator:
            # map paths to termini of those paths
            out =  dict(json_find_matches(json,
                                          json,
                                          filter_path = filter_path,
                                          get_full_path_also = True, 
                                          reverse_selectivity = reverse_selectivity, 
                                          recursive = recursive))
        else:
            # show only termini of good paths
            out =  list(json_find_matches(json,
                                          json,
                                          filter_path = filter_path,
                                          get_full_path_also = False, 
                                          reverse_selectivity = reverse_selectivity, 
                                          recursive = recursive))
        if mutator:
            mutator.mutate(json, out, ask_permission)
        elif aggregator:
            return aggregator.aggregate(out)
        else:
            return out
    else:
        df = json_find_matches_dataframe(json, filter_path, reverse_selectivity)
        if df.shape != (0, 0) and mutator:
            return mutator.replacement_func(df)
        return df



class JsonPath:
    '''Class for manipulating and traversing filter paths.

**Initialization args:**

*filters_or_query*: a list of layers of Filters and GlobalConstraints; or a 
query that can be parsed by parse_json_path and translated into such a list.

*json*: a nested Python object. This can be added later by add_json().

*fuzzy_keys*: See the documentation for the :class:`Filter` class and :func:`json_extract`.

**Attributes:**

*filters*: A list of layers of Filters and GlobalConstraints, along with '..' 
and '!!' flags.

*mutator*: The final item in the "filters" list passed in when initialized.
This is a Mutator object that mutates the JSON passed in to this func.

*curLayer*: Tracks what index of the filters the JsonPath will start 
traversing from. This can be manipulated with :func:`JsonPath.descend` to see how the 
resultset changes.

**Methods:**
    *'+'*: Two JsonPaths can be added together to concatenate their filters; 
    the JsonPath produced by (a+b) has a's JSON.
    You can also add a JsonPath to a list of filters, or vice versa.

    *copy()*: Returns a new JsonPath with no associated json.

    *descend()*: Allows examination of how each filter layer changes the 
    resultset.

    *extract()*: Like json_extract().

    *sub()*: Finds all the paths from extract(), then applies a function to 
    each child node found. This is an in-place transformation.

**Other notes:**

You can access slices and individual filter layers in a JsonPath with the 
[a:b] or [a] array-slicing notation.
    '''
    def __init__(self, 
                 filters_or_query,
                 json = None,
                 fuzzy_keys = False):
        self.json = json
        self.resultset = None
        self.mutator = None
        self.aggregator = None
        self.curLayer = 0
        self._initial_fuzzy_keys = fuzzy_keys # handy because fuzzy_keys can change
        self.fuzzy_keys = fuzzy_keys
        if isinstance(filters_or_query, str):
            self.query = filters_or_query
            self.filters = parse_json_path(filters_or_query, fuzzy_keys)
            for layer in self.filters:
                if isinstance(layer, list):
                    for filt in layer:
                        if hasattr(filt, 'fuzzy_keys'):
                            self.fuzzy_keys = filt.fuzzy_keys
        else:
            self.query = None
            self.filters = filters_or_query
        if isinstance(self.filters[-1], Mutator):
            self.filters, self.mutator = self.filters[:-1], self.filters[-1]
        elif isinstance(self.filters[-1], Aggregator):
            self.filters, self.aggregator = self.filters[:-1], self.filters[-1]
            
    def add_filters(self, filters_or_query):
        '''filters_or_query: a query parsed by parse_json_path that returns a list of
    filter layers, or a list of filter layers.
Adds new filters to the end of the this JsonPath's 'filters' attribute.'''
        if len(self.filters[-1]) == 1 \
        and (self.filters[-1][0].keys_in == [''] or (not self.filters[-1][0].keys_in)) \
        and not self.filters[-1][0].vals_in:
            # this is a filter with no specification for keys or values, which could
            # have been made by terminating a parsed path with a path-separating pipe
            self.filters.pop()
        if isinstance(filters_or_query, str):
            self.filters.extend(parse_json_path(filters_or_query, 
                                                fuzzy_keys = self.fuzzy_keys))
        else:
            self.filters.extend(filters_or_query)
            
    def __getitem__(self, slice_or_ind):
        return JsonPath(self.filters[slice_or_ind], self.json, self._initial_fuzzy_keys)
        
    def __setitem__(self, slice_or_ind, new_filters):
        if isinstance(new_filters, JsonPath):
            if isinstance(slice_or_ind, int):
                if slice_or_ind < 0:
                    slice_or_ind = len(self) + slice_or_ind
                # need to make sure that we don't put a filter layer inside of an
                # existing filter layer
                self.filters[slice_or_ind:slice_or_ind+1] = new_filters.filters
            else:
                self.filters[slice_or_ind] = new_filters.filters
        else:
            self.filters[slice_or_ind] = new_filters
            
    def __delitem__(self, slice_or_ind):
        del self.filters[slice_or_ind]
        
    def __add__(self, other_JsonPath):
        if isinstance(other_JsonPath, JsonPath):
            return JsonPath(self.filters + other_JsonPath.filters, 
                            self.json, 
                            self._initial_fuzzy_keys)
        elif isinstance(other_JsonPath, list):
            # add a list of filters to this JsonPath.
            return JsonPath(self.filters + other_JsonPath, 
                            self.json,
                            self._initial_fuzzy_keys)
        raise TypeError("Can only add lists of filters and other JsonPaths to JsonPaths.")
        
    def __radd__(self, other_JsonPath):
        if isinstance(other_JsonPath, JsonPath):
            # (a + b) keeps a's JSON; (b + a) keeps b's JSON. 
            return JsonPath(other_JsonPath.filters + self.filters, 
                            other_JsonPath.json,
                            other_JsonPath._initial_fuzzy_keys)
        elif isinstance(other_JsonPath, list):
            return JsonPath(other_JsonPath + self.filters, 
                            self.json,
                            self._initial_fuzzy_keys)
        raise TypeError("Can only add lists of filters and other JsonPaths to JsonPaths.")
            
    def copy(self):
        '''Return a new JsonPath with the same filters but no associated JSON.'''
        return JsonPath(self.filters.copy())
            
    def __str__(self):
        return "JsonPath(filters_or_query = {},\nfuzzy_keys = {},\njson = {})".format(gprint(self.filters, str), self.fuzzy_keys, compressed_obj_repr(self.json))
    __repr__ = __str__
    
    def __len__(self):
        return len(self.filters)
        
    def add_json(self, json):
        '''Set this JsonPath's 'json' attribute to json. Resets resultset and 
    curLayer.''' 
        self.curLayer = 0
        self.json = json
        self.resultset = None
    
    def follow_path(self, layers = None):
        '''See the documentation for JsonPath.descend().

This is mainly useful as a helper function for JsonPath.descend(), which is 
in turn a helper function for JsonPath.extract().

EXAMPLES:
________
>>> list(JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2}).follow_path(1))
    # only applies the first filter, which finds key 'a' and then descends
[(('a',), [1, 2, 3])]
>>> dict(JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2}).follow_path())
    # no path was specified, so it applies both filters and descends to json['a']
    # and then json['a'][1:]
{('a', 1): 2, ('a', 2): 3}
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> dict(jpath_ex.follow_path(1)) 
    # note that calling follow_path(1) increases its curLayer from 0 to 1
{('a',): [1, 2, 3]}
>>> dict(jpath_ex.follow_path(1)) 
    # now calling follow_path(1) increases its curLayer from 1 to 2,
    # but the first call didn't update the resultset so we get nothing.
    # use descend() to update the resultset.
{}
        '''
        if self.curLayer == len(self):
            raise StopIteration("Traversal of this JsonPath is complete.")
        if layers is None:
            path_continued = self.filters[self.curLayer:]
            self.curLayer = len(self)
        else:
            path_continued = []
            ii = 0
            # print({"ii":ii, "curLayer": self.curLayer, "filters[curLayer+ii]":self.filters[self.curLayer+ii], 'path_continued': path_continued})
            while ii < layers:
                path_continued.append(self.filters[self.curLayer+ii])
                if isinstance(self.filters[self.curLayer+ii], str):
                    # it's a '..' indicating the switch to recursive mode
                    # or a '!!' indicating the switch to "reverse_selectivity" mode.
                    layers += 1
                ii += 1
            self.curLayer += layers
        
        if self.resultset is not None:
            for curpath, subgraph in self.resultset.items():
                yield from json_find_matches(self.json,
                                        subgraph,
                                        path_continued, 
                                        curpath = curpath, 
                                        get_full_path_also=True)
        else:
            yield from json_find_matches(self.json,
                                        self.json,
                                        path_continued, 
                                        curpath = tuple(), 
                                        get_full_path_also=True)
        
    def descend(self, layers = None):
        '''layers: The number of layers of this JsonPath's filters to traverse.

If layers is None, just use all of the Filters and GlobalConstraints in this
JsonPath.

Returns None, but updates the JsonPath's resultset so that repeated calls to 
descend() followed by peeks at its resultset show you how its resultset 
evolves as the filters are successively applied.

Note that the traversal starts at self.curLayer, which may not be the first 
layer.

EXAMPLES:
________
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> jpath_ex.resultset
>>> jpath_ex.curLayer
0
>>> jpath_ex.descend(1) 
    # applies the filter(s) in layer 0, and descends to layer 1.
>>> jpath_ex.resultset
{('a',): [1, 2, 3]}
>>> jpath_ex.descend(1) # applies the filters in layer 1, which is the last layer
>>> jpath_ex.resultset
{('a', 1): 2, ('a', 2): 3}
        '''
        new_resultset = {}
        for newpath, newgraph in self.follow_path(layers):
            new_resultset[newpath] = newgraph
        self.resultset = new_resultset
        
    def extract(self, layers = None):
        '''With no arguments, this is equivalent to json_extract(self.json).
If layers is an int, it's equivalent to 
:func:`json_extract`(self.json, self.filters[:layers]),
unless one or more layers is '..' or '!!', because '..' and '!!' don't count
as their own filter layers.'''
        if re.search('DataFrame', str(type(self.json))):
            # the json is a DataFrame, which is extracted differently
            return json_find_matches_dataframe(self.json,
                                               self.filters[:layers])
        self.curLayer = 0
        self.descend(layers)
        self.curLayer = 0
        out = self.resultset
        self.resultset = None
        return out
        
    def sub(self, func = None, ask_permission = False, layers = None):
        '''Applies func to the terminal nodes of all the paths found by
    self.extract(layers).
    If func is None, uses this JsonPath's mutator to alter the JSON.
See the documentation for :func:`mutate_json` and :func:`JsonPath.extract`.
WARNING: This is an IN-PLACE transformation.
If you're concerned about making unintended changes, use ask_permission=True.

PERFORMANCE NOTE: If you intend to use the results from extract() and then 
use sub(), the below will save time by not calling extract() twice::
    
    >>> results = jp.extract() # jp is a JsonPath
    >>> mutate_json_repeatedly(jp.json, results.keys(), jp.mutator.replacement_func)

EXAMPLES:
________
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> jpath_ex.sub(lambda x: (x+1)*2, False)
>>> jpath_ex.json
{'a':[1,6,8], 'b':2}
>>> jpath_ex.sub(lambda x: (x+1)*2, True)
At path ('a', 1),
6
    would be replaced by
14.
Do you want to do this? (y/n) y
There are 1 nodes remaining that may be replaced. Do you still want to be asked permission? (y/n) y
At path ('a', 2),
8
    would be replaced by
18.
Do you want to do this? (y/n) n
Do you want to quit? (y/n) y
>>> JsonPath('b~~@nn1:', json = jpath_ex.json).sub(lambda x: x*3, False, 1)
    # note that we supplied layers = 1, so this will only traverse the first filter
    # layer before trying to make replacements.
>>> jpath_ex.json
{'a':[1, 14, 8], 'b':6}
>>> JsonPath('a~~@nn1:~~ss str(x)', 
...          json = jpath_ex.json).sub(ask_permission=False, layers = 2)
    # Here we are using the syntax of parse_json_path that allows us to add a Mutator
    # to a JsonPath by terminating the JsonPath string with "~~ss<func of 1 variable>"
>>> jpath_ex.json
{'a':[1, '14', '8'], 'b':6}
        '''
        if func is None:
            func = self.mutator.replacement_func
        if re.search('DataFrame', str(type(self.json))):
            # the json is a DataFrame, which is extracted differently
            results = self.extract(layers)
            rows, cols = list(results.index), list(results.columns)
            decision = 'y'
            replacement = func(self.json.loc[rows, cols])
            if ask_permission:
                print(self.json.loc[rows, cols])
                print("would be replaced by")
                print(replacement)
                decision = input("Is this OK? ")
            if decision == 'y':
                self.json.loc[rows, cols] = replacement
            return
        paths = list(self.extract(layers).keys())
        mutate_json_repeatedly(self.json, paths, func, ask_permission)
    
    def aggregate(self, func = None, agg_level = None):
        '''See documentation of jsonpath.aggregate.agg_by_path and
jsonpath.aggregate.Aggregator.

EXAMPLES:
___________
>>> path_vals = {(0, 'a'): 1, (0, 'b'): 2, (0, 'c'): 3, (1, 'd'): 4, (2, 'e'): 5}
>>> jp = JsonPath("nn:~~@zz[a-z]", json = path_vals)
>>> jp.aggregate(sum, 1)
{('a',): 1, ('b',): 2, ('c',): 3, ('d',): 4, ('e',): 5}
>>> jp.aggregator = Aggregator(sum, 0)
>>> jp.aggregate()
{(0,): 6, (1,): 4, (2,): 5}
        '''
        json = self.extract()
        if func is None:
            if self.aggregator:
                return self.aggregator.aggregate(json)
            raise TypeError("Expected a function as the first argument for JsonPath.aggregate.")
        if agg_level is None:
            agg_level = slice(0)
        return agg_by_path(json, func, agg_level)
