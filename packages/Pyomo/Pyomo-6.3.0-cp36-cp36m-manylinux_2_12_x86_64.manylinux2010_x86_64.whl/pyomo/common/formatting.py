#  ___________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright 2017 National Technology and Engineering Solutions of Sandia, LLC
#  Under the terms of Contract DE-NA0003525 with National Technology and
#  Engineering Solutions of Sandia, LLC, the U.S. Government retains certain
#  rights in this software.
#  This software is distributed under the 3-clause BSD License.
#  ___________________________________________________________________________
"""This module provides general utilities for producing formatted I/O

.. autosummary::

   tostr
   tabular_writer
   StreamIndenter
"""

import types
from pyomo.common.sorting import sorted_robust

def tostr(value, quote_str=False):
    """Convert a value to a string

    This function is a thin wrapper around `str(value)` to resolve a
    problematic __str__ implementation in the standard Python container
    types (tuple, list, and dict).  Those classes implement __str__ the
    same as __repr__ (by calling repr() on each contained object).  That
    is frequently undesirable, as you may wish the string representation
    of a container to contain the string representations of the
    contained objects.

    This function generates string representations for native Python
    containers (tuple, list, and dict) that contains the string
    representations of the contained objects.  In addition, it also
    applies the same special handling to any types that derive from the
    standard containers without overriding either __repn__ or __str__.

    Parameters
    ----------
    value: object
        the object to convert to a string
    quote_str: bool
        if True, and if `value` is a `str`, then return a "quoted
        string" (as generated by repr()).  This is primarily used when
        recursively processing native Python containers.

    Returns
    -------
    str

    """
    # Override the generation of str(list), but only if the object is
    # using the default implementation of list.__str__.  Note that the
    # default implemention of __str__ (in CPython) is to call __repr__,
    # so we will test both.  This is particularly important for
    # collections.namedtuple, which reimplements __repr__ but not
    # __str__.
    _type = type(value)
    if _type not in tostr.handlers:
        # Default to the None handler (just call str()), but override it
        # in particular instances:
        tostr.handlers[_type] = tostr.handlers[None]
        if isinstance(value, list):
            if ( _type.__str__ is list.__str__ and
                 _type.__repr__ is list.__repr__ ):
                tostr.handlers[_type] = tostr.handlers[list]
        elif isinstance(value, tuple):
            if ( _type.__str__ is tuple.__str__ and
                 _type.__repr__ is tuple.__repr__ ):
                tostr.handlers[_type] = tostr.handlers[tuple]
        elif isinstance(value, dict):
            if ( _type.__str__ is dict.__str__ and
                 _type.__repr__ is dict.__repr__ ):
                tostr.handlers[_type] = tostr.handlers[dict]
        elif isinstance(value, str):
            tostr.handlers[_type] = tostr.handlers[str]

    return tostr.handlers[_type](value, quote_str)

tostr.handlers = {
    list: lambda value, quote_str: (
        "[%s]" % (', '.join(tostr(v, True) for v in value))
    ),
    dict: lambda value, quote_str: (
        "{%s}" % (', '.join('%s: %s' % (tostr(k, True), tostr(v, True))
                            for k, v in value.items()))
    ),
    tuple: lambda value, quote_str: (
        "(%s,)" % (tostr(value[0], True),) if len(value) == 1
        else "(%s)" % (', '.join(tostr(v, True) for v in value))
    ),
    str: lambda value, quote_str: (
        repr(value) if quote_str else value
    ),
    None: lambda value, quote_str: str(value),
}


def tabular_writer(ostream, prefix, data, header, row_generator):
    """Output data in tabular form

    Parameters
    ----------
    ostream: io.TextIOBase
        the stream to write to
    prefix: str
        prefix each generated line with this string
    data: iterable
        an iterable object that returns (key, value) pairs
        (e.g., from iteritems()) defining each row in the table
    header: List[str]
        list of column headers
    row_generator: function
        a function that accepts the `key` and `value` from `data` and
        returns either a tuple defining the entries for a single row, or
        a generator that returns a sequence of table rows to be output
        for the specified `key`

    """

    prefix = tostr(prefix)

    _rows = {}
    # NB: _width is a list because we will change these values
    if header:
        header = (u"Key",) + tuple(tostr(x) for x in header)
        _width = [len(x) for x in header]
    else:
        _width = None
    _minWidth = 0

    for _key, _val in data:
        try:
            _rowSet = row_generator(_key, _val)
            if isinstance(_rowSet, types.GeneratorType):
                _rowSet = list(_rowSet)
            else:
                _rowSet = [_rowSet]
        except ValueError:
            # A ValueError can be raised when row_generator is called
            # (if it is a function), or when it is exhausted generating
            # the list (if it is a generator)
            _minWidth = 4 # Ensure columns are wide enough to output "None"
            _rows[_key] = None
            continue

        _rows[_key] = [
            ((tostr("" if i else _key),) if header else ())
            + tuple(tostr(x) for x in _r)
            for i, _r in enumerate(_rowSet) ]

        if not _rows[_key]:
            _minWidth = 4
        elif not _width:
            _width = [0]*len(_rows[_key][0])
        for _row in _rows[_key]:
            for col, x in enumerate(_row):
                _width[col] = max(_width[col], len(x), col and _minWidth)

    # NB: left-justify header entries
    if header:
        # Note: do not right-pad the last header with unnecessary spaces
        tmp = _width[-1]
        _width[-1] = 0
        ostream.write(prefix
                      + " : ".join( "%%-%ds" % _width[i] % x
                                    for i,x in enumerate(header) )
                      + "\n")
        _width[-1] = tmp

    # If there is no data, we are done...
    if not _rows:
        return

    # right-justify data, except for the last column if there are spaces
    # in the data (probably an expression or vector)
    _width = ["%"+str(i)+"s" for i in _width]

    if any( ' ' in r[-1]
            for x in _rows.values() if x is not None
            for r in x  ):
        _width[-1] = '%s'
    for _key in sorted_robust(_rows):
        _rowSet = _rows[_key]
        if not _rowSet:
            _rowSet = [ [_key] + [None]*(len(_width)-1) ]
        for _data in _rowSet:
            ostream.write(
                prefix
                + " : ".join( _width[i] % x for i,x in enumerate(_data) )
                + "\n")


class StreamIndenter(object):
    """
    Mock-up of a file-like object that wraps another file-like object
    and indents all data using the specified string before passing it to
    the underlying file.  Since this presents a full file interface,
    StreamIndenter objects may be arbitrarily nested.
    """

    def __init__(self, ostream, indent=' '*4):
        self.os = ostream
        self.indent = indent
        self.stripped_indent = indent.rstrip()
        self.newline = True

    def __getattr__(self, name):
        return getattr(self.os, name)

    def write(self, data):
        if not len(data):
            return
        lines = data.split('\n')
        if self.newline:
            if lines[0]:
                self.os.write(self.indent+lines[0])
            else:
                self.os.write(self.stripped_indent)
        else:
            self.os.write(lines[0])
        if len(lines) < 2:
            self.newline = False
            return
        for line in lines[1:-1]:
            if line:
                self.os.write("\n"+self.indent+line)
            else:
                self.os.write("\n"+self.stripped_indent)
        if lines[-1]:
            self.os.write("\n"+self.indent+lines[-1])
            self.newline = False
        else:
            self.os.write("\n")
            self.newline = True

    def writelines(self, sequence):
        for x in sequence:
            self.write(x)
