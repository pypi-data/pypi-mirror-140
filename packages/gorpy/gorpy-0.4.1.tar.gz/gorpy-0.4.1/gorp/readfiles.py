'''Welcome to the gorp prompt.
- The general query format is 
    <options> '<pattern>' /<directory or filename>, 
    followed by any number of 
    <options> '<pattern>' subqueries separated by "-}}" delimiters.
- You can exit at any time by entering 'e','q','quit', or 'exit'.
- Enter "options" or 'o' for a list of gorp's optional arguments.
- You can display the working directory with 'd' or 'dir', change the working
    directory with 'cd <new directory name>', and display the contents of the
    working directory with 'ls'.
- You can write the results of a query to a JSON or YAML file by terminating 
    the query with " -}} -w '<name of file to write to>'.
- You can also supply a numeric argument to limit the size of the resultset.
- If you want more extensive documentation on any option(s) just type
    "doc (any number of options separated by spaces)" 
    and gorp will display some documentation on each option you named.
- To change how some options (currently just the -u, -k, and -pdf options) 
    behave, and to see if any text files found have bad encodings, enter 
    "DEFAULTS".
- You can reset all the default behaviors to their original values with 
    "DEFAULTS.reset()".
- You can set a DEFAULT option as well, e.g. "DEFAULTS.PROMPT_K_OPTION = True"
- Finally, not all text files will be read by default by gorp. To change which
    file extensions are treated as text files, see site-packages/gorp/utils.py.
- "gorp doc f" will show a list of "text-type-files".
'''
from gorp.utils import *
from gorp.gprint import gprint


helpstring = __doc__


