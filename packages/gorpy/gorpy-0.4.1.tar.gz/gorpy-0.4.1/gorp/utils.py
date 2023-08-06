import sys
import os
import re
import datetime
import json
import time
from dateutil import parser as date_parser
from math_eval import compute, binops
import logging
GorpLogger = logging.getLogger("GorpLogger")
GorpLogger.setLevel(logging.WARNING)
gorpdir = os.path.abspath(os.path.dirname(__file__))
default_options_fname = os.path.join(gorpdir, "DEFAULT_OPTIONS.json")
# bad_text_files_fname = os.path.join(gorpdir, "bad_text_files.json")

if sys.version_info.minor < 8 or sys.version_info.major < 3:
    from collections import OrderedDict as Orddict
else:
    Orddict = dict # regular dicts remember insertion order as of Python 3.7

if hasattr(sys, "getwindowsversion"):
    run_file_default_app = os.startfile # os.startfile is only available on Windows
else: # we use subprocess to open the file on any OS that's not Windows
    def run_file_default_app(filename):
        import subprocess
        subprocess.run(filename, shell = True, check = False)

INITIAL_DEFAULT_OPTIONS = {'PDF_PAGE_LIMIT': 100, 
                           'PROMPT_K_OPTION': True,
                           'PROMPT_U_OPTION': True,
                           "U_OPTION_OVERWRITES": True,
                           "ALLOW_REMOVE_TREES": False,
                           'bad_text_files': set()} 
                           #this is how they are initialized
# Could consider including pdf_textcache.json in bad_text_files, because it
# doesn't include particularly useful info and it's guaranteed to have a ton
# of text on a single line.

try:
    with open(default_options_fname) as f:
        DEFAULT_OPTIONS = json.load(f)
except:
    # DEFAULT_OPTIONS file doesn't exist or contents were deleted somehow
    DEFAULT_OPTIONS = INITIAL_DEFAULT_OPTIONS.copy()
DEFAULT_OPTIONS['bad_text_files'] = set(DEFAULT_OPTIONS['bad_text_files'])
# contains all filenames of files with a text-type extension 
# but that can't be read by the open() method using any 
# encoding in utils.text_encodings.
# Checking set membership is at least 10,000x faster than
# checking all of those encodings.
globals().update(DEFAULT_OPTIONS)


def is_iterable(x):
    '''Returns True for all iterables except str and bytes, else False.'''
    return hasattr(x,'__iter__') and not isinstance(x, (str, bytes))


# add your favorite text-type file extensions here!
textTypeFiles = {'bat',
 'c',
 'cpp',
 'cs',
 'css',
 'csv',
 'fwf', # fixed-width files (does anyone actually use these?)
 'gitignore',
 'go',
 'h', # extension for C and C++ header files (e.g., "#include 'stdio.h')
 'htm',
 'html',
 'ipynb',
 'java',
 'js',
 'json',
 'less', # LEan StyleSheets, a superset of CSS
 'log',
 'md',
 'py',
 'r', # normally R files have the '.R' extension but all extensions are
      # coerced to lowercase before reading anyway; same note for 'rmd' ext.
 'rb',
 'rmd',
 'rs',
 'rst', # ReStructuredText (e.g., Sphinx)
 'sass', # SASS (Syntactically Awesome StyleSheets), a cousin of CSS
 'scss', # also SASS
 'sh', # bash file for Linux
 'sql',
 'toml',
 'ts',
 'tsv',
 'txt',
 'xml',
 'yaml',
 'yml'}

def isTextType(fname, case_insensitive = False):
    ext = get_ext(fname)
    if ext is None:
        return False
    if case_insensitive:
        return ext.lower() in textTypeFiles
    return ext in textTypeFiles


text_encodings = [None, # use the default encoding method of Python's open() function.
    'utf_8', # probably 99% of the time if this fails everything else will fail too
    'utf_8_sig',
    'utf_32',
    'latin_1',
    'utf_32_be',
    'utf_32_le',
    'utf_16',
    'utf_16_be',
    'utf_16_le',
    'utf_7',
    'ascii',
    'big5',
    'big5hkscs',
# 'cp037', 'cp273', 'cp424', 'cp437', 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257', 'cp1258', 'cp65001', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u', 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'idna', 'mbcs', 'oem', 'palmos', 'punycode', 'raw_unicode_escape', 'unicode_escape', 
    # all of these are I think much less likely; since trying every single encoding
    # requires about 1sec more for every file that doesn't have any valid encoding at
    # all, it seems likely to me that only trying a small subset of the possible
    # encodings saves enough time to justify the loss of generality.
    'undefined' #always raises an exception
 ]

