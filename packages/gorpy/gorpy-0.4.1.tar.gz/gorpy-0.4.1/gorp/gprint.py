"""
This is generally worse than the built-in module pprint.
However, pprint has an annoying tendency to chop apart long strings into 
little chunks that can span many lines. For example gprint.gprint() on a 
certain dictionary will print stuff that looks like this:
'''
'C:\\Users\\molso\\AppData\\Local\\Programs\\Python\\Python38\\yaml_found_in_yaml_example.yaml':
    {
    "('C:\\\\Users\\\\molso\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python38\\\\reurenwn.yaml', 1)": 3,
    "('C:\\\\Users\\\\molso\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python38\\\\yaml example.yml', 1)": 'see also https://pynative.com/python-yaml/'
    }
'''
whereas the builtin pprint.pprint() would print this:
'''
 'C:\\Users\\molso\\AppData\\Local\\Programs\\Python\\Python38\\yaml_found_in_yaml_example.yaml': {"('C:\\\\Users\\\\molso\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python38\\\\reurenwn.yaml', 1)": 3,
                                                                                                   "('C:\\\\Users\\\\molso\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python38\\\\yaml example.yml', 1)": 'see '
                                                                                                                                                                                                            'also '
                                                                                                                                                                                                            'https://pynative.com/python-yaml/'}

'''
The gprint.gprint() version makes is easy to read the line "see also ...", 
whereas the pprint.pprint() version is hard to read. 
This gets worse for very long string values.
Because gorp reads a lot of very long strings (lines from files),that kind of
automatic string-chopping is very annoying and adversely impacts readability.
The normal alternative, using default print(), results in a nigh-unreadable 
block of JSON.

Of course, pprint uses an OOP-based approach, and there are probably ways 
around that particular issue using pprint alone, but I found it easier to 
design my own module to address this problem.
"""
import re
import json
from .utils import funcname, is_iterable

bad_json = {'a': False,
 'b': '3',
 '6': 7,
 '9': 'ball',
 'jub': {'uy': (1, 2, float('nan')),
  'yu': [[6, {'y': 'b', 'm8': 9}], None],
  'status': 'jubar'},
 '9"a"': 2,
 'blutentharst': ['\n\'"DOOM" BOOM, AND I CONSUME\', said Bludd, the mighty Blood God.\n\t',
  True]} # for testing


def bracket_of_itbl(x, jsonify, start = True):
    '''Returns the opening (if start) or closing (if not start) bracket of an iterable.
If jsonify, it just returns '{' or '}' for dicts and '[' or ']' for 
everything else.'''
    if jsonify:
        if isinstance(x, dict):
            if start:
                return '{'
            return '}'
        else:
            if start:
                return '['
            return ']'
            
    else:
        if isinstance(x, list):
            if start:
                return '['
            return ']'
        elif isinstance(x, dict) or isinstance(x, set):
            if start:
                return '{'
            return '}'
        elif isinstance(x, tuple):
            if start:
                return '('
            return ')'
        else: # is some other iterable class
            if start:
                return funcname(type(x)) + '(['
            return '])'

def key_repr(key, jsonify = False):
    if jsonify:
        return json.dumps(str(key)) 
        # object keys must be strings in JSON
    return repr(key)


def val_repr(val, jsonify = False):
    if jsonify:
        return json.dumps(val)
    return repr(val)


