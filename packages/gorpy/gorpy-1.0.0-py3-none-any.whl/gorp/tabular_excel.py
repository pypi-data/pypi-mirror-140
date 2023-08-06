import csv
from .utils import *
from .jsonpath import JsonPath
try:
    import pandas as pd
except:
    pd = None
    print("pandas (installed by pip install pandas) is recommended for the tab and xl options of gorp.\nIt's also generally awesome!")
try:
    import openpyxl
except:
    openpyxl = None # already in gorp.readfiles.import_warnings

sniffer = csv.Sniffer()


def read_excel(fname, **kwargs):
    '''Returns either a dict mapping sheetnames to DataFrames or a dict mapping
sheet names to lists of lists representing worksheets, depending on whether
or not pandas is installed.'''
    tab = None
    if pd:
        tab = pd.read_excel(fname, sheet_name = None, **kwargs)
        # if sheet_name is None, returns a dict mapping sheet names to DataFrames.
        # If no argument is supplied, the default is to return a single DataFrame
        # for the first worksheet.
    elif openpyxl:
        wkbk = openpyxl.open(fname, **kwargs)
        tab = {}
        for sheetname, wksht in zip(wkbk.sheetnames, wkbk):
            tab[sheetname] = []
            for ii, col in enumerate(wksht.columns):
                tab[sheetname].append([])
                for cell in col:
                    tab[sheetname][ii].append(cell.value)
    return tab


def read_tabular(fname, 
                 as_dict = True, 
                 header = None, 
                 amount_to_sniff = 4_000,
                 **kwargs):
    '''Tries to read a tabular text file and return an object representing its contents.
fname: the name of any tabular text file (e.g., csv, tsv).
as_dict: If pandas is not installed, and this is True, return a list of dicts mapping
    column names to values.
header: None, or a list of column names.
amount_to_sniff: int, default 4000.
    This function takes the first amount_to_sniff characters of the file
    and "sniffs" them to determine how the columns and rows are separated.
    Sniffing seems to take about 2ms/KB of text.
    '''
    beginning, encoding = get_text_best_encoding(fname, amount_to_sniff)
    dialect = sniffer.sniff(beginning)
    if pd:
        header = 'infer' if header is None else header
        tab = pd.read_csv(fname,
                           header = header,
                           delimiter = dialect.delimiter,
                           encoding = encoding,
                           **kwargs)
    else:
        with open(fname, encoding = encoding) as f:
            if as_dict:
                reader = csv.DictReader(f,
                                        fieldnames = header,
                                        dialect = dialect,
                                        **kwargs)
            else:
                reader = csv.reader(f, dialect = dialect)
            tab = list(reader)
    return tab


'''
read_csv(filepath_or_buffer: 'FilePathOrBuffer', sep=<no_default>, delimiter=None, header='infer', names=<no_default>, index_col=None, usecols=None, squeeze=False, prefix=<no_default>, mangle_dupe_cols=True, dtype: 'DtypeArg | None' = None, engine=None, converters=None, true_values=None, false_values=None, skipinitialspace=False, skiprows=None, skipfooter=0, nrows=None, na_values=None, keep_default_na=True, na_filter=True, verbose=False, skip_blank_lines=True, parse_dates=False, infer_datetime_format=False, keep_date_col=False, date_parser=None, dayfirst=False, cache_dates=True, iterator=False, chunksize=None, compression='infer', thousands=None, decimal: 'str' = '.', lineterminator=None, quotechar='"', quoting=0, doublequote=True, escapechar=None, comment=None, encoding=None, encoding_errors: 'str | None' = 'strict', dialect=None, error_bad_lines=None, warn_bad_lines=None, on_bad_lines=None, delim_whitespace=False, low_memory=True, memory_map=False, float_precision=None, storage_options: 'StorageOptions' = None)
'''

'''csv.Dialect properties
 |  delimiter = None
 |
 |  doublequote = None
 |
 |  escapechar = None
 |
 |  lineterminator = None
 |
 |  quotechar = None
 |
 |  quoting = None
 |
 |  skipinitialspace = None
'''