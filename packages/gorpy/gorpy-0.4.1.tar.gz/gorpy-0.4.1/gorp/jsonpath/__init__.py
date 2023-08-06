'''Contains utilities for performing complex searches in nested Python 
    iterables based on both keys/indices and values.
    This has been tested (using gorp.test.test_jsonpath) on Python 3.6-3.9.
    It might work on 3.5, but no warranty is made except for 3.6-3.9.
The most immediately comparable project in terms of scope is jsonpath_ng, 
    which is fully JsonPath standard-compliant, but which appears to me to 
    lack some of this module's power, such as regex matching on keys.
Some things that you can do with this module:
    - Use regular expressions to match keys as well as values in dicts.
    - Filter layers of JSON based on comparisons of multiple values (e.g., 
        get indices 1:10 of an array only if arr[1] > str(arr[2]))
    - Mutate JSON at the nodes found by a search.
    - Enable the calculation of aggregates on nested iterables while grouping
        by different levels of organization.
    - Filter pandas DataFrames using the same query language, while still 
        getting their incredibly fast performance.
    - If you prefer not to use a query parser, build layers of filters by an 
        object-oriented approach. See the Filter, GlobalConstraint, Mutator, 
        and JsonPath classes. Thanks to jsonpath_ng for pioneering this 
        approach!
    - Build arithmetic expressions of the values and keys in an iterable 
        without using eval(). See math_eval, and its workhorse function, 
        compute(eqn).
The searching of nested iterables (which we'll call JSON for short) in this 
    module works using a "filter path" that contains ordered "filter layers" 
    that may look  something like this::
    [
    '..', # flag that turns on recursive search (descend til you find a match).
        [ # layer 1
        Filter(keys_in = ['key', number], # key must match one of these
               vals_in = ['a regex'], # corresponding value must match this
               fuzzy_keys = True), # keys_in can have regexes or functions
        GlobalConstraint(keys_in = ['blah'], # this key must be in the iterable
                         vals_in = [lambda x: x['a']>x['b']], 
                         # constraint on the iterable as a whole
                         action = 'down')
        ], 
        # if the iterable matched both filters, descend to iterable['blah']
    '!!', # another type of flag (the below constraints should NOT be matched).
        [ # layer 2
        Filter(keys_in = ['baz'], # key that must be in the iterable 
               vals_in = [lambda x: (x<3) and (x>0)], 
               # constraint on the value associated with that key
               action = 'up2', 
               # if the iterable satisfied this filter, we'll go up to the
               # grandparent of this iterable
               fuzzy_keys = False) 
               # keys must match a string/number in keys_in exactly
        ],
    <optional Mutator object for updating JSON or Aggregator object>
    ]

In this example, we see that our filter path can contain:
    
    1. flags ('..' and '!!') that change how filters are used
    
    2. sublists of filters that all operate on the same level of the JSON (so 
        layer 1 operates on the root level of the JSON,
        layer 2 operates on the second level of key-value pairs, and so on)
        - Even if you only have one filter in a layer, it has to be contained 
            in a list.
    
    3. An optional Mutator or Aggregator object after all the filter sublists.

Note that the user of this module doesn't need to explicitly build a list of 
filter layers like the one shown above; the parse_json_path and related 
functions take care of translating query strings into layers of filters, 
so a query string like::
    ..~~@zzfo{2};;nn1:vv^[a-z]+$~~ggblahvvnnx[`a`]>x[`b`]~~@!!zzbazvvnnx<3&x>0~~^^

would translate directly into one possible list of filter layers that 
would match the example above.

I have not attempted to comply with the JsonPath "standard" established by 
Stefan Goessner (https://goessner.net/articles/JsonPath/), which in turn 
was inspired by the syntax of the much-better-known XPath for XML.

I apologize for the lack of compliance with this standard, and I apologize 
still more for the rather long query strings caused by my profuse use of 
special double-characters,
but I would also like to explain the philosophy that motivates this choice:
    
    * Regular expressions have many special characters, including '.' and '*'.
    In any application like this where regular expressions are used, 
    it is inconvenient for '.' and '*' have any other special meanings.
    
    * A special double-character is easily compatible with regular 
    expressions because any double-character can be expressed as 
    "character{2}" in regex.
    
    * A more talented programmer than I could undoubtedly create a parser 
    that can handle the overloading of special characters, but I can't.
'''
from gorp.jsonpath.jsonpath import *
__version__ = '0.2.0'
