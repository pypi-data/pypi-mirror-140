from .utils import textTypeFiles
from .gprint import gprint

option_descriptions = {
"a": "-a(ll file types, names only)",
"b": "-b (read all files, regardless of type, as raw bytes)",
"c": "-c(ount occurrences of pattern)",
"d": "-d(irectory names only)",
"docx": "-docx (read text of Word documents)",
"e": "-e (read a list of filenames from a JSON or YAML file)",
"f": "-f(ilenames and directories only)",
"g": "-g (execute a series of gorp commands written in a text file)",
"h": "-h (display lines, not files)",
"i": "-i (case insensitive)",
"j": "-j (read JSON files as JSON, using gorp.jsonpath)",
"k": "-k (kill [i.e. delete] all files found, pending user permission for each one",
"l": "-l (list filenames)",
"m": "-m (get last Modification time; sort files by most recent first)",
"n": "-n (get paths/line Numbers of results found)",
"num": "-<integer> (truncate resultset to length <integer>)", 
"o": "-o (match only entire words)",
"p": "-p (oPen all files in the final resultset with their default apps)",
"pdf": "-pdf (read text of PDF files)",
"q": "-q (get union (Qnion?) of two resultsets)",
"r": "-r(ecursive search)",
"s": "-s(izes of files found; sorts files by size descending)",
"sed": '''-sed (Find regex and replace with repl in text files. The correct syntax is "(other_queries -}})? <options> -sed 'regex//repl'".)''',
"t": "-t (number of files found (and total size if -s arg used)",
"tab": "-tab (read tabular files (e.g. csv) using gorp.jsonpath. Supports pandas.",
"u": "-u(pdate all files or their contents according to some function)",
"v": "-v (display only things that DON'T match)",
"w": "-w (write results of query to a JSON or YAML file)",
"x": "-x (use XPath or CSS selectors to navigate XML and HTML files)",
"y": "-y (read YAML files as YAML, using gorp.jsonpath. See -j option documentation)",
"z": "-z[lb]? (write copies of all files found to a Zip archive at target location with optional BZIP or LZMA compression)"
}


