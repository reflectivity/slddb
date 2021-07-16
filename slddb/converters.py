"""
Classes for conversion of specific data into sqlite types and back.
"""
import re
from numpy import array, frombuffer
from datetime import datetime
from .material import Formula

SQLITE_TYPES=[int, float, str, bytes]
SQLITE_STR={int: 'INT', float: 'REAL', str: 'TEXT', bytes: 'BLOB'}

class Converter():
    """
    Base class for all other converters, can't be used stand alone.
    """
    sql_type="TEXT" # if subclass does not define the SQLite type assume TEXT for compatibility

    def __init__(self):
        raise NotImplementedError(
            "Converters has to be used from a derived class")

    def validate(self, data):
        # Default behavior is to just try to convert.
        try:
            self.convert(data)
        except Exception as e:
            return False
        else:
            return True

    def convert(self, data):
        raise NotImplementedError("Sub-class has to implement convert method")

    def revert(self, db_data):
        # Default behavior is to return the database data directly
        return db_data

    def revert_serializable(self, db_data):
        # generage json serialisable value, default is the normal value
        return self.revert(db_data)

    def html_input(self, field, value):
        # return a string containing the input key for html entry template
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}">'


class CType(Converter):
    # converts between a python type and SQLite type

    def __init__(self, fromtype, dbtype, db_repstr=None):
        self._fromtype=fromtype
        if dbtype not in SQLITE_TYPES:
            raise TypeError("Type %s is not a valid SQLite type"%
                            dbtype.__name__)
        self._dbtype=dbtype
        if db_repstr is None:
            self.sql_type=SQLITE_STR[dbtype]
        else:
            self.sql_type=db_repstr

    def convert(self, data):
        value=self._fromtype(data)
        return self._dbtype(value)

    def revert(self, db_data):
        if db_data is None:
            return None
        elif type(db_data) is not self._dbtype:
            raise ValueError(
                "Wrong type of database data %s, expecte %s"%(
                    type(db_data).__name__,
                    self._dbtype.__name__)
                             )
        else:
            return self._fromtype(db_data)

class CDate(Converter):
    sql_type='TEXT'

    def __init__(self):
        pass

    def convert(self, data):
        if type(data) is datetime:
            return data.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return data

    def revert(self, db_data):
        if db_data is not None:
            return  datetime.strptime(db_data, '%Y-%m-%d %H:%M:%S')
        else:
            return None

    def revert_serializable(self, db_data):
        return db_data

    def html_input(self, field, value):
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}"'\
               ' placeholder="date: {year}-{month}-{day} {hours}:{minutes}:{seconds}"/>'

class CFormula(Converter):
    def __init__(self):
        pass

    def convert(self, data):
        res=Formula(data)
        return str(res)

    def revert(self, db_data):
        return db_data

    def html_input(self, field, value):
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}"'\
               ' placeholder="Fe2O3 / H[2]2O / H2(C2H4)4"/>'

class ValidatedString(CType):
    regex=None
    placeholder=''

    def __init__(self):
        CType.__init__(self, str, str)

    def convert(self, data):
        if re.match(self.regex, data) is not None:
            return CType.convert(self, data)
        else:
            raise ValueError("Not a valid %s: %s"%(self.__class__.__name__[1:], data))

    def html_input(self, field, value):
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}"'\
               ' placeholder="'+self.placeholder+'"/>'

class CUrl(ValidatedString):
    regex=re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    placeholder='http://www.your_website.net'

class CMail(ValidatedString):
    regex=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.IGNORECASE)
    placeholder='your.name@domain.net'

