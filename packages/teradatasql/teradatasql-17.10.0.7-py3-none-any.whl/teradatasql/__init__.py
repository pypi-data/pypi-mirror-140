# Copyright 2018-2019 by Teradata Corporation. All rights reserved.

import binascii
import ctypes
import datetime
import decimal
import io
import json
import os
import platform
import re
import struct
import sys
import threading
import time
import traceback
from . import vernumber

apilevel = "2.0" # Required by DBAPI 2.0

threadsafety = 2 # Threads may share the module and connections, but not cursors # Required by DBAPI 2.0

paramstyle = "qmark" # Required by DBAPI 2.0

class Warning(Exception): # Required by DBAPI 2.0
    pass

class Error(Exception): # Required by DBAPI 2.0
    pass

class InterfaceError(Error): # Required by DBAPI 2.0
    pass

class DatabaseError(Error): # Required by DBAPI 2.0
    pass

class DataError(DatabaseError): # Required by DBAPI 2.0
    pass

class OperationalError(DatabaseError): # Required by DBAPI 2.0
    pass

class IntegrityError(DatabaseError): # Required by DBAPI 2.0
    pass

class InternalError(DatabaseError): # Required by DBAPI 2.0
    pass

class ProgrammingError(DatabaseError): # Required by DBAPI 2.0
    pass

class NotSupportedError(DatabaseError): # Required by DBAPI 2.0
    pass

osType = platform.system()
lockInit = threading.Lock()
bInitDone = False
goside = None

def logMsg (sCategory, s):
    print ("{:.23} [{}] PYDBAPI-{} {}".format (datetime.datetime.now ().strftime ("%Y-%m-%d.%H:%M:%S.%f"), threading.current_thread ().name, sCategory, s))
    sys.stdout.flush ()

def traceLog (s):
    logMsg ("TRACE", s)

def debugLog (s):
    logMsg ("DEBUG", s)

def timingLog (s):
    logMsg ("TIMING", s)

def prototype(rtype, func, *args):
    func.restype = rtype
    func.argtypes = args