detailed_option_descriptions = {
    'm': '''You can get all files ordered by mod time with just '-m',
    or (with version >=0.4.0) you can filter with '-m[><=]=?<date>', where 
    <date> is any date in YYYY-MM-DD format, or a fragment like yyyy-mm''',
    
    's': '''You can get all files ordered by size (desc) with just '-s',
    or (with gorp version >=0.4.0) you can filter with '-s[><=]=?<size>', 
    where <size> is a number of bytes, which can be unitless or measured in 
    bytes, b, KB, MB, or GB''',
    
    'u': '''The -u option updates text files or renames files and 
    directories, and may use an interactive prompt.
The general syntax is "subquery (-}} other_subquery)* -}} -u 'function'.
    If you want to edit text files sed-style, 'function' should be replaced with
    'x sub `regex//replacement`'. Note that the regex and replacement must be separated
    by '//' and enclosed in backticks ('`').
    However, you can also have other functions like 'str(int(x[3:4])*3)' or 'x**3'.
To rename files, the -u option should come immediately after a -f, -a, or -d option,
    all of which filter on file/directory names rather than text.
Note that the -u option is not just a sed/mv workalike- it can also edit the termini of
    paths found by the -j and -y options.
DEFAULTS.U_OPTION_OVERWRITES determines whether the -u option overwrites files with the
    updated version or creates a new file with a filename incremented from the original.
DEFAULTS.PROMPT_U_OPTION determines whether there's an interactive prompt that considers
    each edit on a case-by-case basis.''',
    
    'b': '''Does not work with any options other than ['-r', '-l', '-h', '-i', '-c', '-o', '-n', '-v'].
Added in version 0.2.5.''',
    
    'z': '''-zb and -zl variants for BZIP and LZMA compression added in version 0.2.5.''',
    
    'e': '''The syntax is "-e <other options> '<regex>' /<fname>.(json|yaml)".
fname.json (or fname.yaml) should contain a single array of valid filenames
or a dict with valid filenames as keys. A typical use of the -e option would
be to first dump a bunch of filenames into a json/yaml file with the -w option
and then read it in the future with the -e option.''',
    
    'f': f'''This option filters filenames, and ignores filenames with 
extensions not in the following list:
{gprint(sorted(textTypeFiles), str)}''',

    'g': '''The syntax for the -g option is "python -m gorp -g <text file name>".
Added in version 0.2.4 for command line use only.
Added for general use in version 0.2.5.''',
    
    'docx': "Gets the text only. No formatting information is extracted.",
    
    'x': '''See the documentation of 'lxml' and 'cssselect' to learn more.
I am not very familiar with either package, and this option may be bugged without my
    knowledge.''',
    
    'v': '''Don't make the mistake of assuming that the -v option on text
    will exclude all files that contain lines that DO match the regex.
If a file contains some lines that DO match the regex and some that DON'T, the -v option
    will get all the lines that don't match from that file.''',
    
    'pdf': '''Because extracting text from PDFs can take an extremely long time,
    gorp ignores all PDFs longer than 100 pages by default.
DEFAULTS.PDF_PAGE_LIMIT controls this limit.
After the text has been extracted for the first time, the text is stored in
    pdf_textcache.json, located in gorp's directory, and loaded whenever the pdf
    option is invoked in future sessions.
This caching of text means that subsequent queries to the same file are very fast.''',

    'k': '''Delete files found by queries.
DEFAULTS.ALLOW_REMOVE_TREES determines whether the -k option can be used to delete
    entire directory trees. By default, the -k option can't touch directories at all.
DEFAULTS.PROMPT_K_OPTION determines whether the user can see an interactive prompt and
    decide on a case-by-case basis which files and directories they want to delete.''',
    
    'num': '''The integer can be positive or negative. For example, 
"-2 <query>" would get the first two files alphabetically that satisfy <query>,
"-3 -s <query>" would get the three LARGEST files that satisfy <query>, and
"--3 -s <query>" would get the three SMALLEST files that satisfy <query>.''',
    
    'j': [
'''The -j and -y options are based on gorp.jsonpath, and specifically on
JsonPath(query, json).extract().
gorp.jsonpath has extensive documentation for programmatic applications,
    particularly parse_json_path, json_extract, JsonPath, Filter, and GlobalConstraint.
This documentation is concerned exclusively with using the -j option from the gorp
    interactive prompt or the command line.
Suppose you have the following two json documents:
~~~~~~~~~~~~~
bad_json.json
~~~~~~~~~~~~~
{
"a": false,
"b": "3",
"6": 7,
"9": "ball",
"jub":
      {
      "uy":
            [
            1,
            2,
            NaN
            ],
      "yu":
            [
                  [
                  6,
                        {
                        "y": "b",
                        "m8": 9
                        }
                  ],
            null
            ],
      "status": "jubar"
      },
"9\"a\"": 2,
"blutentharst":
      [
      "\n'\"DOOM\" BOOM, AND I CONSUME', said Bludd, the mighty Blood God.\n\t",
      true
      ]
}
~~~~~~~~~~~~~
J OPTION EXAMPLES
~~~~~~~~~~~~~
$ python gorp.py
############
## FINDING THE CHILDREN OF A KEY/ARRAY INDEX
############
gorp> -j -n 'jub~~@status' /bad_json.json # "A~~@B" means "A, then A's child B"
        # By default, keys must be matched exactly; later we'll see how to do regex
            # matching of keys.
        # So we look for the key 'jub', and then search for the key 'status' among its
            # children.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'status'): 'jubar'
    }
}
############
## CONSTRAINING VALUES ASSOCIATED WITH KEYS/INDICES
############
gorp> -j -n '9vvball' /bad_json.json # Everything after the 'vv' is a filter on values;
                # everything before the 'vv' is a filter on keys.
                # So this is looking for the key '9', matched to a value that contains
                    # the regex 'ball'.
                # Note that string matching on values is always based on regexes.
                # The next '~~@' or '~~^' or '~~' for path splitting will end the
                # value filter.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('9',): 'ball'
    }
}''',

'''############
## MATHEMATICAL EXPRESSIONS
############
gorp> -j -n 'jub~~@uy~~@nn1:' /bad_json.json # the 'nn' flag turns on "math mode".
                # In "math mode", for example "0" is read as the integer 0,
                # "3+0.5" is read as 3.5, and "x+3" is read as function(x) { x + 3 }.
                # See math_eval.compute.__doc__ for more information.
                # While in math mode, we can use start:stop:step
                # notation to make IntRange objects, which match all integers in 
                # range(start, stop, step). 1 is the default step, 0 the default start.
                # But what's the stop for this range ('1:')?
                # It's infinite! So basically this is just shorthand for
                # "match any key or array index that's an integer >= 1".
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'uy', 1): 2,
    ('jub', 'uy', 2): nan
    }
}
############
## DEFINING STRINGS IN A MATH EXPRESSION
############
gorp> -j -n 'jub~~@uy~~@nn:vvnnstr(x)[0]==`n`' /bad_json.json
                # the 'nn' flag for math mode
                # has to be called separately for the value filter and the key filter.
                # Also, you can define strings in math mode by surrounding them in ``.
                # So in this case, we're looking for children of bad_json['jub']['yu']
                # such the key is any array index ('nn:') (but not a dict key)
                # and the stringified value begins with an 'n'.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'uy', 2): nan
    }
}''',

'''############
## INEXACT MATCHES ON KEYS (WRONG)
############
gorp> -j -n '^\d+$' /bad_json.json # this is a regex match on keys; 
                                   # it doesn't work by default
                                   # the -n option is used to show the paths followed.
ALERT: It looks like you may have tried to match keys with regular expressions
['\\\\d'] while not in fuzzy_keys mode. Did you intend this?
0 files
{
}
############
## INEXACT MATCHES ON KEYS (RIGHT)
############
gorp> -j 'zz^\d+$' /bad_json.json # zz turns on "fuzzy" matching of keys, 
                                  # so you can use regexes to search for keys
    # In this case, we're looking for keys at the root level of bad_json that match the
    # regex '^\d+$', i.e., they are strings containing exactly one digit 0-9.
1 files
{
'C:\\Users\\mjols\\Python39\\bad_json.json':
    {
    ('6',): 7,
    ('9',): 'ball'
    }
}''',

'''############
## USING FILTERS TO MAKE ASSERTIONS ("CHECK")
############
gorp> -j 'jub~~@yu~~uy' /bad_json.json 
# As before, the ~~@ means "descend to children".
# But what does the '~~' do?
    # Here we will introduce the concept of "filter layers", which are fundamental
        # to gorp.jsonpath.
    # Each jsonpath is divided into "layers", each of which act on a different
        # level of the iterable.
    # The layers are separated by '~~@', '~~^', and '~~}' (we'll get to the other
        # two later).
    # Within a layer of a jsonpath, you can have multiple filters, each applying
        # constraints to the json.
    # Each filter in a layer is separated from the others in its layer by '~~'.
    # The last filter in a layer is the one that we descend from; the others just
        # act as "checks" that make assertions about what the json contains.
    # So in this example, we look for 'jub' in the top level of bad_json,
        # and then check for both 'yu' and 'uy' among its children.
    # If the children of 'jub' contain both 'yu' and 'uy', we return ('jub', 'uy').
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'uy'):
        [
        1,
        2,
        nan
        ]
    }
}
############
## RECURSIVE SEARCH (KEEP DESCENDING TIL YOU FIND A MATCH)
############
gorp> -j -n '..~~@zz[5-8]' /bad_json.json # '..' turns on recursive search.
                # While recursive search is active, we keep looking deeper and
                # deeper in bad_json until we find a match, in this case any string
                # representing a digit from 5 to 8 inclusive.
                # Once a match is found, recursive search is turned off.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'yu', 0, 1, 'm8'): 9,
    ('6',): 7
    }
}''',

'''############
## MULTIPLE CONSTRAINTS ON A SINGLE VALUE: ';;' FOR LOGICAL "OR"
############
gorp> -j -n '6;;baz;;foo' /bad_json.json # the ';;' separates a list of options
            # within a single filter. So now we're looking for keys at the top level
            # that match one of '6', 'baz', or 'foo' (exactly, because no 'zz' flag).
            # It's OK that 'baz' and 'foo' aren't among the keys; we just match '6'.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('6',): 7
    }
}
############
## MULTIPLE CONSTRAINTS ON A SINGLE VALUE: '&&' FOR LOGICAL "AND"
############
gorp> -j -n 'zzfoo&&bar&&baz' /bad_json.json # the '&&' works like ';;', except instead
                    # of a key having to match *one* of the options separated by '&&',
                    # it has to match *all* of them. So in this case, we could only
                    # match a key that contains ALL of the regexes "foo", "bar", "baz",
                    # like the string "barfoobaz".
0 files
{
}
gorp> -j -n '6&&baz&&foo' /bad_json.json # WHOOPS! The '&&' for bundling conditions only
                    # works if we use the 'zz' flag to invoke fuzzy key matching.
Traceback (most recent call last)
...
gorp.jsonpath.aggregate.JsonPathError: When not in fuzzy_keys mode, only IntRange slicers and ints are allowed as key tests.''',

'''############
## GlobalConstraints FOR ALLOWING COMPARISONS OF TWO OR MORE KEY-VALUE PAIRS
############
gorp> -j -n 'ggjubvvnn str(x[`6`]) <= x[`9`] ~~@status' /bad_json.json
        # the "gg" flag means that everything between the "gg" and the end of the query
        # or the next '~~', '~~@', or '~~^' is a GlobalConstraint, not a Filter.
        # GlobalConstraints, unlike Filters, place constraints on the iterable as a
        # whole, rather than on individual key-value pairs.
        # The constraint on the iterable as a whole comes after the 'vv', and the keys
        # that the GlobalConstraint matches come before hand.
        # So in this example, we want to descend from the top-level "jub" to "status",
        # but only if str(bad_json['6']) <= bad_json['9'].
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'status'): 'jubar'
    }
}
############
## REGEX MATCHING IN A MATH EXPRESSION
############
gorp> -j -n 'ggvvnn str(x[`b`])=~`^\d` ~~zz\dvvnnx<4' /bad_json.json
        # While in "math mode", the binary operator "=~" means "contains pattern".
        # So 'x[`b`]=~`^\d`' means we're asserting that bad_json['b'] starts with a 
        # digit.
        # Notice that the GlobalConstraint doesn't have any keys; it's just applying a
        # constraint to the iterable as a whole.
        # Since the GlobalConstraint is satisfied (bad_json['b'] is '3'),
        # we move on to the next top-level constraint, which looks for a key containing
        # a digit ("zz\d") with a value less than 4 ("vvnnx<4").
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('9"a"',): 2
    }
}''',

'''############
## REVERSING SELECTIVITY (WHAT IF YOU WANT A CONSTRAINT TO *NOT* BE SATISFIED?)
############
gorp> -j -n 'zz!!\dvvnn:~~@!!yu' /bad_json.json # '!!' is a flag that reverses the
    # selectivity of a match. Subsequent uses of '!!' toggle the flag on and off.
    # in this case, '!!' toggles reverse_selectivity on and then off again.
    # reverse_selectivity always works for values, but it only affects key matching
    # if the 'zz' flag has been used to turn on fuzzy key matching.
    # So in this case we look for a key-value pair such that the key DOESN'T contain a
    # digit and the value ISN'T a positive integer, then turn reverse_selectivity off 
    # again, and look for a key that contains the regex 'yu'.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'yu'):
        [
            [
            6,
                {
                'y': 'b',
                'm8': 9
                }
            ],
        None
        ]
    }
}
############
## FINDING THE PARENTS (AND OTHER ANCESTORS) OF A KEY/ARRAY INDEX
############
gorp> -j -n '..~~@zz^(?i)[a-z]+\d$~~^^' /bad_json.json
        # finally, we reach an explanation for the "~~^" path splitter.
        # "~~"+"^"*n means "ascend n times", so "~~^" means "ascend to parent",
        # "~~^^" means "ascend to grandparent, and so forth.
        # So here we're recursively searching for a key that contains any number of
        # ASCII letters (case-insensitive) followed by a single digit,
        # and then return the grandparents of those keys.
        # Since "m8" meets this description, and "yu" is its grandparent, we get
        # ('jub', 'yu') as the final path.
1 files
{
'C:\\Users\\mjols\\Python39\\gorp\\bad_json.json':
    {
    ('jub', 'yu'):
        [
            [
            6,
                {
                'y': 'b',
                'm8': 9
                }
            ],
        None
        ]
    }
}''',

'''############
## CALCULATING AGGREGATE FUNCTIONS AT VARIOUS LEVELS OF GRANULARITY
############
Consider a new JSON file, baseball.json.
{'foo':
    {'alice': 
        {'hits': [3, 4, 2, 5], 'at-bats': [4, 3, 3, 6]},
     'bob': 
        {'hits': [-2, 0, 4, 6], 'at-bats': [1, 3, 5, 6]}
    },
'bar': 
    {'carol': 
        {'hits': [7, 3, 0, 5], 'at-bats': [8, 4, 6, 6]},
     'dave': 
        {'hits': [1, 0, 4, 10], 'at-bats': [1, 3, 6, 11]}
    }
}
gorp> -j -n 'zz~~@~~@.*AGG sum BY :' /baseball.json
    # the "AGG sum BY :" at the end of the query means that we sum up all the
    # numbers we found, grouped by each distinct path (":" means all of it).
    # So we're aggregating hits and at-bats separately by player-team combo.
1 files
{
'C:\\Users\\mjols\\Python39\\gorpy\\gorp\\testDir\\walnut\\baseball.json':
    {
    ('bar', 'carol', 'at-bats'): 24,
    ('bar', 'carol', 'hits'): 15,
    ('bar', 'dave', 'at-bats'): 21,
    ('bar', 'dave', 'hits'): 15,
    ('foo', 'alice', 'at-bats'): 16,
    ('foo', 'alice', 'hits'): 14,
    ('foo', 'bob', 'at-bats'): 15,
    ('foo', 'bob', 'hits'): 8
    }
}
gorp> -j -n 'zz~~@~~@hitsAGG sum(x)/len(x) BY 0' /baseball.json
    # average hits grouped by team (could use 'avg' instead of 'sum(x)/len(x)')
1 files
{
'C:\\Users\\mjols\\Python39\\gorpy\\gorp\\testDir\\walnut\\baseball.json':
    {
    ('bar',): 3.75,
    ('foo',): 2.75
    }
}
~~~~~~~~~~~~~~~
END OF EXAMPLES
~~~~~~~~~~~~~~~
This concludes our overview of gorp.jsonpath syntax.
We've at least touched on all of the key features, the most important of which are:
    - 'vv' to separate key constraints from value constraints.
    - 'nn' to turn on 'math mode' (see math_eval.compute.__doc__ for more info).
    - 'zz' to allow regex matching of keys (by default keys must be matched exactly).
    - '..' to turn on recursive search.
    - 'gg' to create GlobalConstraints that allow comparisons of multiple values in the
        same iterable.
    - '~~@' and '~~^' to get children and parents, respectively .
    - '!!' to reverse the selectivity of key and value matching.
    - 'AGG<function>BY<int/slice>' to calculate aggregates with grouping.'''
    ]
}