class Cdoi(ValidatedString):
    regex=re.compile(
        r'^https://doi.org/'  # https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    placeholder='https://doi.org/your/ref'

    def convert(self, data):
        # if entry is just the doi value it is replaced by the url
        if data.startswith('http'):
            return ValidatedString.convert(self, data)
        else:
            return ValidatedString.convert(self, 'https://doi.org/'+data)

class Ccas(ValidatedString):
    regex=re.compile(
        r'\b[1-9]{1}[0-9]{1, 5}-\d{2}-\d\b', re.IGNORECASE)
    placeholder='xxxxxxx-yy-z'


class CArray(Converter):
    # convert numpy array to bytest representation and back
    sql_type='BLOB'

    def __init__(self, shape=None, ndim=None):
        self._shape=shape
        self._ndim=ndim

    def convert(self, data):
        adata=array(data)
        if self._shape is not None and adata.shape!=self._shape:
            raise ValueError("Array shape should be %s"%str(self._shape))
        if self._ndim is not None and data.ndim!=self._ndim:
            raise ValueError("Array dimension should be %s"%self._ndim)
        type_char=data.dtype.char.encode('ascii')
        dim=str(data.ndim).encode('ascii')
        pre_chars=type_char+dim
        if data.ndim!=1:
            # for arrays >1d store the array shape before the data
            # first store the length of the shape string and then
            # the string itself
            shapestr=str(data.shape).encode('ascii')
            shapelen=("%06i"%len(shapestr)).encode('ascii')
            pre_chars+=shapelen+shapestr
        str_data=adata.tobytes()
        return pre_chars+str_data

    def revert(self, db_data):
        if db_data is None:
            return None
        if type(db_data) is not bytes:
            raise TypeError("Array type needs binary string to revert")

        dtype=db_data[0:1]
        ndim=int(db_data[1:2].decode('ascii'))
        if ndim!=1:
            shapelen=int(db_data[2:8].decode('ascii'))
            shape=eval(db_data[8:8+shapelen].decode('ascii'))
            dstart=8+shapelen
        else:
            dstart=2
            shape=None
        return frombuffer(db_data[dstart:], dtype=dtype).reshape(shape)

    def revert_serializable(self, db_data):
        if db_data is None:
            return None
        else:
            data=self.revert(db_data)
            if data.dtype == complex:
                return str(data)
            else:
                return data.tolist()

class CLimited(CType):
    # a converter for numbers that checks the range
    def __init__(self, fromtype, db_type,
                 low_lim=None, up_lim=None, db_repstr=None):
        CType.__init__(self, fromtype, db_type, db_repstr=db_repstr)
        self._low_lim=low_lim
        self._up_lim=up_lim

    def validate(self, data):
        if CType.validate(self, data):
            data=self.convert(data)
            return (self._low_lim is None or self._low_lim<=data) and (
                    self._up_lim is None or self._up_lim>=data)
        else:
            return False

    def convert(self, data):
        value=CType.convert(self, data)
        if (self._low_lim is None or self._low_lim<=value) and (
                    self._up_lim is None or self._up_lim>=value):
            return value
        else:
            raise ValueError("Value out of range, has to be %s<value<%s"%(
                self._low_lim, self._up_lim))

    def html_input(self, field, value):
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}"'\
               f' placeholder="{self._low_lim}<value<{self._up_lim}"/>'

class CComplex(CArray):
    def __init__(self):
        CArray.__init__(self, shape=(1,), ndim=1)

    def convert(self, data):
        if type(data) is str:
            data=complex(data)
        if type(data) not in [float, complex]:
            raise TypeError("Needs to be complex number")
        return CArray.convert(self, array([data]))

    def revert(self, db_data):
        if db_data is None:
            return None
        else:
            return CArray.revert(self, db_data)[0]

    def revert_serializable(self, db_data):
        if db_data is None:
            return None
        else:
            return str(self.revert(db_data))

    def html_input(self, field, value):
        return f'<input type="text" name="{field}" id="compound {field}" value="{value}"'\
               ' placeholder="complex: (real)+(imag)j"/>'


class CSelect(CType):
    def __init__(self, options):
        self.options=options
        CType.__init__(self, str, str)

    def convert(self, data):
        value=CType.convert(self, data)
        if not value in self.options:
            raise ValueError("Value has to be in selection %s"%repr(self.options))
        return value

    def html_input(self, field, value):
        output=f'<select name="{field}" id="compound {field}">'
        output+='<option value=""></option>'
        for selection in self.options:
            if value==selection:
                output+=f'<option value="{selection}" selected>{selection}</option>'
            else:
                output+=f'<option value="{selection}">{selection}</option>'
        output+='</select>'
        return output

class CMultiSelect(CType):
    def __init__(self, options):
        self.options=options
        CType.__init__(self, list, str)

    def convert(self, data):
        data=list(data)
        for value in data:
            if not value in self.options:
                raise ValueError("Item have to be in selection %s"%repr(self.options))
        return repr(data)

    def revert(self, db_data):
        if db_data is None:
            return []
        return eval(db_data)

    def html_input(self, field, value):
        output=f'<select name="{field}" id="compound {field}" multiple>'
        for selection in self.options:
            if selection in value:
                output+=f'<option value="{selection}" selected>{selection}</option>'
            else:
                output+=f'<option value="{selection}">{selection}</option>'
        output+='</select><br />'
        output+=f'<input type="button" id="btnReset {field}" value="clear" onclick="document.getElementById(\'compound {field}\').selectedIndex=-1;" />'
        output+=' use ctrl+click'
        return output
