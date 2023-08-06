from gorp.jsonpath.filters import *
from gorp.jsonpath.mutate import *
import re

def parse_json_path_tuple(node, 
                          fuzzy_keys,
                          ask_about_ambiguity, 
                          possible_uncomputed_eqns, 
                          possible_nonfuzzy_regexes = None,
                          numer_mode = False, 
                          recursions = 0):
    '''Parses the key part or the value part of a json_path step.'''
    out = []
    if recursions:
        splitter = '&&'
    else:
        splitter = ';;' # separates a condition that does not have to be satisfied
                        # at the same time as any other conditions
    for elt in node.split(splitter):
        # print('    '*recursions + "in parse_json_path_tuple, elt = "+repr(elt))
        if elt[:2] == 'nn':
            numer_mode = not numer_mode
            elt = elt[2:]
        if '&&' in elt: # a tuple of bundled conditions within a tuple!
            out.append(parse_json_path_tuple(elt,
                                             fuzzy_keys,
                                             ask_about_ambiguity,
                                             possible_uncomputed_eqns,
                                             possible_nonfuzzy_regexes,
                                             numer_mode, 
                                             recursions + 1))
            continue
        if numer_mode:
            compute_result = compute(elt)
            out.append(compute_result)
        else:
            if (possible_nonfuzzy_regexes is not None) and (not fuzzy_keys):
                maybe_nonfuzzy_regex = re.findall("\\\\[ds]", elt)
                # "\s" and "\d" are probably the most 
                # distinctive features of regular expressions.
                possible_nonfuzzy_regexes.extend(maybe_nonfuzzy_regex)
            maybe_uncomputed_eqn = re.findall("(?:\d+|:|[`a-zA-Z]+)?[<>=!]=?(?:\d+|:|[`a-zA-Z]+)", elt)
            if maybe_uncomputed_eqn:
                possible_uncomputed_eqns.extend(maybe_uncomputed_eqn)
            out.append(elt)
    # print('    '*recursions+"In parse_json_path_tuple, out = "+repr(out))
    return out


def parse_json_path_step(elt, 
                         filters, 
                         layer, 
                         action, 
                         fuzzy_keys,
                         ask_about_ambiguity, 
                         possible_uncomputed_eqns,
                         possible_nonfuzzy_regexes):
    '''Parses a string representing a single substep in a json path layer as 
    described in parse_json_path.__doc__.'''
    global_constraint = False
    if elt == '..':
        filters[layer] = '..'
        return layer + 1, fuzzy_keys
    while elt[:2] in {'!!', 'zz', 'gg'}:
        if elt[:2] == 'gg':
            global_constraint = True
            elt = elt[2:]
            continue
        elif elt[:2] == 'zz':
            fuzzy_keys = not fuzzy_keys
            elt = elt[2:]
            continue
        elif filters.get(layer) is not None:
            raise JsonPathError("The reverse_selectivity-toggling '!!' token must be declared at the beginning of a filter layer. If you have one or more 'check' filters and then a non-check filter, the '!!' token must be before the first consecutive 'check' filter.")
        if elt[:2] == '!!':
            filters[layer] = '!!'
            layer += 1
            elt = elt[2:]
        
    key_or_val = False
    try:
        filters.setdefault(layer, [])
        val_part = elt.index('vv')
        e = [elt[:val_part], elt[val_part+2:]] #e[0] will be keys_in, e[1] vals_in
        # print(e)
        if e[0] == '':
            keys_in = tuple()
        else:
            if e[0][-2:] == '||':
                e[0] = e[0][:-2]
                key_or_val = True
            keys_in = parse_json_path_tuple(e[0],
                                            (fuzzy_keys and not global_constraint),
                                            ask_about_ambiguity, 
                                            possible_uncomputed_eqns,
                                            possible_nonfuzzy_regexes)
        vals_in = parse_json_path_tuple(e[1], 
                                        True, #fuzzy_keys only applies to keys.
                                        ask_about_ambiguity, 
                                        possible_uncomputed_eqns,
                                        None)
    except Exception as ex: # this is likely because there is no 'vv' in elt,
                            # causing a "ValueError: substring not found"
                            # at "val_part = elt.index('vv')". We assume this means
                            # that the user didn't intend to add any vals_in
                            # constraints
        if isinstance(ex, (JsonPathError, ComputeError)):
            raise JsonPathError(ex)
        keys_in = parse_json_path_tuple(elt, 
                                        (fuzzy_keys and not global_constraint),
                                        ask_about_ambiguity, 
                                        possible_uncomputed_eqns,
                                        possible_nonfuzzy_regexes)
        vals_in = tuple()
    if global_constraint:
        filters[layer].append(GlobalConstraint(keys_in = keys_in,
                                               vals_in = vals_in,
                                               action = action))
    else:
        filters[layer].append(Filter(keys_in, 
                                     vals_in, 
                                     key_or_val, 
                                     action, 
                                     fuzzy_keys))
    updown_count = sum(filt.action != 'check' for filt in filters[layer])
    if updown_count > 1:
        raise JsonPathError("Error at filter layer {}: Cannot have more than one filter with an action other than 'check'".format(layer))
    if action == 'check':
        return layer, fuzzy_keys
    return layer+1, fuzzy_keys