def gprint(x, buff = None, indent = 4):
    '''A simple function that pretty-prints objects according to rules that 
    differ from pprint.pprint.
buff: one of {
    str: returns string, 
    None: prints to sys.stdout, 
    '_io.TextIOWrapper' object returned by open(fname, 'w'): writes x to file}
indent: int, the number of spaces of indentation per layer of depth.
NOTES:
    - If buff is an '_io.TextIOWrapper' object from open(fname, 'w'), x will be
        JSONified before writing to file. Thus all dicts and dict subclasses 
        will be coerced to JSON Objects, all dict keys will be converted to 
        strings, every iterable that's not a dict will be coerced to an array,
        and the mappings 
        {None: 'null', math.inf: 'Infinity', float('nan'): 'NaN'} 
        will be made.
    - Thus, an object written to file by gprint() can be reconstituted by 
        json.load().
    '''
    jsonify = buff not in [None, str]
    def addon(itbl, arr, indent, depth = 0, islast = False):
        if islast:
            terminator = '\n'
        else:
            terminator = ',\n'
        if re.search('DataFrame|Series', str(type(itbl))):
            # The default string representation of DataFrames is much prettier
            # than whatever gprint would do.
            arr.append(repr(itbl) + terminator)
            return
        isdict = isinstance(itbl, dict)
        arr.append(' '*indent*depth + bracket_of_itbl(itbl, jsonify) + '\n')
        for ii, e in enumerate(itbl):
            e_islast = (ii == len(itbl)-1)
            if isdict:
                if is_iterable(itbl[e]):
                    arr.append(' '*indent*depth + key_repr(e, jsonify) + ':\n')
                    addon(itbl[e], arr, indent, depth + 1, e_islast)
                else:
                    if e_islast:
                        arr.append(' '*indent*depth + key_repr(e, jsonify) + ': ' \
                            + val_repr(itbl[e], jsonify) + '\n')
                    else:
                        arr.append(' '*indent*depth + key_repr(e, jsonify) + ': ' \
                            + val_repr(itbl[e], jsonify) + ',\n')
            else:
                if is_iterable(e):
                    addon(e, arr, indent, depth + 1, e_islast)
                else:
                    if e_islast:
                        arr.append(' '*indent*depth + val_repr(e, jsonify) + '\n')
                    else:
                        arr.append(' '*indent*depth + val_repr(e, jsonify) + ',\n')
        arr.append(' '*indent*depth + bracket_of_itbl(itbl, jsonify, False) \
                    + terminator)
    if not is_iterable(x):
        out = repr(x)
    else:
        arr = []
        addon(x, arr, indent)
        out = ''.join(arr)[:-2]
    if buff is None:
        print(out)
    elif buff == str:
        return out
    else:  
        # assumes buff is an '_io.TextIOWrapper' object returned by
        # open(filename, 'w')
        buff.write(out)
        

def compressed_obj_repr(obj, maxlines = 10, printer = gprint):
    '''If the representation of a Python object obj (as made by printer, any function 
    that takes an object as argument and returns a string) would take up more 
    than maxlines lines, print the first (maxlines//2) lines, then 
    "... (number of lines in full representation) ...",
    then the last (maxlines//2) lines.
EXAMPLE:
_________
>>> compress_obj_repr({'a': False, 'b': '3', '6': 7, '9': 'ball', 'jub': {'uy': (1, 2, float('nan')),  'yu': [[6, {'y': 'b', 'm8': 9}], None],  'status': 'jubar'}, '9"a"': 2, 'blutentharst': ['\n\'"DOOM" BOOM, AND I CONSUME\', said Bludd, the mighty Blood God.\n\t', True]}, maxlines = 8)
{
'a': False,
'b': '3',
'6': 7,
... 33 lines total ...
    '\n\'"DOOM" BOOM, AND I CONSUME\', said Bludd, the mighty Blood God.\n\t',
    True
    ]
}
    '''
    json_repr = printer(obj, str).split('\n')
    if len(json_repr) <= maxlines:
        return '\n'.join(json_repr)
    else:
        return '\n'.join(json_repr[:(maxlines//2)] + 
                         ['... {} lines total ...'.format(len(json_repr))] + 
                         json_repr[-(maxlines//2):])


if __name__ == '__main__':
    import os
    fname = os.path.join(os.path.dirname(__file__),'bad_json.json')
    with open(fname, 'w') as f:
        gprint(bad_json, f, 6)
    with open(fname) as f:
        bad_json_loaded = json.load(f)
    gprinted_bad_json = gprint(bad_json, str)
    gprint("Printing a simple nested container:")
    gprint({1: [1,2,3], (1,2): frozenset({2,3})})
    gprint("Printing a number:")
    gprint(2.343)