class GorpSession:
    '''This is the normal high-level interface for gorp. A typical usage in a
programmatic context (i.e., not from the command line) is something like this:

>>> with GorpSession(print_output = False) as session: 
    # sessions are context managers like file handles from open()
    session.receive_query("help")
    session.receive_query("DEFAULTS")
    session.receive_query("cd directory/of/interest")
    session.receive_query("some query")
    blah = session.resultset 
    # the resultset of the last query (other than cd/ls/help)
>>> session2 = GorpSession()
>>> session2.receive_query("another query")
>>> session2.close()
    '''
    def __init__(self, print_output = True):
        self.old_queries = {}
        self.print_output = print_output 
        # if True, print output instead of returning it
        self.isclosed = False
        
    @property
    def resultset(self):
        if not self.old_queries:
            return None
        return self.old_queries['prev'].resultset
    
    @property
    def last_query(self):
        if not self.old_queries:
            return None
        return self.old_queries['prev'].parsedQuery
        
    def _Gorp(self, parsedQuery, resultset = None):
        assert not self.isclosed, "A closed GorpSession cannot receive queries."
        new_handler = GorpHandler(parsedQuery, self, resultset, self.print_output)
        new_handler.search()
        new_handler.process_final_resultset()
        self.old_queries[f'q{len(self.old_queries)+1}'] = new_handler
        self.old_queries['prev'] = new_handler
    
    # The __enter__ and __exit__ methods allow a class to be used as a 
    # context manager so that I can use the "with" statement.
    def __enter__(self):
        return self
    def close(self):
        '''Removes data associated with the session and writes DEFAULT_OPTIONS
    and pdf_textcache to file.'''
        del self.old_queries
        pdf_textcache = globals().get('pdf_textcache')
        if pdf_textcache is not None:
            pdf_textcache.dump(os.path.join(gorpdir, "pdf_textcache.json"))
            del pdf_textcache
        with open(default_options_fname, 'w') as f:
            DEFAULT_OPTIONS['bad_text_files'] = list(bad_text_files)
            gprint(DEFAULT_OPTIONS, f)
        self.isclosed = True
    def __exit__(self, type, value, traceback):
        self.close()
        # the type, value, and traceback args of the __exit__ method capture 
        # and display any tracebacks that occur, in addition to calling all 
        # this cleanup code.
        
            
    def receive_query(self, query):
        assert not self.isclosed, "A closed GorpSession cannot receive queries."
        GorpLogger.info(f"In GorpSession.receive_query, query = {query}")
        if not query:
            return
        elif query in ['h','help', '?']:
            print(helpstring)
        elif query[:3] == 'doc':
            query = re.findall('[a-z]+', query[3:].lower())
            if not query:
                print(helpstring)
                return
            from .option_docs import option_descriptions, detailed_option_descriptions
            for opt in query:
                if opt in option_descriptions:
                    print(option_descriptions[opt])
                else:
                    print(f"No '{opt}' option currently exists for gorp.") 
                if opt in detailed_option_descriptions:
                    description = detailed_option_descriptions[opt]
                    if isinstance(description, str):
                        print(description)
                    else:
                        for ii, section in enumerate(description):
                            print(section)
                            if ii < len(description) - 1:
                                show_more = input("===========\nSHOW MORE?\n")
                                if show_more == 'q':
                                    break
                print()
        elif query in ['o', 'options']:
            from gorp.option_docs import option_descriptions
            gprint(option_descriptions)
        elif query in ['dir','d']:
            print(os.getcwd())
            return
        elif query[:2].lower() == 'cd':
            newdir = re.sub("^\s*cd\s*",'',query)
            newdir = re.sub('\'|"','',newdir)
            try:
                if newdir:
                    os.chdir(newdir)
                else:
                    print(os.getcwd())
            except FileNotFoundError:
                print(f"The directory {repr(newdir)} was not found.")
        elif query[:2].lower() == 'ls':
            newdir = re.sub("^\s*ls\s*",'',query)
            newdir = re.sub('\'|"','',newdir)
            try:
                if newdir:
                    gprint(os.listdir(newdir))
                else:
                    gprint(os.listdir())
            except FileNotFoundError:
                print(f"The directory {repr(newdir)} was not found.")
        elif query[:8] == "DEFAULTS":
            query = query[8:]
            DEFAULT_OPTIONS = globals()['DEFAULT_OPTIONS']
            if not query:
                gprint(DEFAULT_OPTIONS)
            elif query[0] == '.':
                query = query[1:]
                if query == 'reset()':
                    # reset the DEFAULT_OPTIONS to whatever they would normally be
                    DEFAULT_OPTIONS = INITIAL_DEFAULT_OPTIONS.copy()
                elif query in DEFAULT_OPTIONS:
                    gprint(DEFAULT_OPTIONS[query])
                elif "=" in query:
                    def_opt, new_val = [x.strip() for x in re.split("(?<!=)=(?!=)", query)]
                    if def_opt in DEFAULT_OPTIONS:
                        DEFAULT_OPTIONS[def_opt] = compute(new_val)
                    else:
                        print("No such option in DEFAULT_OPTIONS.")
                globals().update(DEFAULT_OPTIONS)
                globals()['DEFAULT_OPTIONS'] = DEFAULT_OPTIONS
        elif re.match("\s*-g", query):
            # -g option, read in a gorp script and run its commands.
            script_name = re.sub("\s*-g\s*", '', query) 
            with open(script_name) as f:
                queries = re.split('\r?\n', f.read())
                for script_query in queries:
                    self.receive_query(script_query)
        else: # it's either a normal Gorp query or syntactically invalid
            splitquery = [x.strip() for x in query.split('-}}', 1)]
            resultset = None
            if splitquery[0] in self.old_queries:
                resultset = self.old_queries[splitquery[0]].resultset
                if len(splitquery) == 1: 
                    # the user just wanted old query results displayed again.
                    gprint(resultset)
                    return
                else:
                    query = splitquery[1]
            parsedQuery = re.findall(queryParserRegex, query.strip())
            if not len(parsedQuery):
                print("Invalid query.")
                return
            before_q_option = False
            before_q_subqueries, after_q_subqueries = [], []
            for subquery in reversed(parsedQuery):
                if before_q_option:
                    before_q_subqueries.append(subquery)
                else:
                    after_q_subqueries.append(subquery)
                if 'q' in subquery[0]:
                    # Split the query into two queries to be unioned,
                    # the second starting with the -q option
                    before_q_option = True
            before_q_subqueries = before_q_subqueries[::-1]
            # these were iterated through in reverse order, so we need to reverse them
            # again
            after_q_subqueries = after_q_subqueries[::-1]
            GorpLogger.debug(before_q_subqueries, after_q_subqueries)
            if '-sed' in after_q_subqueries[-1][0]:
                # this implements linux "sed" basically
                # "(<subqueries> -}})? <options> -sed 'regex//repl' /dirname" is equivalent 
                # to "(<subqueries> -}})? <options> 'regex' /dirname -}} -u 'x sub '`regex//repl`'"
                sed_options, regex_repl, sed_dirname = after_q_subqueries[-1]
                new_sed_options = sed_options.replace("-sed", "")
                Regex, Repl = regex_repl.split('//')
                after_q_subqueries[-1] = (new_sed_options, Regex, sed_dirname)
                if '-i' in new_sed_options:
                    # need to ensure that the re.sub update is also
                    # case-insensitive
                    regex_repl = '(?i)' + regex_repl
                after_q_subqueries.append(('-u', f"x sub `{regex_repl}`", ''))
                GorpLogger.debug(after_q_subqueries)
            if before_q_subqueries:
                #after_query_as_string = ''.join(''.join(q) for q in after_q_subqueries)
                # get the union of the resultsets from the two GorpHandlers created here
                # print(before_q_subqueries)
                first_handler = GorpHandler(before_q_subqueries, 
                                            self, 
                                            resultset, 
                                            self.print_output)
                first_handler.search()
                GorpLogger.debug(first_handler.resultset)
                # print(after_q_subqueries)
                second_handler = GorpHandler(after_q_subqueries,
                                             self,
                                             None,
                                             self.print_output)
                second_handler.search()
                # print(second_handler.resultset)
                numfiles = len(first_handler.resultset) + len(second_handler.resultset)
                first_summary = first_handler.readers[-1].summary
                second_summary = second_handler.readers[-1].summary
                if isinstance(first_summary, list) and isinstance(second_summary, list):
                    # both queries used the -s option to get file sizes.
                    first_size = byteform_to_num(first_summary[1])
                    second_size = byteform_to_num(second_summary[1])
                    second_handler.readers[-1].summary = [f"{numfiles} files", 
                                             format_bytes(first_size+second_size)]
                else:
                    second_handler.readers[-1].summary = f"{numfiles} files"
                unioned_resultset = {}
                # we want not just the union of the sets of files in each resultset,
                # but also the union of the lines found for each file, in case
                # the two resultsets overlap
                for fname in second_handler.resultset:
                    unioned_resultset[fname] = second_handler.resultset[fname]
                    if fname in first_handler.resultset:
                        if not isinstance(first_handler.resultset[fname], dict):
                            continue # it might be a number or a tuple
                        unioned_resultset[fname].update(first_handler.resultset[fname])
                for fname in first_handler.resultset:
                    if fname not in second_handler.resultset:
                        unioned_resultset[fname] = first_handler.resultset[fname]
                second_handler.resultset = unioned_resultset
                second_handler.process_final_resultset()
                self.old_queries[f'q{len(self.old_queries)+1}'] = second_handler
                self.old_queries['prev'] = second_handler
            else: # only one query, no -q option
                self._Gorp(after_q_subqueries, resultset)

