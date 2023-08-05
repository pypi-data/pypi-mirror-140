from gorp.jsonpath import *

def jsonpath_testdoc():
    '''
>>> bad_json = {'b': 3,'6': 7,
...     'jub': {'uy': [1, 2, 3],
...     'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}
>>> json_extract(json = bad_json,
...  filter_path = '^\d+$') # this is a regex match on keys; it doesn't work by default 
ALERT: It looks like you may have tried to match keys with regular expressions
['\\\\d'] while not in fuzzy_keys mode. Did you intend this?
[]
>>> json_extract(json = bad_json, filter_path = '^\d+$', fuzzy_keys=True) 
... # regexes on keys work with fuzzy_keys=True.
[7]
>>> json_extract(json = bad_json ,filter_path = 'jub~~@yu~~uy') 
[[1, 2, 3]]
>>> json_extract(json = {'b': 3,'6': 7, 'jub': {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}, filter_path = '..~~@zz^[a-z]{2}$~~@zznn0')
[1, 6]
>>> json_extract(json = {'b': 3,  '6': 7,  'jub': {'uy': [1, 2, 3],  'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},  fuzzy_keys = True,   filter_path = '[a-z]{2}~~@nn0') 
[]
>>> json_extract(json = {'b': 3, '6': 7,  'jub': {'uy': [1, 2, 3],  'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}, filter_path = '..~~@zz[5-8];;nn5:9', get_full_path_also = True) # returns a dict mapping complete paths to children.
{('jub', 'yu', 1, 'M8'): 9, ('6',): 7}
>>> json_extract(json = {'b': 3,  '6': 7,'jub': {'uy': [1, 2, 3],'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}, filter_path = '[5-8];;nn5:9')
[]
>>> json_extract(json = {'b': 3, '6': 7, 'jub': {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}}, filter_path = '..~~@zznnint(k)*2<4vvnnstr(v)>`8`', get_full_path_also = True)
{('jub', 'yu', 1): {'y': 'b', 'M8': 9, 1: (3, 0)}}
>>> json_extract(json = {'b': 3, '6': 7, 'jub': {'uy': [1, 2, 3],  'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},  filter_path = '..~~@nnint(k)*2<4vvnnstr(v)>`8`', get_full_path_also = True) 
Traceback (most recent call last):
...
gorp.jsonpath.aggregate.JsonPathError: When not in fuzzy_keys mode, only IntRange slicers and ints are allowed as key tests.
>>> json_extract(json = [[1, 2, 3, 4, 5], {0: 'a', 1: 'b'}, {2: 'c'}, [6, 7], {3: 'd'}], filter_path = 'nn:3~~@nn1:3', get_full_path_also = True)
{(0, 1): 2, (0, 2): 3}
>>> json_extract(json = [[1, 2, 3, 4, 5], {0: 'a', 1: 'b'}, {2: 'c'}, [6, 7], {3: 'd'}],  filter_path = 'nn:3~~@..~~@ggnn1vvnnx[0]<x[1]', get_full_path_also = True)
{(0, 1): 2, (1, 1): 'b'}
>>> json_extract(json = [[1, 2, 3, 4, 5], {0: 'a', 1: 'b'}, {2: 'c'}, [6, 7], {3: 'd'}],  filter_path = 'nn:3~~@..~~@ggnn1:3vvnnx[0]<x[1]', get_full_path_also = True)
{(0, 1): 2, (0, 2): 3}
>>> json_extract(json = {'b': 3, '6': 7,'jub': {'uy': [1, 2, 3],'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},filter_path = 'zz[a-z]')
[3, {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3, 0)}]}]
>>> json_extract(json = {'b': 3, '6': 7,  'jub': {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},  filter_path = '..~~@zz(?i)^[M-Y]||vvnn1:10:2', get_full_path_also = True) 
{('jub', 'uy'): [1, 2, 3], ('jub', 'yu'): [6, {'y': 'b', 'M8': 9, 1: (3, 0)}], ('6',): 7, ('b',): 3}
>>> json_extract(json = {'b': 3,   '6': 7,   'jub': {'uy': [1, 2, 3],           'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},    filter_path = 'zz!!\d~~@!!yu', get_full_path_also = True) 
{('jub', 'yu'): [6, {'y': 'b', 'M8': 9, 1: (3, 0)}]}
>>> json_extract(json = {'b': 3,   '6': 7,   'jub': {'uy': [1, 2, 3],  'yu': [6, {'y': 'b', 'M8': 9, 1: (3,0)}]}},  fuzzy_keys = True,   filter_path = '..~~@(?i)[a-z]+\d~~^^',  get_full_path_also = True)
{('jub',): {'uy': [1, 2, 3], 'yu': [6, {'y': 'b', 'M8': 9, 1: (3, 0)}]}}
>>> json_extract(filter_path = 'zz^[a-z]vvnnv>3&&str(v)<`3`', json = {'a':17, 'b':2, 'c': 4, 'd': 31}, get_full_path_also=True) 
{('a',): 17}
>>> json_extract(json = {'b': 3,  'g6': 2,  '6': 7}, filter_path = "ggvvnnstr(x[`b`]) =~ `^\d`~~zz\dvvnnx<4")
[2]
>>> parse_json_path("nn5:8vv77")
[[Filter(keys_in = [IntRange(5, 8, 1)], vals_in = ['77'], key_or_val = False, action = 'down', fuzzy_keys = False)]]
>>> parse_json_path("\\d\\n~~}") # don't forget to turn on fuzzy_keys if you want regex!
ALERT: It looks like you may have tried to match keys with regular expressions
['\\\\d'] while not in fuzzy_keys mode. Did you intend this?
[[Filter(keys_in = ['\\\\d\\n'], vals_in = [], key_or_val = False, action = 'stay', fuzzy_keys = False)]]
>>> parse_json_path("zzx*3<=4**3")
ALERT: It looks like you may have forgotten to use the 'nn' token to indicate that the equation(s)
['3<=4'] should be treated as math expressions. Did you intend this?
[[Filter(keys_in = ['x*3<=4**3'], vals_in = [], key_or_val = False, action = 'down', fuzzy_keys = True)]]
>>> parse_json_path("^[a-z]{2}$||vvnnx<3&&x>2;;nn^[23]", fuzzy_keys = True)
[[Filter(keys_in = ['^[a-z]{2}$'], vals_in = [['compute("x<3")', 'compute("x>2")'], '^[23]'], key_or_val = True, action = 'down', fuzzy_keys = True)]]
>>> parse_json_path("3~~ggnn1:4:2vvnnx[0]>1")
[[Filter(keys_in = ['3'], vals_in = [], key_or_val = False, action = 'check', fuzzy_keys = False), GlobalConstraint(keys_in = [IntRange(1, 4, 2)], vals_in = ['compute("x[0]>1")'], action = 'down')]]
>>> parse_json_path('..~~@yu~~zzvvuy~~^^')
['..', [Filter(keys_in = ['yu'], vals_in = [], key_or_val = False, action = 'check', fuzzy_keys = False), Filter(keys_in = [], vals_in = ['uy'], key_or_val = False, action = 'up2', fuzzy_keys = True)], [Filter(keys_in = [''], vals_in = [], key_or_val = False, action = 'down', fuzzy_keys = True)]]
>>> list(JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2}).follow_path(1))
[(('a',), [1, 2, 3])]
>>> dict(JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2}).follow_path())
{('a', 1): 2, ('a', 2): 3}
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> dict(jpath_ex.follow_path(1)) 
{('a',): [1, 2, 3]}
>>> dict(jpath_ex.follow_path(1)) 
{}
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> jpath_ex.resultset
>>> jpath_ex.curLayer
0
>>> jpath_ex.descend(1) # applies the filter(s) in layer 0, and descends to layer 1.
>>> jpath_ex.resultset
{('a',): [1, 2, 3]}
>>> jpath_ex.descend(1) # applies the filters in layer 1, which is the last layer
>>> jpath_ex.resultset
{('a', 1): 2, ('a', 2): 3}
>>> jpath_ex = JsonPath('a~~@nn1:', json={'a':[1,2,3],'b':2})
>>> jpath_ex.sub(lambda x: (x+1)*2, False)
>>> jpath_ex.json
{'a': [1, 6, 8], 'b': 2}
>>> JsonPath('b~~@nn1:', json = jpath_ex.json).sub(lambda x: x*3, False, 1)
>>> jpath_ex.json
{'a': [1, 6, 8], 'b': 6}
>>> JsonPath('a~~@nn1:~~ss str(x)', json = jpath_ex.json).sub(ask_permission=False, layers = 2)
>>> jpath_ex.json
{'a': [1, '6', '8'], 'b': 6}
>>> path_vals = [{'a': 1, 'b': 2, 'c': 3}, {'d': 4}, {'e': 5}]
>>> jp = JsonPath("nn:~~@zz[a-z]", json = path_vals)
>>> jp.aggregate(sum, 1)
{('a',): 1, ('b',): 2, ('c',): 3, ('d',): 4, ('e',): 5}
>>> jp.aggregator = Aggregator(sum, 0)
>>> jp.aggregate()
{(0,): 6, (1,): 4, (2,): 5}
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
    pass


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    doctest.testmod(aggregate)
