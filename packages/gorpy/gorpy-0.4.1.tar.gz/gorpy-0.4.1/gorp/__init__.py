'''gorpy: Good Old Regex and Python
This is a grep/sed/ls/renaming tool for Python 3.6-3.9 that includes:
    * piping syntax, 
    * a built-in jsonpath implementation for searching and manipulating JSON/YAML
        documents, comparable to jsonpath_ng in power and extensibility.
    * Text extraction from PDF's and Word documents
    * support for XPath and CSS selectors to filter HTML and XML documents
    * automatically opening all files found if desired (-p option)
    * and much more
It can be conveniently used via the command line, through an interactive prompt,
    or programmatically using a GorpSession object.
Wait: yet another grep tool? Didn't we already have enough of those?
Yes, no doubt. For sed-type tasks, you're probably better off using the Unix standard
    grep or something similar. I personally will continue using Notepad++ to edit my
    text files most of the time.
For renaming and finding files, I will usually stick to the Windows File Explorer.

I envision gorp being most useful as a tool for editing JSON and YAML based on the
    strength of the jsonpath module.
I also find the ability to automatically open files found convenient.
'''
__all__ = ['readfiles', 'option_docs', 'utils', 'x_option', 'zip_utils', 'tabular_excel', 'textcache', '__main__', 'pdf_utils', 'k_option_del_files', 'gprint', 'jsonpath', 'extended_programming_file_exts']

from .readfiles import GorpSession, GorpLogger, GorpHandler, FileReader, Orddict
from .readfiles import helpstring
from .utils import DEFAULT_OPTIONS, PDF_PAGE_LIMIT, PROMPT_K_OPTION, PROMPT_U_OPTION, U_OPTION_OVERWRITES
from . import jsonpath

__version__ = '0.4.1'