def parse_json_path(x, 
                    fuzzy_keys = False, 
                    ask_about_ambiguity = True):
    """*x*: a string.

*fuzzy_keys*: See the same argument of json_extract.__doc__.

*ask_about_ambiguity*: Print possibly helpful messages when x appears to have a
    malformed pipe, a missing 'nn' for declaring "compute mode",
    or a missing 'zz' for declaring fuzzy_keys mode when using regexes.

RULES FOR PARSING AN ENTIRE JSON PATH ('x'):
    
    * x is split into path layers or substeps by one of the delimiters 
    {'~~', '~~@', '~~^+'), '~~}'}.
        
        * '~~' means that the preceding path substep serves as a "check"; 
        (de/a)scent to a child or parent cannot proceed unless all checks 
        at a path layer are satisfied.
        There can be any number of checks at a path layer.
        
        * '~~@' comes at the end of a path layer; it means that once all the 
        checks are satisfied at the current path layer, you begin searching 
        the CHILDREN of all nodes that satisfied the preceding check.
        
        * '~~^+' also comes at the end of a path layer; it means that
        once all the checks are satisfied at the current path layer, you 
        begin searching the n^th ancestor of the current level of json, 
        where n is the number of '^' characters.
        
        * '~~}' can be supplied as the last three characters of a path.
        It means that if the all the checks in the current layer of json were
        satisfied, you return the CURRENT LAYER, not children or ancestors.
        
        * Descent-type-search (as specified by '~~@') is the default, so the 
        final path layer will always return the children of all matched nodes
        unless the path is terminated with '~~}' or '~~^+'.
    
    * '..' switches json_extract into recursive search mode.
    Recursive search mode is off by default.
    
    * '!!' as its own path layer or at the beginning of another path layer 
    is treated as a special indicator that toggles reverse_selectivity mode.
    
    * 'zz' at the beginninng of another path layer toggles fuzzy_keys, which 
    changes the fuzzy_keys parameter of the Filters created by this function.
    
    * 'gg' at any point in a path layer (including on a "check" filter in a
    multi-substep path layer) creates a GlobalConstraint rather than a Filter.
    
    * '~~ss<func of one variable>' as the FINAL ELEMENT IN A PATH
    (even after '~~}') ends the path with a :class:`Mutator` object that 
    can be used to perform in-place transformations on the JSON after paths 
    have been found by json_extract() or JsonPath.extract().
    
    * 'AGG<func of one iterable variable>(BY<integer|IntRange>)' as the
    FINAL ELEMENT IN A PATH (even after '~~}') ends the path with a 
    :class:`Aggregator` object that can be used to aggregate the data found
    by json_extract or JsonPath.extract().


RULES FOR PARSING A SINGLE PATH SUBSTEP (performed by parse_json_path_step):
    
    * 'nn' at any point in a path substep toggles "compute mode".
    While the parser is in "compute mode", it interprets everything as a
    mathematical expression, and passes it into :func:`math_eval.compute`.
    Thus, it is easier to include string filters at the beginning of a tuple
    path substep and numeric filters at the end of a tuple path substep.
    
    * ';;' separates two elements within the path substep.
    
    * '&&' separates two elements within the path substep, and every 
    consecutive element joined by '&&' is bundled together; 
    so 'cond1;;cond2&&cond3;;cond4' 
    would filter on cond1 OR (cond2 AND cond3) OR cond4.
    
    * 'vv' is a delimiter. 
    everything after 'vv' in the path substep is a filter on VALUES and 
    everything before 'vv' is a filter on KEYS.
        * Note that 'vv' resets the 'nn' flag.
        This means that you need to use 'nn' to turn on compute mode 
        separately for values and keys.
        * Note also that for a GlobalConstraint, everything after the 'vv' 
        flag is a filter on the iterable as a whole.
    
    * By default, a path substep must match at least one key filter AND at 
    least one value filter, assuming both key and value filters are supplied.
    
    * '||' is an optional indicator that can be used with 'vv'.
    When '||' is supplied, the filter at that path substep only requires that
    a key filter OR a value filter is matched.
    
        * The '||' flag does not do anything when used on a GlobalConstraint.
    
    * When not in compute mode, all strings (including numeric strings) are 
    treated as regular expressions if fuzzy_keys = True and not inside a 
    :class:`GlobalConstraint`.
    Otherwise, they are treated as plain strings.

EXAMPLES: 
________

>>> parse_json_path("nn5:8vv77")
[[Filter(keys_in = [IntRange(5, 8, 1)], vals_in = ['77'], key_or_val = False, action = 'down', fuzzy_keys = False)]]
>>> parse_json_path("\\d\\n~~}") # don't forget to turn on fuzzy_keys if you want regex!
ALERT: It looks like you may have tried to match keys with regular expressions
['\\d'] while not in fuzzy_keys mode. Did you intend this?
[[Filter(keys_in = ['\\d\\n'], vals_in = [], key_or_val = False, action = 'stay', fuzzy_keys = False)]]
>>> parse_json_path("zzx*3<=4**3")
ALERT: It looks like you may have forgotten to use the 'nn' token to indicate that the equation(s)
['3<=4'] should be treated as math expressions. Did you intend this?
[[Filter(keys_in = ['x*3<=4**3'], vals_in = [], key_or_val = False, action = 'down', fuzzy_keys = True)]]
>>> parse_json_path("^[a-z]{2}$||vvnnx<3&&x>2;;nn^[23]", fuzzy_keys = True)
    # the "nnx<3&&x>2" means that the conditions "x<3" and "x>2" must BOTH be satisfied.
    # The other condition, "^[23]", wants the value to be a string starting with '2' or 
    # '3'. 
    # So long as BOTH of the first two conditions OR the third condition is/are satisfied,
    # this vals_in requirement is met.
[[Filter(keys_in = ["^[a-z]{2}$"], vals_in = [[compute('x<3'), compute('x>2')], "^[23]"], key_or_val = True, action = 'down', fuzzy_keys = True)]]
>>> parse_json_path("3~~ggnn1:4:2vvnnx[0]>1")
[[Filter(keys_in = ['3'], vals_in = [], key_or_val = False, action = 'check', fuzzy_keys = False), GlobalConstraint(keys_in = [IntRange(1, 4, 2)], vals_in = [compute('x[0]>1')], action = 'down')]] 
>>> parse_json_path('..~~@yu~~zzvvuy~~^^')
['..', [Filter(keys_in = ['yu'], vals_in = [], key_or_val = False, action = 'check', fuzzy_keys = False)], [Filter(keys_in = [], vals_in = ['uy'], key_or_val = False, action = 'up2', fuzzy_keys = True)], [Filter(keys_in = [''], vals_in = [], key_or_val = False, action = 'down', fuzzy_keys = True)]]
>>> parse_json_path('a~~@nn1:~~}~~ss str(x)')
[[Filter(keys_in = ['a'], vals_in = [], key_or_val = False, action = 'down', fuzzy_keys = False)], [Filter(keys_in = [IntRange(1, inf, 1)], vals_in = [], key_or_val = False, action = 'stay', fuzzy_keys = False)], Mutator(replacement_func = 'compute( str(x))')]
    """
    mutator = False
    aggregator = False
    if '~~ss' in x:
        x, replacement_funcname = x.split('~~ss')
        mutator = Mutator(replacement_funcname)
    elif 'AGG' in x:
        x, agg_func = x.split('AGG')
        agg_level = None
        if 'BY' in agg_func:
            agg_func, agg_level = agg_func.split('BY')
            agg_level = compute(agg_level)
        aggregator = Aggregator(agg_func, agg_level)
    arr = re.split('(~~(?:\^+|[@\}])?)', x)
    possible_uncomputed_eqns = []
    possible_nonfuzzy_regexes = []
    if ask_about_ambiguity:
        possible_malformed_pipes = re.findall("(?<!~)~[@\^\}]", x)
        if possible_malformed_pipes:
            pass
            print("ALERT: It looks like you included path-splitting pipe(s) with only one '~': {}.\nIs this what you intended?".format(possible_malformed_pipes))
    filters = {}
    layer = 0
    for ii, elt in enumerate(arr):
        if ii == len(arr)-1:
            action = 'down'
        elif arr[ii+1] == '~~':
            action = 'check'
        elif re.search("~~\^+", arr[ii+1]):
            action = 'up'+str(arr[ii+1].count("^"))
        elif arr[ii+1] == '~~@':
            action = 'down'
        elif arr[ii+1] == '~~}':
            action = 'stay'
        if elt[:2] == '~~':
            if len(elt)==3 and elt == '~~}':
                break
            continue
        layer, fuzzy_keys = parse_json_path_step(elt, 
                                     filters,
                                     layer, 
                                     action,
                                     fuzzy_keys,
                                     ask_about_ambiguity, 
                                     possible_uncomputed_eqns,
                                     possible_nonfuzzy_regexes)
    if ask_about_ambiguity and possible_uncomputed_eqns:
        pass
        print("ALERT: It looks like you may have forgotten to use the 'nn' token to indicate that the equation(s)\n{} should be treated as math expressions. Did you intend this?".format(possible_uncomputed_eqns))
    if ask_about_ambiguity and possible_nonfuzzy_regexes:
        pass
        print("ALERT: It looks like you may have tried to match keys with regular expressions\n{} while not in fuzzy_keys mode. Did you intend this?".format(possible_nonfuzzy_regexes))
    filters = [filt for lay, filt in sorted(filters.items(), key = lambda x: x[0])]
    if mutator:
        return filters + [mutator]
    elif aggregator:
        return filters + [aggregator]
    return filters