# should think about using argparse to help with the documentation of the gorp options

import_warnings = {
    'yaml': [False, "PyYAML (imported by 'import yaml') is required for the 'y' option and some nonessential aspects of the 'e' and 'w' options. Try installing with 'pip install pyyaml'"
    ],
    'docx': [False, "python-docx (imported by 'import docx') is required for the 'docx' option, which allows reading of Word documents. Try installing with 'pip install python-docx'.\nDO NOT USE 'pip install docx'; that is a DIFFERENT LIBRARY."
    ],
    'pdfminer': [False, "pdfminer.six (imported by 'import pdfminer') is required for the 'pdf' option. Try installing with 'pip install pdfminer.six'.\nDO NOT USE 'pip install pdfminer'; that is a DIFFERENT LIBRARY."
    ],
    'sortedcollections': [False, "sortedcollections (imported by 'import sortedcollections') is required for the 'pdf' option. Try installing with 'pip install sortedcollections'."
    ],
    'openpyxl': [False, "openpyxl (imported by 'import openpyxl') is required for the 'xl' option, which allows reading of Excel files. Try installing with 'pip install openpyxl'."
    ],
    'lxml':   [False, "lxml (imported by 'import lxml') is required for the 'x' option, which enables XPath access to HTML and XML files. Try installing it with 'pip install lxml'."
    ],
}

def warn_first_import_error(package):
    '''For errors that the user should be alerted of exactly once, checks if they've
    already been alerted, and if not, prints the warning.'''
    if not import_warnings[package][0]:
        import_warnings[package][0] = True
        print(import_warnings[package][1])


queryParserRegex = re.compile(("\s*(?P<options>(?:-(?:[a-zA-Z]+"
                               r"(?:[><=]=?[\d\.,-]+(?:[gmk]?b(?:ytes)?)?)?"
                               # allows filtering of mod times and file sizes
                               "|-?\d+)\s+)*)" # num option to limit # results
                               r"'(?P<text>(?:[^']|(?<=\\)')*?)(?<!\\)'"
                               # the text regex allows recognition of "'" in the regex
                               # itself, so long as they're preceded by r'\\'
                               "(?:\s+/(?P<fname>[^}\t]+?)"
                               "(?:\s+-}} |\s*$))?"), re.I) 
# note that the last part of the regex (the -}} pipe splitter) greedily consumes
# spaces after the fname. This actually works out fine because neither filenames nor
# directory names can be terminated by spaces.

w_query_splitter = " -}} \s*(?:-y)?\s*-w\s+(?:-y)?\s*'(.+)'"

blaquery = (" -f -r 'foo' /jfur/runj roo-jun  -}}"
           " -i     -p -m -22 'run\\'ru' -}}\t-j 'rej\\'wn~~@nn1~3' -}} 'j'")