def get_text_best_encoding(fname, size = -1):
    '''Keep searching until you find a valid encoding for a file, or exhaust all the
    encodings designated in textTypeFiles, at which point raise a UnicodeDecodeError.
If a good encoding is found, return the first "size" characters of the text of fname,
    or all of the text if size is negative or omitted.'''
    for enc_num,encoding in enumerate(text_encodings):
        try:
            with open(fname,'r', encoding = encoding) as f:
                #print(encoding,end=', ')
                return f.read(size), encoding # found a good encoding, stop trying new ones.
        except UnicodeDecodeError as ex:
            pass #keep trying other encodings
    raise ex


def funcname(func):
    '''Mostly useful for running functions on arbitrary string inputs with eval().'''
    module = func.__module__
    name = re.findall("<.*(?:function|class) \'?([a-zA-Z_\d\.]+)\'?.*>", repr(func))[0]
    if isinstance(func, type) or module in ['builtins', '__main__']:
        return name
    return module + '.' + name


def seconds_to_datetime(secs):
    unix_epoch_0 = datetime.datetime(1970, 1, 1)
    return unix_epoch_0 + datetime.timedelta(seconds = int(secs))


def last_mod_time(fname,as_datetime=True):
    '''Get the last time the file named fname was modified.
Default return value is a formatted datetime string. If as_datetime, then 
return a datetime.datetime object representing that time.'''
    mod_time_seconds = os.path.getmtime(fname)
    formatted_time_string = time.ctime(mod_time_seconds)
    if as_datetime:
        return date_parser.parse(formatted_time_string)
    else:
        return formatted_time_string


def commanum(num):
    '''As of Python 3.7, this can be accomplished in an f-string by the syntax
    f"{num:,f}", in which the ":,f" adds commas at the appropriate places.
In Python 2.6 to 3.6, we could use "{n:,f}".format(n = nums) or similar.''' 
    bd = str(num).split('.')
    if len(bd)==1:
        base, dec = bd[0],''
    else:
        base,dec = bd
    newbase =  ''
    lb = len(base)
    for ii in range(1,lb):
        newbase+=base[lb-ii]
        if ii%3==0:
            newbase+=','
    newbase += base[0]
    if dec=='':
        return newbase[::-1]
    return newbase[::-1]+'.'+dec
    

def format_bytes(num, decimal_places = 3):
    '''Converts a number of bytes (float/int) into a reader-friendly format.
    Rounds values off to decimal_places decimal places, or to 0 decimal places 
    if num < 1000.'''
    if num >= 1e9:
        return f"{num/1e9:,.{decimal_places}f} GB"
    elif num >= 1e6:
        return f"{num/1e6:,.{decimal_places}f} MB"
    elif num >= 1e3:
        return f"{num/1e3:,.{decimal_places}f} KB"
    else:
        return f"{num:.0f} bytes"
        

def byteform_to_num(byte_format):
    '''Converts a string expressing a size of a file in bytes into the 
    corresponding number of bytes. Accepts commas and decimal points in nums.
    Allows 'b', 'mb', 'gb', and variants like 'bytes', but not 'tb', 'zb', etc.
Note that format_bytes is a lossy function (it doesn't retain all sigfigs 
    by default), so byteform_to_num(format_bytes(x)) does not always equal x.
    '''
    x = re.findall('([\d,\.]+)\s*([a-z]*)', byte_format, re.I)[0]
    num, suf = float(x[0].replace(',', '')), x[1].lower()
    if suf == '' or suf[0] == 'b':
        return num
    elif suf[:2] == 'kb':
        return num*1e3
    elif suf[:2] == 'mb':
        return num*1e6
    elif suf[:2] == 'gb':
        return num*1e9
    
    raise ValueError(f"byteform_to_num couldn't recognize quantifier '{suf}'")


def ext_checker(fname,ext):
    '''Replaces the extension of fname with ext, or adds ext to fname
    if fname doesn't already have an extension.'''
    ext_begin = -len(fname)
    for ind in range(1,len(fname)+1):
        if fname[-ind]=='.':
            ext_begin = ind
            break
    return fname[:-ext_begin] + '.' + ext


def get_ext(fname):
    '''Returns the extension of a filename, or None if there is no extension.'''
    for ii in range(len(fname)-1,-1,-1):
        if fname[ii]=='.':
            return fname[ii+1:]


def increment_name(fname,check_dups = True,start_num = 0):
    '''If fname is not the name of an extant file, returns fname.
Else:
    Create a new file name with _{number} appended to the end of fname,
    where "number" is either start_num (if check_dups is False or
    no file already exists with that extension) or the lowest integer n greater
    than start_num such that no file named fname+"_"+str(n)+(fname's extension)
    already exists with that extension.'''
    fname = os.path.abspath(fname)
    ext = get_ext(fname)
    stem = fname[:-len(ext)-1]
    if not check_dups:
        return stem+'_'+str(start_num)+ '.' + ext
    else:
        if not (os.path.exists(fname) or os.path.isfile(fname)):
            return fname
        ii = start_num
        while True:
            new_ext = stem+'_'+str(ii) + '.' + ext
            if not os.path.exists(new_ext):
                return new_ext
            ii += 1