class TeradataConnection:

    def __init__ (self, sConnectParams=None, **kwargs):

        if ctypes.sizeof (ctypes.c_voidp) < 8:
            raise ImportError ("This package requires 64-bit Python. 32-bit Python is not supported.")

        self.uLog = 0
        self.bTraceLog = False
        self.bDebugLog = False
        self.bTimingLog = False
        self.uConnHandle = None # needed by __repr__

        if not sConnectParams:
            sConnectParams = '{}'

        for sKey, oValue in kwargs.items ():
            if isinstance (oValue, bool):
                kwargs [sKey] = str (oValue).lower () # use lowercase words true and false
            else:
                kwargs [sKey] = str (oValue)

        # Compose a streamlined stack trace of script file names and package names
        listFrames = []
        sPackagesDir = os.path.dirname (os.path.dirname (__file__)).replace (os.sep, "/") + "/"
        for fr in traceback.extract_stack ():
            sFrame = fr [0].replace (os.sep, "/")
            if sFrame.startswith (sPackagesDir):
                sFrame = sFrame [len (sPackagesDir) : ].split ("/") [0] # remove the packages dir prefix and take the first directory, which is the package name
            else:
                sFrame = sFrame.split ("/") [-1] # take the last element, which is the Python script file name
            if not sFrame.startswith ("<") and sFrame not in listFrames: # omit <string>, omit <template>, omit repeated entries
                listFrames += [ sFrame ]

        kwargs ['client_kind'  ] = 'P' # G = Go, P = Python, R = R, S = Node.js
        kwargs ['client_vmname'] = 'Python ' + sys.version
        kwargs ['client_osname'] = platform.platform () + ' ' + platform.machine ()
        kwargs ['client_stack' ] = " ".join (listFrames)
        kwargs ['client_extra' ] = 'PYTHON=' + platform.python_version () + ';' # must be semicolon-terminated
        try:
            kwargs ['client_extra'] += 'TZ=' + datetime.datetime.now (tz=datetime.timezone.utc).astimezone ().strftime ('%Z %z') + ';' # must be semicolon-terminated
        except: # astimezone() can fail when the TZ environment variable is set to an unexpected format
            pass

        sConnectArgs = json.dumps (kwargs)

        global bInitDone, goside # assigned-to variables are local unless marked as global

        try:
            lockInit.acquire()
            if not bInitDone:
                bInitDone = True

                if osType == "Windows":
                    sExtension = "dll"
                elif osType == "Darwin":
                    sExtension = "dylib"
                else:
                    sExtension = "so"

                sLibPathName = os.path.join(os.path.dirname(__file__), "teradatasql." + sExtension)
                goside = ctypes.cdll.LoadLibrary(sLibPathName)

                prototype (None, goside.goCombineJSON     , ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goParseParams     , ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goCreateConnection, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goCloseConnection , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goCreateRows      , ctypes.c_uint64, ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint64, ctypes.c_char_p, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64))
                prototype (None, goside.goResultMetaData  , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_uint64), ctypes.POINTER (ctypes.c_int32), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goFetchRow        , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_int32), ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goNextResult      , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)), ctypes.POINTER (ctypes.c_char))
                prototype (None, goside.goCloseRows       , ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER (ctypes.POINTER (ctypes.c_char)))
                prototype (None, goside.goFreePointer     , ctypes.c_uint64, ctypes.POINTER (ctypes.c_char))

        finally:
            lockInit.release()

        pcError = ctypes.POINTER (ctypes.c_char) ()
        pcCombined = ctypes.POINTER (ctypes.c_char) ()
        goside.goCombineJSON (sConnectParams.encode ('utf-8'), sConnectArgs.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (pcCombined))
        if pcError:
            sErr = ctypes.string_at (pcError).decode ('utf-8')
            goside.goFreePointer (self.uLog, pcError)
            raise OperationalError (sErr)

        sConnectParams = ctypes.string_at (pcCombined).decode ('utf-8')
        goside.goFreePointer (self.uLog, pcCombined)

        pcError = ctypes.POINTER (ctypes.c_char) ()
        uLog = ctypes.c_uint64 ()
        goside.goParseParams (sConnectParams.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (uLog))
        if pcError:
            sErr = ctypes.string_at (pcError).decode ('utf-8')
            goside.goFreePointer (self.uLog, pcError)
            raise OperationalError (sErr)

        self.uLog = uLog.value
        self.bTraceLog  = (self.uLog & 1) != 0
        self.bDebugLog  = (self.uLog & 2) != 0
        self.bTimingLog = (self.uLog & 8) != 0

        if self.bTraceLog:
            traceLog ("> enter __init__ {}".format (sConnectParams))
        try:
            pcError = ctypes.POINTER (ctypes.c_char)()
            uConnHandle = ctypes.c_uint64()
            goside.goCreateConnection (self.uLog, vernumber.sVersionNumber.encode ('utf-8'), sConnectParams.encode ('utf-8'), ctypes.byref (pcError), ctypes.byref (uConnHandle))
            if pcError:
                sErr = ctypes.string_at(pcError).decode('utf-8')
                goside.goFreePointer (self.uLog, pcError)
                raise OperationalError(sErr)

            self.uConnHandle = uConnHandle.value

        finally:
            if self.bTraceLog:
                traceLog ("< leave __init__ {}".format (self))

        # end __init__

    def close(self): # Required by DBAPI 2.0

        if self.bTraceLog:
            traceLog ("> enter close {}".format (self))
        try:
            pcError = ctypes.POINTER (ctypes.c_char)()
            goside.goCloseConnection (self.uLog, self.uConnHandle, ctypes.byref (pcError))
            if pcError:
                sErr = ctypes.string_at(pcError).decode('utf-8')
                goside.goFreePointer (self.uLog, pcError)
                raise OperationalError(sErr)

        finally:
            if self.bTraceLog:
                traceLog ("< leave close {}".format (self))

        # end close

    def commit(self): # Required by DBAPI 2.0
        if self.bTraceLog:
            traceLog ("> enter commit {}".format (self))
        try:
            with self.cursor () as cur:
                cur.execute ("{fn teradata_commit}")
        finally:
            if self.bTraceLog:
                traceLog ("< leave commit {}".format (self))

        # end commit

    def rollback(self): # Required by DBAPI 2.0
        if self.bTraceLog:
            traceLog ("> enter rollback {}".format (self))
        try:
            with self.cursor () as cur:
                cur.execute ("{fn teradata_rollback}")
        finally:
            if self.bTraceLog:
                traceLog ("< leave rollback {}".format (self))

        # end rollback

    def cursor(self): # Required by DBAPI 2.0
        return TeradataCursor(self)

    def __enter__(self): # Implements with-statement context manager
        return self

    def __exit__(self, t, value, traceback): # Implements with-statement context manager

        if self.bTraceLog:
            traceLog ("> enter __exit__ {}".format (self))
        try:
            self.close()

        finally:
            if self.bTraceLog:
                traceLog ("< leave __exit__ {}".format (self))

        # end __exit__

    def __repr__(self): # Equivalent to the toString method in Java or the String method in Go
        return("{} uConnHandle={}".format(self.__class__.__name__, self.uConnHandle))

    # end class TeradataConnection