class GorpHandler:
    '''Handles a single query, including generating the initial resultset, 
    piping to subqueries as needed, and any optional post-processing like 
    the -k and -p options.
GorpHandlers should only be created by a GorpSession.'''
    def __init__(self, parsedQuery: list,  session: GorpSession, resultset = None, print_output = True):
        self.print_output = print_output
        self.parsedQuery = parsedQuery
        self.session = session
        GorpLogger.info(f"In GorpHandler.__init__, parsedQuery = {self.parsedQuery}")
        self.readers = []
        self.level = 0
        self.options = [set(re.findall("-(\S+)", x[0].strip().lower())) for x in self.parsedQuery]
        # print(f'{self.options = }')
        self.all_options = set(opt for opts in self.options for opt in opts)
        self.regexes = [x[1].replace('\\\'', '\'') for x in self.parsedQuery]
        self.s = [x for x in self.all_options if x[0] == 's' and x != 'sed']
        self.m = [x for x in self.all_options if x[0] == 'm' and x != 'mv']
        self.k = 'k' in self.all_options
        self.w = 'w' in self.options[-1]
        self.u = 'u' in self.options[-1]
        self.z = any(x[0]=='z' for x in self.options[-1])
        self.mv = 'mv' in self.options[-1]
        if self.w or self.u or self.z or self.mv:
            if self.z:
                import zipfile
                if 'zb' in self.options[-1]:
                    self.zip_compression = zipfile.ZIP_BZIP2
                elif 'zl' in self.options[-1]:
                    self.zip_compression = zipfile.ZIP_LZMA
                else:
                    self.zip_compression = zipfile.ZIP_STORED
                    # this is the default; it means no compresssion
                # may also add support for gzip, but only lzma and bzip are in
                # the standard Lib.
            if self.u:
                self.replacement_func = compute(self.regexes[-1])
            self.options = self.options[:-1]
            self.regexes = self.regexes[:-1]
            GorpLogger.debug((
                   "in self.w or self.u or self.z branch of GorpHandler.__init__,"
                   f"\noptions = {self.options} and regexes = {self.regexes}"
                   f"and replacement_func = compute({self.regexes[-1]})"))
        self.p = 'p' in self.all_options
        self.t = 't' in self.all_options
        self.f = 'f' in self.options[-1]
        self.l = 'l' in self.options[-1]
        self.c = 'c' in self.options[-1]
        self.h = 'h' in self.options[-1] 
        self.n = 'n' in self.options[-1]
        # now read the files!
        if resultset is None:
            # the resultset has to be generated by reading files in the directory
            # named by the first subquery.
            self.firstGorp, self.gorps = self.parsedQuery[0], self.parsedQuery[1:]
            self.dirName = os.path.abspath(self.firstGorp[2])
            self.readers.append(FileReader(self.options[0], 
                                        self.regexes[0], 
                                        self.dirName,
                                        self))
            self.resultset = self.readers[-1].resultset
        else:
            self.dirName = os.getcwd()
            self.resultset = resultset
            
    def refine(self):
        '''Passes the current resultset of the GorpHandler to the next 
    FileReader in sequence, which further winnows down the resultset.
    The GorpHandler's resultset is then set to that FileReader's resultset.'''
        # print(self.resultset)
        if self.resultset and ('d' not in self.options[self.level]):
            resultset_dirs_expanded = []
            for fname in self.resultset:
                if os.path.isdir(fname):
                    new_files = (os.path.join(fname, x) for x in os.listdir(fname))
                    resultset_dirs_expanded.extend(new_files)
                else:
                    resultset_dirs_expanded.append(fname)
        else:
            resultset_dirs_expanded = self.resultset
        # print(resultset_dirs_expanded)
        curReader = FileReader(self.options[self.level], 
                               self.regexes[self.level], 
                               resultset_dirs_expanded,
                               self)
        self.readers.append(curReader)
        self.resultset = curReader.resultset
        
    def search(self):
        '''Use all of this GorpHandler's FileReaders to completely winnow
down the resultset'''
        for ii, (opts, regs) in enumerate(zip(self.options, self.regexes)):
            self.level = ii
            self.refine()            

    def process_final_resultset(self):
        if self.print_output:
            print(self.readers[-1].summary)
        if self.p:
            gprint(self.resultset)
            user_decision = 'y'
            if len(self.resultset) > 5:
                    user_decision = input(f"This resultset includes {len(self.resultset)} files. Are you sure you want to open all of them (y/n)?\n")
            if user_decision == 'y':
                # open each file with default application
                for filename in self.resultset:
                    run_file_default_app(filename)
        if self.u and not (self.options[-1] & {'x', 'pdf', 'docx', 'xl', 'tab'}):
            # the -u option may evenutally be implemented for updating at least some of 
            # PDF's, Word Documents, Excel files, and (X|HT)ML files, but for now it's
            # limited to JSON, YAML, and plaintext documents.
            self.update(self.replacement_func,
                        ask_permission = PROMPT_U_OPTION,
                        overwrite =  U_OPTION_OVERWRITES)
        if self.k:
            # delete files, pending user approval
            from .k_option_del_files import killGorp
            killGorp(self.resultset,
                     ask_permission = globals()['PROMPT_K_OPTION'],
                     allow_remove_trees = globals()['ALLOW_REMOVE_TREES'])
        if self.w: #used -w option, write results to files
            write_to_name = self.parsedQuery[-1][1] # the syntax is ...-}} -w 'filename'
            if 'y' in self.options[-1] or re.search('\.ya?ml$', write_to_name.lower()): 
                # the -y option means 'write to yaml' rather than 'parse yaml' when 
                # used with -w, and of course if the chosen filename has a 'yaml'
                # or 'yml' extension that's a sure sign we should use yaml.
                write_to_name = increment_name(ext_checker(write_to_name,'yaml'))
                try:
                    import yaml
                    with open(write_to_name,'w') as f:
                        yaml.safe_dump(self.resultset,f)
                    # the yaml.dump() function creates a file with metadata on Python 
                    # objects other than normal lists and dicts, such that
                    # the original Python objects could be completely reconstituted
                    # by parsing the YAML file with yaml.load() (but NOT yaml.safe_load)
                    # Since this function doesn't care about preserving arbitrary Python
                    # objects, and the class metadata made by yaml.dump() breaks
                    # yaml.safe_load(), I have to use yaml.safe_dump(),
                    # which, e.g., coerces dict-likes to dicts and tuples to lists.
                except ImportError:
                    warn_first_import_error('yaml')
            else: # write to a JSON file
                write_to_name = increment_name(ext_checker(write_to_name,'json'))
                with open(write_to_name,'w') as f:
                    json.dump(self.resultset,f, indent = 4)
        if self.z: # collect all files into a ZIP file at target location
            import zipfile
            from gorp.zip_utils import make_relpaths
            write_to_name = increment_name(ext_checker(self.parsedQuery[-1][1], 'zip'))
            curdir = os.getcwd()
            try:
                zf = zipfile.ZipFile(write_to_name, 
                                 mode = 'w', # 'x' mode is like 'w', but raises error
                                             # if file already exists
                                 compression = self.zip_compression
                                 )
                if not self.resultset:
                    files = []
                elif len(self.resultset) > 1:
                    files, commondir = make_relpaths(self.resultset)
                    os.chdir(commondir)
                elif len(self.resultset) == 1:
                    files = [os.path.basename(f) for f in self.resultset]
                    commondir = [os.path.dirname(f) for f in self.resultset][0]
                    os.chdir(commondir)
                    # make_relpaths(files) finds the longest path shared by
                    # all paths in files, and truncates all those files to
                    # remove the redundant common part.
                    # But if there's only one file, this chops off everything.
                for fname in files:
                    zf.write(fname)
            finally:
                os.chdir(curdir)
                zf.close()
        if self.mv: # collect all files, copy them into a directory
            pass
        if not (self.w or self.k or self.p or self.t or self.u):
            if self.s or self.m:
                pass
            elif any(opt in self.options[-1] for opt in ('a', 'f', 'd', 'l')):
                self.resultset =  list(self.resultset.keys())
            elif self.c:
                fileLineCounts={}
                for key in self.resultset:
                    fileLineCounts[key] = len(self.resultset[key])
                self.resultset =  fileLineCounts
            elif self.h:
                if self.readers[-1].tab or self.readers[-1].xl:
                    raise NotImplementedError("The '-tab' and '-xl' options cannot be used in combination with the '-h' option for combining results from all files without filenames.")
                if self.n: 
                    linelistWithNums={}
                    for key in self.resultset:
                        linelistWithNums.update(self.resultset[key].items())
                    self.resultset =  linelistWithNums
                else:
                    linelist=[]
                    for key in self.resultset:
                        linelist.extend(self.resultset[key].values())
                    self.resultset =  linelist
            elif not (self.n or self.readers[-1].tab or self.readers[-1].xl):
                # DataFrames can't really be conveniently displayed except by
                # their default string representations.
                self.resultset = {fname: list(lines.values()) \
                                        for fname, lines in self.resultset.items()}
            if self.print_output:
                gprint(self.resultset)
            else:
                return self.resultset

    def update(self, replacement_func, ask_permission = True, overwrite = True):
        '''replacement_func: a function of one argument.
ask_permission: bool, default True. 
    If True, gives an interactive prompt so that the user can manually
    choose which changes in the resultset should be made.
overwrite: bool, default True. If False, create a new file rather than 
    overwriting the original.
If the last FileReader in this GorpHandler was looking at (file|dir)names, this
will rename all the files and directories in the resultset, pending user input.
Otherwise, this will apply replacement_func to all the locations in those 
    files that were found by the query.'''
        from .jsonpath import JsonPathError, compressed_obj_repr
        def mutate_file(obj, path, func, ask_permission = False, **kwargs):
            '''Mutates a nested iterable object in-place by applying func to obj[path]. 
    obj: an object containing arbitrarily nested iterables.
    path: a tuple of keys or indices to follow through the object.
    func: a function to apply to the child found at the end of the path.
    ask_permission: if True, ask before changing the node. Useful when this 
    is called repeatedly by other functions.
        Returns: None.'''
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
                        next_decision = input("Do you want to stop editing this file? (y/n) ")
                        if next_decision == 'y':
                            raise JsonPathError("mutate_file halted at user request.")
                        return obj
                return out
            obj[path[level]] = mutate_file(obj[path[level]], 
                                           path, 
                                           func, 
                                           ask_permission,
                                           level = level+1)
            if (level != 0):
                return obj
        
        def mutate_file_repeatedly(obj, paths, func, ask_permission = False):
            '''See mutate_file. This applies the func to obj[path] for each path in 
paths (by which we mean line numbers, or (page, line) tuples, or json paths).'''
            for ii, p in enumerate(paths):
                if not is_iterable(p):
                    p = (p,)
                try:
                    mutate_file(obj, p, func, ask_permission)
                except Exception as ex:
                    if 'halted at user request' in repr(ex):
                        return False
                    raise JsonPathError(ex)
                if ask_permission and ii < len(paths)-1:
                    ask_permission = (input("There are {numpaths} locations in this file that may be changed. Do you still want to be asked permission? (y/n) ".format(numpaths= len(paths)-ii-1)) == 'y')
            return True
        
        for ii, (fname, paths) in enumerate(self.resultset.items()):
            if {'f', 'a', 'd'} & self.options[-1]:
                # these all look at (file|dir)names only, so the -u option with one of
                # these options should only change the (file|dir)name.
                new_fname = replacement_func(fname)
                decision = 'n'
                if ask_permission:
                    decision = input((f"{fname} will be renamed to {new_fname}."
                                      " Is that OK?\n"))
                if (not ask_permission) or (decision == 'y'):
                    try:
                        os.rename(fname, new_fname)
                    except Exception as ex:
                        raise ex
                        pass
            else:
                use_yaml = 'y' in self.options[-1]
                if use_yaml:
                    try:
                        import yaml
                    except:
                        warn_first_import_error('yaml')
                        use_yaml = False
                # process the text in fname in some appropriate way
                if ask_permission:
                    print(f"Now editing {fname}.")
                with open(fname) as f:
                    if 'j' in self.options[-1]:
                        processed_text = json.load(f)
                    elif use_yaml:
                        processed_text = list(yaml.safe_load_all(f))
                        is_single_doc = False
                        if len(processed_text) == 1:
                            processed_text = processed_text[0]
                            is_single_doc = True
                    else:
                        processed_text = re.split('\r?\n', f.read())
                edit_file = mutate_file_repeatedly(obj = processed_text,
                                       paths = paths,
                                       func = replacement_func,
                                       ask_permission = ask_permission)
                if edit_file:
                    if overwrite:
                        write_to_name = fname
                    else:
                        write_to_name = increment_name(fname)
                    with open(write_to_name, 'w') as f:
                        if 'j' in self.options[-1]:
                            json.dump(processed_text, f)
                        elif use_yaml:
                            if is_single_doc:
                                yaml.safe_dump(processed_text, f)
                            else:
                                yaml.safe_dump_all(processed_text, f)
                        else:
                            f.write('\n'.join(processed_text))
            if ask_permission  and ii < len(self.resultset)-1:
                ask_permission = (input(f"There are {len(self.resultset)-ii-1} files remaining that may be edited. Do you still want to be asked permission? (y/n) ") == 'y')
                if ask_permission:
                    quit_decision = input("Do you want to stop editing files? (y/n) ")
                    if quit_decision == 'y':
                        return
                    



