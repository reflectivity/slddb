"""
Classes for conversion of specific data into sqlite types and back.
"""

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


class CFormula(Converter):
    def __init__(self):
        pass

    def convert(self, data):
        res=Formula(data)
        return str(res)

    def revert(self, db_data):
        return db_data

class CArray(Converter):
    # convert numpy array to string representation and back
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
        str_data=adata.tostring()
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

class CComplex(CArray):
    def __init__(self):
        self._shape=(1,)
        self._ndim=1

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