class DBAPITypeObject:

    def __init__(self, *values):
        self.values = values

    def __eq__(self, other):
        return other in self.values

    # end class DBAPITypeObject

connect = TeradataConnection # Required by DBAPI 2.0

Date = datetime.date # Required by DBAPI 2.0

Time = datetime.time # Required by DBAPI 2.0

Timestamp = datetime.datetime # Required by DBAPI 2.0

DateFromTicks = datetime.date.fromtimestamp # Required by DBAPI 2.0

def TimeFromTicks (x): # Required by DBAPI 2.0
    return datetime.datetime.fromtimestamp (x).time ()

TimestampFromTicks = datetime.datetime.fromtimestamp # Required by DBAPI 2.0

Binary = bytes # Required by DBAPI 2.0

STRING = str # Required by DBAPI 2.0

BINARY = bytes # Required by DBAPI 2.0

NUMBER = DBAPITypeObject (int, float, decimal.Decimal) # Required by DBAPI 2.0

DATETIME = DBAPITypeObject (datetime.date, datetime.time, datetime.datetime) # Required by DBAPI 2.0

ROWID = None # Required by DBAPI 2.0

# Serialized data value type codes:
# B=bytes
# D=double (64-bit double)
# F=false (bool)
# I=integer (32-bit integer)
# L=long (64-bit integer)
# M=number
# N=null
# S=string (UTF8-encoded)
# T=true (bool)
# U=date
# V=time
# W=time with time zone
# X=timestamp
# Y=timestamp with time zone
# Z=terminator

def _serializeCharacterValue (abyTypeCode, s):

    aby = s.encode ('utf-8')
    return abyTypeCode + struct.pack (">Q", len (aby)) + aby

def _deserializeCharacterValue (abyTypeCode, pc, i, row):

    if pc [i] == abyTypeCode:
        i += 1

        uByteCount = struct.unpack (">Q", pc [i : i + 8]) [0] # uint64
        i += 8

        sValue = pc [i : i + uByteCount].decode ('utf-8')
        i += uByteCount

        if row is not None:

            # Accommodate optional fractional seconds for V=time, W=time with time zone, X=timestamp, Y=timestamp with time zone
            sFormatSuffix = '.%f' if abyTypeCode in (b'V', b'W', b'X', b'Y') and '.' in sValue else ''

            if abyTypeCode in (b'W', b'Y'): # W=time with time zone, Y=timestamp with time zone
                sValue = sValue [ : -3] + sValue [-2 : ] # remove colon from time zone value for compatibility with strptime
                sFormatSuffix += '%z'

            if abyTypeCode == b'U': # U=date
                row.append (datetime.datetime.strptime (sValue, '%Y-%m-%d').date ())

            elif abyTypeCode in (b'V', b'W'): # V=time, W=time with time zone
                row.append (datetime.datetime.strptime (sValue, '%H:%M:%S' + sFormatSuffix).timetz ())

            elif abyTypeCode in (b'X', b'Y'): # X=timestamp, Y=timestamp with time zone
                row.append (datetime.datetime.strptime (sValue, '%Y-%m-%d %H:%M:%S' + sFormatSuffix))

            elif abyTypeCode == b'M': # M=number
                row.append (decimal.Decimal (sValue))

            else: # S=string
                row.append (sValue)

            # end if row is not None

        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type {}/N but got {} at byte offset {}'.format (abyTypeCode, pc [i], i))

    # end _deserializeCharacterValue