def generateFileSet(fname: str, d = False, r = False):
    '''fname: the name of a file or directory.
d: Boolean. If true, only yield directories.
r: Boolean. If true, recursively search subdirectories of fname for files.
Returns: a generator that yields names of directories or files, as per d and r.
    '''
    fname = os.path.abspath(fname)
    if os.path.isfile(fname):
        yield fname
    else:
        if r:
            if d:
                for root, dirs, files in os.walk(fname):
                    root = os.path.relpath(root, fname)
                    if root == '.':
                        root = ''
                    GorpLogger.info(f"in generateFileSet (r and d), root = {root}")
                    for Dir in dirs:
                        yield os.path.join(root, Dir)
            else:
                for root, dirs, files in os.walk(fname):
                    root = os.path.relpath(root, fname)
                    if root == '.':
                        root = ''
                    GorpLogger.info(f"in generateFileSet (r and not d), root = {root}") 
                    for file in files:
                        yield os.path.join(root, file)
        else:
            for file in os.listdir(fname):
                GorpLogger.info(f"in generateFileSet (not r), file = {file}")
                if d and not os.path.isdir(os.path.join(fname, file)):
                    continue
                yield file



class FileReader:
    '''Handles a single subquery, filtering a set of files based on filenames or text
    matching a regex. These should only be created by a GorpHandler.

*options*: a tuple of options.

*regex*: a string (regex, gorp.jsonpath query, XPath, or CSS selector)

*files*: a list of files or filename.

*handler*: the GorpHandler that spawned it.'''
    def __init__(self, options, regex, files, handler: GorpHandler):
        # bad_text_files.add("rerjeu.2py")
        self.handler = handler
        self.options = options
        self.regex = regex

        self.a = ('a' in self.options)
        self.b = ('b' in self.options) # read raw bytes of any file
        if self.b:
            regex = regex.encode()
            self.regex = regex
        self.docx = ('docx' in self.options) and (not import_warnings['docx'][0])
        self.pdf = ('pdf' in self.options) and (not import_warnings['pdfminer'][0])
        self.xl = ('xl' in self.options) and (not import_warnings['openpyxl'][0])
        self.c = ('c' in self.options)
        self.d = ('d' in self.options)
        self.e = ('e' in self.options)
        self.f = ('f' in self.options)
        self.g = ('g' in self.options)
        self.h = ('h' in self.options)
        self.i = ('i' in self.options)
        self.j = ('j' in self.options)
        # self.k = ('k' in self.options) # a post-processing option used on the final resultset
        self.l = ('l' in self.options)
        self.m = [x for x in self.options if x[0] == 'm' and x != 'mv']
        if self.m:
            m = self.m[0]
            try:
                comparator, modtime = re.findall('([<>=]=?)(.+)', m)[0]
                compare_func = {**binops, '=': binops['==']}[comparator] 
                self.modtime_filter = lambda x: compare_func(str(x), modtime)
            except:
                self.modtime_filter = lambda x: True
        self.n = ('n' in self.options)
        self.o = ('o' in self.options)
        # self.p = ('p' in self.options) # see self.k comment
        # self.q = ('q' in self.options)
        self.r = ('r' in self.options)
        self.s = [x for x in self.options if x[0] == 's' and x != 'sed']
        if self.s:
            s = self.s[0]
            try:
                comparator, size = re.findall('([<>=]=?)(.+)', s)[0]
                size = byteform_to_num(size)
                compare_func = {**binops, '=': binops['==']}[comparator]
                self.size_filter = lambda x: compare_func(x, size)
            except:
                self.size_filter = lambda x: True
        # self.t = ('t' in self.options) # see self.k
        self.tab = ('tab' in self.options)
        # self.u = ('u' in self.options) # see self.k
        self.v = ('v' in self.options)
        self.w = ('w' in self.options)
        self.x = ('x' in self.options) and not import_warnings['lxml'][0]
        self.y = ('y' in self.options) and not import_warnings['yaml'][0]
        # self.z = ('z' in self.options) # see self.k
        # print(f'{self.m = }, {self.s = }, {self.r = }')
        
        self.numarg = None
        for opt in self.options:
            try:
                self.numarg = int(opt)
            except Exception as ex:
                # if not "invalid literal for int(" in repr(ex):
                    # GorpLogger.error(ex)
                continue
        
        if self.j or self.y or self.tab or self.xl:
            from .jsonpath import JsonPath
            self.jsonpath = JsonPath(self.regex)
            # print(self.jsonpath)
        else:
            self.jsonpath = None
        # print(files)
        if not isinstance(files, str): # files is a list of (file/dir)names
            self.dirName = ''
            self.files = files
        else: # files is a directory/filename
            if os.path.isdir(files): # gorp from a directory
                self.dirName = files
                self.files = generateFileSet(files, self.d, self.r)
            else:
                self.dirName = ''
                if self.e: 
                    # 'e' option means you read files in from a JSON/YAML file
                    use_yaml = get_ext(files) in {'yml', 'yaml'}
                    with open(files) as fhand:
                        if use_yaml:
                            try:
                                import yaml
                                self.files = yaml.safe_load(fhand)
                            except ImportError:
                                warn_first_import_error('yaml')
                        else:
                            self.files = json.load(fhand)
                else: # gorping a single file
                    self.dirName = ''
                    self.files = [files]
        
        self.resultset = {}
        
        if self.i:
            if self.o:
                def goodness_condition(line):
                    out = []
                    for x in line.split():
                        mtch = re.fullmatch(regex, x, re.I)
                        if mtch:
                            out.append(mtch.string)
                    return out
                self.goodness_condition = goodness_condition
                self.f_goodness_condition = lambda fname: re.fullmatch(regex,fname,re.I)
            else:
                self.goodness_condition = lambda line: re.search(regex,line,re.I)
                self.f_goodness_condition = lambda fname: re.search(regex,fname,re.I)
        else:
            if self.o:
                def goodness_condition(line):
                    out = []
                    for x in line.split():
                        mtch = re.fullmatch(regex, x)
                        if mtch:
                            out.append(mtch.string)
                    return out
                self.goodness_condition = goodness_condition
                self.f_goodness_condition = lambda fname: re.fullmatch(regex,fname)
            else:
                self.goodness_condition = lambda line: re.search(regex,line)
                self.f_goodness_condition = lambda fname: re.search(regex,fname)
        for fname in self.files:
            GorpLogger.info(f"In FileReader.__init__, fname = '{fname}'")
            self._single_file_gorp(fname)
            
        new_result_len = self.numarg
        if (not (self.s or self.m)) and (new_result_len is not None):
            # truncate the resultset to new_result_len
            if isinstance(self.resultset, dict):
                short_results = Orddict()
                for ii, elt in enumerate(self.resultset):
                    if new_result_len >= 0:
                        # add the first new_result_len elements of the
                        # resultset, when iterated through in the default order
                        if ii == new_result_len:
                            break
                        short_results[elt] = self.resultset[elt]
                    else:
                        # add the last new_result_len elements of the the
                        # resultset, when iterated through in the default order
                        if ii >= len(self.resultset) + new_result_len:
                            short_results[elt] = self.resultset[elt]
                self.resultset = short_results
            else:
                self.resultset = self.resultset[:new_result_len]
        if self.m and self.s: # get size and mod time of each file
            sizes = list(filter(lambda x: self.modtime_filter(x[1]) \
                                          and self.size_filter(x[2]),
                                [(f,
                                  last_mod_time(f, True), 
                                  os.path.getsize(f)) \
                                for f in self.resultset]))
            sizes.sort(key = lambda x: x[2], reverse = True)
            if new_result_len is not None: # truncate after sorting to get largest
                if new_result_len < 0:
                    sizes = sizes[new_result_len:]
                else:
                    sizes = sizes[:new_result_len]
            self.summary = [f"{len(sizes)} files", format_bytes(sum(x[-1] for x in sizes))]
            self.resultset = Orddict([(f, (str(mod), format_bytes(siz))) for f,mod,siz in sizes]) 
            # Orddict is just a normal dict for Python 3.7+, else a collections.OrderedDict
        elif self.m: # last mod time; not size
            modtime_d = list(filter(lambda x: self.modtime_filter(x[1]),
                                    [(f, last_mod_time(f,True)) \
                                    for f in self.resultset]))
            modtime_d.sort(key=lambda x: x[1], reverse=True)
            if new_result_len is not None: # truncate after sorting to get most recent
                if new_result_len < 0: # get OLDEST files
                    modtime_d = modtime_d[new_result_len:]
                else: # get NEWEST FILES
                    modtime_d = modtime_d[:new_result_len]
            self.resultset = Orddict((f, str(mod)) for f, mod in modtime_d)
            self.summary = f"{len(self.resultset)} files"
        elif self.s: # get size; not last mod time
            sizes = list(filter(lambda x: self.size_filter(x[1]),
                                [(f, os.path.getsize(f)) \
                                for f in self.resultset]))
            sizes.sort(key = lambda x: x[1], reverse = True)
            if new_result_len is not None: # truncate after sorting to get largest
                if new_result_len < 0: # get the new_result_len SMALLEST files
                    sizes = sizes[new_result_len:]
                else: # get new_result_len LARGEST files
                    sizes = sizes[:new_result_len]
            self.summary = [f"{len(sizes)} files", format_bytes(sum(x[-1] for x in sizes))]
            self.resultset = Orddict([(f, format_bytes(siz)) for f,siz in sizes])
        else:
            self.summary = f"{len(self.resultset)} files"
            
    def _single_file_gorp(self, rel_fname):
        '''Used by FileReaders to find matching text and filenames'''
        file = os.path.join(self.dirName,rel_fname)
        ext = get_ext(rel_fname)
        GorpLogger.info(f"In FileReader._single_file_gorp, rel_fname = {rel_fname}, file = {file}, ext = {ext}")
        if ext: # get_ext returns None for strings with no '.', like most dirnames
            ext = ext.lower()
        if self.a or self.d:
        # Interesting note: I thought I could save time by skipping the 
        # regex parsing if the regex was '.*' (since that matches every 
        # string including ''), but it was actually slower than before!
            if bool(self.f_goodness_condition(rel_fname)) ^ self.v:
                self.resultset.setdefault(file, 0)
            return
        elif self.b: # read any file's raw bytes
            if os.path.isdir(file):
                return
            with open(file, 'rb') as f:
                text = f.read()
            lines = enumerate(re.split(b'\r?\n', text))
        elif self.pdf and ext == 'pdf':
            try:
                global pdf_textcache
                from .pdf_utils import get_text, get_text_by_page, pdf_textcache
                text = get_text_by_page(file)
            except ImportError:
                warn_first_import_error('pdfminer')
                warn_first_import_error('sortedcollections')
                text = None
            if text is not None:
                lines = (((ii, jj), line) for ii, page in enumerate(text) \
                            for jj, line in enumerate(page.split('\n')))
            else:
                lines = []
        elif self.docx and ext in {'docx', 'docm', 'doc'}:
            try:
                import docx
                if file not in bad_text_files:
                    try:
                        doc = docx.Document(file)
                        lines = [(ii, para.text) for ii,para in enumerate(doc.paragraphs)]
                        text = 'dummy text' 
                        # to avoid raising error on "del text"
                    except:
                        bad_text_files.add(file)
                        return
            except ImportError:
                warn_first_import_error('docx')
        elif self.x:
            # although XML and HTML documents are technically textTypeFiles,
            # etree.fromstring(text, parser) tends to crash when reading XML 
            # and etree.parse(fname, parser) seems to be more reliable.
            if isinstance(ext, str) and re.search('xm|ht', ext):
                try:
                    from .x_option import xpath_to_element_text
                    lines = xpath_to_element_text(file, self.regex)
                    if lines:
                        self.resultset[file] = {}
                        for path, elt in lines.items():
                            self.resultset[file][path] = str(elt)
                        if not self.resultset[file]:
                            del self.resultset[file]
                except ImportError:
                    warn_first_import_error('lxml')
            return
        elif self.xl and (ext in {'xlsx', 'xlsm', 'xltx', 'xltm'}):
            # may also want to allow attempts to read 'xlsb', 'xls',
            # and 'xlt' files.
            try:
                from .tabular_excel import read_excel, pd
                docs = read_excel(file)
            except ImportError:
                warn_first_import_error('openpyxl')
            if pd:
                # read_excel returns a dict mapping sheet names to DataFrames
                # Unfortunately, gorp.jsonpath can't handle DataFrames nested
                # inside other iterables, only DataFrames by themselves
                path_obj_map = {}
                for sheetname, df in docs.items():
                    self.jsonpath.add_json(df)
                    try:
                        results = self.jsonpath.extract()
                        # TODO: make jsonpath.aggregate work for DataFrames 
                        # as well
                        if not results.empty:
                            path_obj_map[sheetname] = results
                    except:
                        return
                return
            self.jsonpath.add_json(docs)
            if self.jsonpath.aggregator is not None:
                # use the aggregate function of jsonpath to aggregate the
                # values in the json, e.g., by summing them
                path_obj_map = self.jsonpath.aggregate()
            else:
                path_obj_map = self.jsonpath.extract()
            if path_obj_map:
                self.resultset.setdefault(file, {})
                self.resultset[file].update(path_obj_map)
        elif ext in textTypeFiles and file not in bad_text_files: 
            # these are all text-type file extensions
            if self.f:
                if bool(self.f_goodness_condition(rel_fname)) ^ self.v:
                    self.resultset.setdefault(file,0)
                return
            try:
                text, encoding = get_text_best_encoding(file)
            except UnicodeDecodeError:
                GorpLogger.info(f"{file} has text-type ext {ext}, but bad encoding")
                bad_text_files.add(file)
                return
            if self.j or self.y or self.tab or self.xl:
                if self.y and (ext in {'yaml', 'yml'}):
                    try:
                        import yaml
                        try:
                            docs = list(yaml.safe_load_all(text)) 
                            # returns a generator containing each "---"-delimited YAML 
                            # document in the file.
                            if len(docs) == 1:
                                docs = docs[0]
                        except yaml.constructor.ConstructorError:
                            GorpLogger.info(f"yaml ConstructorError on file {file}")
                            return
                    except ImportError:
                        warn_first_import_error('yaml')
                elif self.j and ext == 'json': # in {'json', 'ipynb'}:
                    # yes, Jupyter notebooks are JSON documents!
                    # but this may lead to unexpected results for most people
                    # so for now we stick with only 'json' extensions.
                    try:
                        docs = json.loads(text)
                    except json.decoder.JSONDecodeError: 
                        GorpLogger.info(f"JSONDecodeError on file {file}")
                        return
                elif self.tab and ext in {'tsv', 'csv', 'txt'}: 
                    # read a csv or other tabular file
                    from .tabular_excel import read_tabular
                    try:
                        docs = read_tabular(file)
                    except:
                        # document is not tabular most likely
                        return
                    text = ''
                else: # not self.a JSON or YAML file
                    return
                del text
                self.jsonpath.add_json(docs)
                if self.jsonpath.aggregator is not None:
                    # use the aggregate function of jsonpath to aggregate the
                    # values in the json, e.g., by summing them
                    path_obj_map = self.jsonpath.aggregate()
                else:
                    path_obj_map = self.jsonpath.extract()
                if 'DataFrame' in str(type(path_obj_map)):
                    # the truth value of a DataFrame is ambiguous, so the line
                    # "if path_obj_map:" raises an error for DataFrames.
                    if path_obj_map.empty:
                        return
                    self.resultset.setdefault(file, {})
                    self.resultset[file] = path_obj_map
                    return
                if path_obj_map:
                    self.resultset.setdefault(file, {})
                    self.resultset[file].update(path_obj_map) 
                # TODO: note that if the 'w' option is used later
                # to write these path_obj_map to self.a file, they must be 
                # converted to {str(PATH): OB for PATH, OB in 
                #       path_obj_map.items()})
                # because the tuple keys used in path_obj_map are not valid 
                # keys for JSON hashes or for YAML safe-dumped dicts.
                return
            else: # any other text-type file
                lines = enumerate(re.split('\r?\n', text))
        try:
            del text
            lines
        except UnboundLocalError:
            return
        self.resultset[file] = {}
        for path, line in lines:
            line_good = self.goodness_condition(line)
            if bool(line_good) ^ self.v:
                if self.o:
                    self.resultset[file][path] = line_good
                else:
                    self.resultset[file][path] = line
        if not self.resultset[file]:
            del self.resultset[file]