def _serializeBool (b):

    return b'T' if b else b'F'

def _deserializeBool (pc, i, row):

    if pc [i] in (b'T', b'F'): # T=true, F=false

        if row is not None:
            row.append (pc [i] == b'T')
        return i + 1

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type T/F/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeBool

def _serializeBytes (aby):

    return b'B' + struct.pack (">Q", len (aby)) + aby

def _deserializeBytes (pc, i, row):

    if pc [i] == b'B': # B=bytes
        i += 1

        uByteCount = struct.unpack (">Q", pc [i : i + 8]) [0] # uint64
        i += 8

        abyValue = pc [i : i + uByteCount]
        i += uByteCount

        if row is not None:
            row.append (abyValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type B/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeBytes

def _serializeDate (da):

    return _serializeCharacterValue (b'U', da.isoformat ())

def _deserializeDate (pc, i, row):

    return _deserializeCharacterValue (b'U', pc, i, row)

def _serializeDouble (d):

    return b'D' + struct.pack (">d", d)

def _deserializeDouble (pc, i, row):

    if pc [i] == b'D': # D=double
        i += 1

        dValue = struct.unpack (">d", pc [i : i + 8]) [0] # float64
        i += 8

        if row is not None:
            row.append (dValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type D/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeDouble

def _serializeInt (n):

    return b'I' + struct.pack (">i", n)

def _deserializeInt (pc, i, row):

    if pc [i] == b'I': # I=integer
        i += 1

        nValue = struct.unpack (">i", pc [i : i + 4]) [0] # int32
        i += 4

        if row is not None:
            row.append (nValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type I/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeInt

def _serializeLong (n):

    return b'L' + struct.pack (">q", n)

def _deserializeLong (pc, i, row):

    if pc [i] == b'L': # L=long
        i += 1

        nValue = struct.unpack (">q", pc [i : i + 8]) [0] # int64
        i += 8

        if row is not None:
            row.append (nValue)
        return i

    elif pc [i] == b'N': # N=null
        return _deserializeNull (pc, i, row)

    else:
        raise OperationalError ('Expected column type L/N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeLong

def _serializeNull ():

    return b'N'

def _deserializeNull (pc, i, row):

    if pc [i] == b'N': # N=null

        if row is not None:
            row.append (None)
        return i + 1

    else:
        raise OperationalError ('Expected column type N but got {} at byte offset {}'.format (pc [i], i))

    # end _deserializeNull

def _serializeNumber (dec):

    return _serializeCharacterValue (b'M', '{:f}'.format (dec)) # avoid exponential notation

def _deserializeNumber (pc, i, row):

    return _deserializeCharacterValue (b'M', pc, i, row)

def _serializeString (s):

    return _serializeCharacterValue (b'S', s)

def _deserializeString (pc, i, row):

    return _deserializeCharacterValue (b'S', pc, i, row)

def _serializeTime (ti):

    return _serializeCharacterValue (b'W' if ti.tzinfo else b'V', ti.isoformat ())

def _deserializeTime (pc, i, row):

    return _deserializeCharacterValue (b'V', pc, i, row)

def _deserializeTimeWithTimeZone (pc, i, row):

    return _deserializeCharacterValue (b'W', pc, i, row)

def _serializeTimestamp (ts):

    return _serializeCharacterValue (b'Y' if ts.tzinfo else b'X', ts.isoformat (' '))

def _deserializeTimestamp (pc, i, row):

    return _deserializeCharacterValue (b'X', pc, i, row)

def _deserializeTimestampWithTimeZone (pc, i, row):

    return _deserializeCharacterValue (b'Y', pc, i, row)

def _formatTimedelta (tdelta):

    # Output format matches VARCHAR values accepted by the Teradata Database for implicit conversion to INTERVAL DAY TO SECOND.
    # positive:  1234 12:34:56.123456
    # negative: -1234 12:34:56.123456

    nMM, nSS = divmod (tdelta.seconds, 60)
    nHH, nMM = divmod (nMM, 60)

    # Prepend a space character for a positive days value.
    return '{: d} {:02d}:{:02d}:{:02d}.{:06d}'.format (tdelta.days, nHH, nMM, nSS, tdelta.microseconds)

    # end _formatTimedelta

def _hexDump (aby):

    asLines = []

    for iOffset in range (0, len (aby), 16):

        abySegment = aby [iOffset : min (iOffset + 16, len (aby))]

        sHexDigits = binascii.hexlify (abySegment).decode ('ascii')
        asHexDigits = [ sHexDigits [i : i + 2] for i in range (0, len (sHexDigits), 2) ]
        sSpacedHexDigits = " ".join (asHexDigits)

        abyPrintable = b''
        for i in range (0, len (abySegment)):
            if abySegment [i] in range (32, 126): # printable chars are 32 space through 126 ~ tilde
                abyPrintable += abySegment [i : i + 1]
            else:
                abyPrintable += b'.'

        sPrintable = abyPrintable.decode ('ascii')

        asLines += [ "{:08x}  {:<47}  |{}|".format (iOffset, sSpacedHexDigits, sPrintable) ]

    return "\n".join (asLines)

    # end _hexDump

class TeradataCursor:

    def __init__(self, con):

        self.description = None # Required by DBAPI 2.0
        self.rowcount = -1 # Required by DBAPI 2.0
        self.arraysize = 1 # Required by DBAPI 2.0
        self.rownumber = None # Optional by DBAPI 2.0
        self.connection = con # Optional by DBAPI 2.0
        self.uRowsHandle = None
        self.bClosed = False

        # end __init__

    def callproc(self, sProcName, params=None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter callproc {}".format (self))
        try:
            sCall = "{call " + sProcName

            if params:
                sCall += " (" + ", ".join (["?"] * len (params)) + ")"

            sCall += "}"

            self.execute (sCall, params)

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave callproc {}".format (self))

        # end callproc

    def close(self): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter close {}".format (self))
        try:
            if not self.bClosed:
                self.bClosed = True
                self._closeRows ()
        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave close {}".format (self))

        # end close

    def _stopIfClosed (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _stopIfClosed {}".format (self))
        try:
            if self.bClosed:
                raise ProgrammingError ("Cursor is closed")
        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _stopIfClosed {}".format (self))

        # end _stopIfClosed

    def _closeRows (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _closeRows {}".format (self))
        try:
            if self.uRowsHandle:
                pcError = ctypes.POINTER (ctypes.c_char)()
                goside.goCloseRows (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError))

                self.uRowsHandle = None

                if pcError:
                    sErr = ctypes.string_at(pcError).decode('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError(sErr)

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _closeRows {}".format (self))

        # end _closeRows

    def execute (self, sOperation, params = None, ignoreErrors = None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter execute {}".format (self))
        try:
            if params and type (params) not in [list, tuple]:
                raise TypeError ("params unexpected type {}".format (type (params)))

            if not params:
                self.executemany (sOperation, None, ignoreErrors)

            elif type (params [0]) in [list, tuple]:
                # Excerpt from PEP 249 DBAPI documentation:
                #  The parameters may also be specified as list of tuples to e.g. insert multiple rows in a single
                #  operation, but this kind of usage is deprecated: .executemany() should be used instead.
                self.executemany (sOperation, params, ignoreErrors)

            else:
                self.executemany (sOperation, [params, ], ignoreErrors)

            return self

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave execute {}".format (self))

        # end execute

    def _obtainResultMetaData (self):

        if self.connection.bTraceLog:
            traceLog ("> enter _obtainResultMetaData {}".format (self))
        try:
            pcError = ctypes.POINTER (ctypes.c_char) ()
            uActivityCount = ctypes.c_uint64 ()
            pcColumnMetaData = ctypes.POINTER (ctypes.c_char) ()
            goside.goResultMetaData (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (uActivityCount), None, ctypes.byref (pcColumnMetaData))

            if pcError:
                sErr = ctypes.string_at (pcError).decode ('utf-8')
                goside.goFreePointer (self.connection.uLog, pcError)
                raise OperationalError (sErr)

            self.rowcount = uActivityCount.value

            if pcColumnMetaData:
                self.description = []
                i = 0
                while pcColumnMetaData [i] != b'Z': # Z=terminator
                    columnDesc = []

                    # (1) Column name
                    i = _deserializeString (pcColumnMetaData, i, columnDesc)

                    i = _deserializeString (pcColumnMetaData, i, None) # discard Type name

                    # (2) Type code
                    i = _deserializeString (pcColumnMetaData, i, columnDesc)

                    if columnDesc [-1] == 'b': # typeCode b=bytes
                        columnDesc [-1] = BINARY

                    elif columnDesc [-1] == 'd': # typeCode d=double
                        columnDesc [-1] = float

                    elif columnDesc [-1] in ('i', 'l'): # typeCode i=integer (int32), l=long (int64)
                        columnDesc [-1] = int

                    elif columnDesc [-1] == 'm': # typeCode m=number
                        columnDesc [-1] = decimal.Decimal

                    elif columnDesc [-1] == 's': # typeCode s=string
                        columnDesc [-1] = STRING

                    elif columnDesc [-1] == 'u': # typeCode u=date
                        columnDesc [-1] = datetime.date

                    elif columnDesc [-1] in ('v', 'w'): # typeCode v=time, w=time with time zone
                        columnDesc [-1] = datetime.time

                    elif columnDesc [-1] in ('x', 'y'): # typeCode x=timestamp, y=timestamp with time zone
                        columnDesc [-1] = datetime.datetime

                    # (3) Display size
                    columnDesc.append (None) # not provided

                    # (4) Max byte count
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (5) Precision
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (6) Scale
                    i = _deserializeLong (pcColumnMetaData, i, columnDesc)

                    # (7) Nullable
                    i = _deserializeBool (pcColumnMetaData, i, columnDesc)

                    self.description.append (columnDesc)

                    # end while

                goside.goFreePointer (self.connection.uLog, pcColumnMetaData)

                # end if pcColumnMetaData

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave _obtainResultMetaData {}".format (self))

        # end _obtainResultMetaData

    def executemany (self, sOperation, seqOfParams, ignoreErrors = None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter executemany {}".format (self))
        try:
            self._stopIfClosed ()
            self._closeRows ()

            if ignoreErrors:

                if type (ignoreErrors) == int:
                    ignoreErrors = [ignoreErrors]

                if type (ignoreErrors) not in [list, tuple]:
                    raise TypeError ("ignoreErrors unexpected type {}".format (type (ignoreErrors)))

                for i in range (0, len (ignoreErrors)):
                    if type (ignoreErrors [i]) != int:
                        raise TypeError ("ignoreErrors[{}] unexpected type {}".format (i, type (ignoreErrors [i])))

                setIgnoreErrorCodes = set (ignoreErrors)
            else:
                setIgnoreErrorCodes = set () # empty set

            dStartTime = time.time ()

            with io.BytesIO (b'') as osBindValues:

                if seqOfParams:

                    if type (seqOfParams) not in [list, tuple]:
                        raise TypeError ("seqOfParams unexpected type {}".format (type (seqOfParams)))

                    for i in range (0, len (seqOfParams)):

                        aoRowValues = seqOfParams [i]

                        if type (aoRowValues) not in [list, tuple]:
                            raise TypeError ("seqOfParams[{}] unexpected type {}".format (i, type (aoRowValues)))

                        if len (aoRowValues) == 0:
                            raise ValueError ("seqOfParams[{}] is zero length".format (i))

                        for j in range (0, len (aoRowValues)):

                            oValue = aoRowValues [j]

                            if isinstance (oValue, str):
                                aby = oValue.encode ("utf-8")
                                osBindValues.write (b'S')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, int):
                                osBindValues.write (b'L')
                                osBindValues.write (struct.pack (">q", oValue))
                                continue

                            if oValue is None:
                                osBindValues.write (b'N')
                                continue

                            if isinstance (oValue, float):
                                osBindValues.write (b'D')
                                osBindValues.write (struct.pack (">d", oValue))
                                continue

                            if isinstance (oValue, decimal.Decimal):
                                aby = "{:f}".format (oValue).encode ("utf-8") # avoid exponential notation
                                osBindValues.write (b'M')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.datetime): # check first because datetime is a subclass of date
                                aby = oValue.isoformat (" ").encode ("utf-8")
                                osBindValues.write (b'Y' if oValue.tzinfo else b'X')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.date):
                                aby = oValue.isoformat ().encode ("utf-8")
                                osBindValues.write (b'U')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.time):
                                aby = oValue.isoformat ().encode ("utf-8")
                                osBindValues.write (b'W' if oValue.tzinfo else b'V')
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, datetime.timedelta):
                                aby = _formatTimedelta (oValue).encode ("utf-8")
                                osBindValues.write (b'S') # serialized as string
                                osBindValues.write (struct.pack (">Q", len (aby)))
                                osBindValues.write (aby)
                                continue

                            if isinstance (oValue, bytes) or isinstance (oValue, bytearray):
                                osBindValues.write (b'B')
                                osBindValues.write (struct.pack (">Q", len (oValue)))
                                osBindValues.write (oValue)
                                continue

                            raise TypeError ("seqOfParams[{}][{}] unexpected type {}".format (i, j, type (oValue)))

                            # end for j

                        osBindValues.write (b'Z') # end of row terminator

                        # end for i
                    # end if seqOfParams

                osBindValues.write (b'Z') # end of all rows terminator

                abyBindValues = osBindValues.getvalue ()

                # end with osBindValues

            if self.connection.bTimingLog:
                timingLog ("executemany serialize bind values took {} ms and produced {} bytes".format ((time.time () - dStartTime) * 1000.0, len (abyBindValues)))

            dStartTime = time.time ()

            pcError = ctypes.POINTER (ctypes.c_char) ()
            uRowsHandle = ctypes.c_uint64 ()
            goside.goCreateRows (self.connection.uLog, self.connection.uConnHandle, sOperation.encode ('utf-8'), len (abyBindValues), abyBindValues, ctypes.byref (pcError), ctypes.byref (uRowsHandle))
            if pcError:
                sErr = ctypes.string_at (pcError).decode ('utf-8')
                goside.goFreePointer (self.connection.uLog, pcError)

                setErrorCodes = { int (s) for s in re.findall ("\\[Error (\\d+)\\]", sErr) }
                setIntersection = setErrorCodes & setIgnoreErrorCodes
                bIgnore = len (setIntersection) > 0 # ignore when intersection is non-empty
                if self.connection.bDebugLog:
                    debugLog ("executemany bIgnore={} setIntersection={} setErrorCodes={} setIgnoreErrorCodes={}".format (bIgnore, setIntersection, setErrorCodes, setIgnoreErrorCodes))
                if bIgnore:
                    return

                raise OperationalError (sErr)

            if self.connection.bTimingLog:
                timingLog ("executemany call to goCreateRows took {} ms".format ((time.time () - dStartTime) * 1000.0))

            self.uRowsHandle = uRowsHandle.value

            self._obtainResultMetaData ()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave executemany {}".format (self))

        # end executemany

    def fetchone(self): # Required by DBAPI 2.0

        try:
            return next(self)

        except StopIteration:
            return None

        # end fetchone

    def fetchmany(self, nDesiredRowCount=None): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter fetchmany {}".format (self))
        try:
            if nDesiredRowCount is None:
                nDesiredRowCount = self.arraysize

            rows = []
            nObservedRowCount = 0
            for row in self:
                rows.append(row)
                nObservedRowCount += 1
                if nObservedRowCount == nDesiredRowCount:
                    break

            return rows

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave fetchmany {}".format (self))

        # end fetchmany

    def fetchall(self): # Required by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter fetchall {}".format (self))
        try:
            rows = []
            for row in self:
                rows.append(row)

            return rows

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave fetchall {}".format (self))

        # end fetchall

    def nextset(self): # Optional by DBAPI 2.0

        if self.connection.bTraceLog:
            traceLog ("> enter nextset {}".format (self))
        try:
            self._stopIfClosed ()

            if self.uRowsHandle:

                pcError = ctypes.POINTER (ctypes.c_char)()
                cAvail = ctypes.c_char()

                goside.goNextResult (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (cAvail))

                if pcError:
                    sErr = ctypes.string_at(pcError).decode('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError(sErr)

                if cAvail.value == b'Y':
                    self._obtainResultMetaData ()
                else:
                    self.description = None
                    self.rowcount = -1

                return cAvail.value == b'Y'

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave nextset {}".format (self))

        # end nextset

    def setinputsizes(self, sizes): # Required by DBAPI 2.0
        self._stopIfClosed ()

    def setoutputsize(self, size, column=None): # Required by DBAPI 2.0
        self._stopIfClosed ()

    def __iter__(self): # Implements iterable # Optional by DBAPI 2.0
        return self

    def __next__(self): # Implements Python 3 iterator

        if self.connection.bTraceLog:
            traceLog ("> enter __next__ {}".format (self))
        try:
            self._stopIfClosed ()

            if self.uRowsHandle:

                pcError = ctypes.POINTER (ctypes.c_char)()
                nColumnValuesByteCount = ctypes.c_int32 ()
                pcColumnValues = ctypes.POINTER (ctypes.c_char)()

                goside.goFetchRow (self.connection.uLog, self.uRowsHandle, ctypes.byref (pcError), ctypes.byref (nColumnValuesByteCount), ctypes.byref (pcColumnValues))

                if pcError:
                    sErr = ctypes.string_at (pcError).decode ('utf-8')
                    goside.goFreePointer (self.connection.uLog, pcError)
                    raise OperationalError (sErr)

                if pcColumnValues:

                    if self.connection.bDebugLog and nColumnValuesByteCount:
                        debugLog ("__next__ nColumnValuesByteCount={}\n{}".format (nColumnValuesByteCount.value, _hexDump (ctypes.string_at (pcColumnValues, nColumnValuesByteCount))))

                    row = []
                    i = 0
                    while pcColumnValues [i] != b'Z': # Z=terminator

                        if pcColumnValues [i] == b'N': # N=null
                            iNew = _deserializeNull (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'B': # B=bytes
                            iNew = _deserializeBytes (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'D': # D=double
                            iNew = _deserializeDouble (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'I': # I=integer
                            iNew = _deserializeInt (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'L': # L=long
                            iNew = _deserializeLong (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'M': # M=number
                            iNew = _deserializeNumber (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'S': # S=string
                            iNew = _deserializeString (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'U': # U=date
                            iNew = _deserializeDate (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'V': # V=time
                            iNew = _deserializeTime (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'W': # W=time with time zone
                            iNew = _deserializeTimeWithTimeZone (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'X': # X=timestamp
                            iNew = _deserializeTimestamp (pcColumnValues, i, row)

                        elif pcColumnValues [i] == b'Y': # Y=timestamp with time zone
                            iNew = _deserializeTimestampWithTimeZone (pcColumnValues, i, row)

                        else:
                            raise OperationalError ('Unrecognized column type {} at byte offset {}'.format (pcColumnValues [i], i))

                        if self.connection.bDebugLog:
                            debugLog ("__next__ row[{}] typeCode={} type={} value={}".format (len (row) - 1, pcColumnValues [i], type (row [-1]), row [-1]))

                        i = iNew

                        # end while

                    goside.goFreePointer (self.connection.uLog, pcColumnValues)

                    return row

                    # end if pcColumnValues

                # end if self.uRowsHandle

            raise StopIteration ()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave __next__ {}".format (self))

        # end __next__

    def next(self): # Implements Python 2 iterator # Optional by DBAPI 2.0
        return self.__next__()

    def __enter__(self): # Implements with-statement context manager
        return self

    def __exit__(self, t, value, traceback): # Implements with-statement context manager

        if self.connection.bTraceLog:
            traceLog ("> enter __exit__ {}".format (self))
        try:
            self.close()

        finally:
            if self.connection.bTraceLog:
                traceLog ("< leave __exit__ {}".format (self))

        # end __exit__

    def __repr__(self): # Equivalent to the toString method in Java or the String method in Go
        return "{} uRowsHandle={} bClosed={}".format (self.__class__.__name__, self.uRowsHandle, self.bClosed)

    # end class TeradataCursor
