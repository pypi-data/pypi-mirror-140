###############################################
#
# Now available: developmental python x3d.py package on PyPi for import.
#   This approach greatly simplifies Python X3D deployment and use.
#   https://pypi.org/project/x3d
#
# Alpha release July 2019:
#   https://twitter.com/Web3DConsortium/status/1154449868846297088
#
# Developer options for loading x3d package:
#
#    from x3d import *  # preferred approach, terser source that avoids x3d.* class prefixes
#
# or
#    import x3d         # traditional way to subclass x3d package, all classes require x3d.* prefix
#                       # but python source is very verbose, for example x3d.Material x3d.Shape etc.
#                       # X3dToPython.xslt stylesheet insertPackagePrefix=true supports this option.

print ('===================')
print ('Importing local development copy of X3D package:')
print ('  from x3d import *')

from x3d import *

print ('===================')

###############################################

print ('PythonX3dSmokeTests:')
print ()

print ('- - - - - - - - - -')

print ('Access types:', AccessType.initializeOnly(), AccessType.inputOutput(), AccessType.inputOnly(), AccessType.outputOnly())

assertionComment = '# execution continues if no assertion failure occurs'

print ('- - - - - - - - - -')

print ('SFBool.NAME()         = ' +     SFBool.NAME());
print ('SFBool.DEFAULT_VALUE()= ' + str(SFBool.DEFAULT_VALUE()));
print ('SFBool.ARRAY_TYPE()   = ' + str(SFBool.ARRAY_TYPE()));
print ('SFBool.TUPLE_SIZE()   = ' + str(SFBool.TUPLE_SIZE()));
print ('SFBool.REGEX_PYTHON() = ' + str(SFBool.REGEX_PYTHON()));
print ('SFBool.REGEX_XML()    = ' + str(SFBool.REGEX_XML()));
print ('SFBool.TOOLTIP_URL()  = ' + str(SFBool.TOOLTIP_URL()));
test = True         # fails in isolation, ignores object type (not an SFBool object)
test = SFBool()     # default value True
test = SFBool(None) # default value True
test = True         # works, uses object type (must be already declared as an SFBool object)
test = SFBool(True)
test = SFBool(False)
test = SFBool(value=True)
test = SFBool(value=False)
test = SFBool('True')
test = SFBool('False')
test = SFBool('true')
test = SFBool('false')
test.value = 'false'    # works
test =  SFBool('false') # works, can initialize object with string
test =  SFBool([False]) # works, wrapped in singleton list
test =  SFBool((False)) # works, wrapped in singleton tuple
PLAIN_TEXT = 'plain text'
# https://stackoverflow.com/questions/18176602/how-to-get-the-name-of-an-exception-that-was-caught-in-python
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFBool " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
#test = 'false'         # always fails, overrides object type as ordinary string
print ('SFBool fixBoolean(test)=', fixBoolean(test), 'type=' + str(type(fixBoolean(test))))
print ('SFBool test       =', test)
print ('SFBool value type =', type(test.value))
print ('isinstance SFBool =', isinstance(test,SFBool))
print ('SFBool test.value =', test.value)
print ('SFBool test.XML() =', test.XML())
print ('SFBool test.VRML()=', test.VRML())
print ('SFBool test.JSON()=', test.JSON())
print ('SFBool regex match=',
             # 're.fullmatch(      SFBool.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFBool.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFBool.REGEX_PYTHON(),          str(test.value)))
print ('SFBool     isValidSFBool(test)=' + str(isValidSFBool(test)), flush=True)
print ('SFBool assertValidSFBool(test)', assertionComment,flush=True); assertValidSFBool(test);
print()

print ('MFBool.NAME()         = ' +     MFBool.NAME());
print ('MFBool.DEFAULT_VALUE()= ' + str(MFBool.DEFAULT_VALUE()));
print ('MFBool.ARRAY_TYPE()   = ' + str(MFBool.ARRAY_TYPE()));
print ('MFBool.TUPLE_SIZE()   = ' + str(MFBool.TUPLE_SIZE()));
print ('MFBool.REGEX_PYTHON() = ' + str(MFBool.REGEX_PYTHON()));
print ('MFBool.REGEX_XML()    = ' + str(MFBool.REGEX_XML()));
print ('MFBool.TOOLTIP_URL()  = ' + str(MFBool.TOOLTIP_URL()));
test = MFBool()
test = MFBool(None) # empty list
test = MFBool('False')
test = MFBool(True)
test = MFBool([True])
test = MFBool([False])
test = MFBool([True,False,'True','False','true','false']) # mixed types, None is not a valid value
test.value = [True,False,]
test.append(True)
test.append('false')
test.append(SFBool(True))
test.append([True,False])
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFBool " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
#test.append(MFBool([True,False])) # fails, TODO make MF array objects iterable
#test = 'false'            # always fails, overrides object type as ordinary string
#test = MFBool(True,False) # always fails due to incorrect parameterization, TODO consider alternatives
print ('MFBool fixBoolean(test)=', fixBoolean(test), 'type=' + str(type(fixBoolean(test))))
print ('MFBool test       =', test)
print ('MFBool value type =', type(test.value))
print ('isinstance MFBool =', isinstance(test,MFBool))
print ('MFBool test.value =', test.value)
print ('MFBool test.XML() =', test.XML())
print ('MFBool test.VRML()=', test.VRML())
print ('MFBool test.JSON()=', test.JSON())
print ('MFBool regex match=',
             # 're.fullmatch(      MFBool.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFBool.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFBool.REGEX_PYTHON(),          str(test.value)))
print ('MFBool     isValidMFBool(test)=' + str(isValidMFBool(test)), flush=True)
print ('MFBool assertValidMFBool(test)', assertionComment,flush=True); assertValidMFBool(test)
print ('MFBool bool(test)=' + str(bool(test)) + ', len(test)=' + str(len(test))); # must be array

test = SFBool(MFBool([True])) # downcast legal singleton
print ('MFBool test downcast legal singleton: SFBool(MFBool([True]))=' + str(test) + ', type=' + str(type(test)))
test = MFBool(SFBool(False)) # upcast legal SF value
print ('MFBool test   upcast legal SF value:  MFBool(SFBool(False))=' + str(test) + ', type=' + str(type(test)))

print ('- - - - - - - - - -')

print ('SFInt32.NAME()         = ' +     SFInt32.NAME());
print ('SFInt32.DEFAULT_VALUE()= ' + str(SFInt32.DEFAULT_VALUE()));
print ('SFInt32.ARRAY_TYPE()   = ' + str(SFInt32.ARRAY_TYPE()));
print ('SFInt32.TUPLE_SIZE()   = ' + str(SFInt32.TUPLE_SIZE()));
print ('SFInt32.REGEX_PYTHON() = ' + str(SFInt32.REGEX_PYTHON()));
print ('SFInt32.REGEX_XML()    = ' + str(SFInt32.REGEX_XML()));
print ('SFInt32.TOOLTIP_URL()  = ' + str(SFInt32.TOOLTIP_URL()));
test = SFInt32()
test = SFInt32(-11)
test = SFInt32('+22')
test.value = 11
test.value = '111'
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFInt32 " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
print('SFInt32 isZeroToOne        (-1)  =' + str(isZeroToOne        (-1)) +   ', isZeroToOne        (0)  ='  + str(isZeroToOne        (0))   + ',  isZeroToOne        (+1) =' + str(isZeroToOne  (+1)))
print('SFInt32 isNonNegative      (-1)  =' + str(isNonNegative      (-1)) +   ', isNonNegative      (0)  ='  + str(isNonNegative      (0))   + ',  isNonNegative      (+1) =' + str(isNonNegative(+1)))
print('SFInt32 isPositive         (-1)  =' + str(isPositive         (-1)) +   ', isPositive         (0)  ='  + str(isPositive         (0))   +  ', isPositive         (+1) =' + str(isPositive   (+1)))
print('SFInt32 isGreaterThan      (-1,0)=' + str(isGreaterThan      (-1,0)) +  ', isGreaterThan      (0,0)=' + str(isGreaterThan      (0,0)) +  ', isGreaterThan      (1,0)=' + str(isGreaterThan(1,0)))
print('SFInt32 isGreaterThanEquals(-1,0)=' + str(isGreaterThanEquals(-1,0)) +  ', isGreaterThanEquals(0,0)=' + str(isGreaterThanEquals(0,0)) + ',  isGreaterThanEquals(1,0)=' + str(isGreaterThanEquals(1,0)))
print('SFInt32 isLessThan         (-1,0)=' + str(isLessThan         (-1,0)) + ',  isLessThan         (0,0)=' + str(isLessThan         (0,0)) +  ', isLessThan         (1,0)=' + str(isLessThan         (1,0)))
print('SFInt32 isLessThanEquals   (-1,0)=' + str(isLessThanEquals   (-1,0)) + ',  isLessThanEquals   (0,0)=' + str(isLessThanEquals   (0,0)) + ',  isLessThanEquals   (1,0)=' + str(isLessThanEquals   (1,0)))
#TODO
print ('SFInt32 test       =', test)
print ('SFInt32 value type =', type(test.value))
print ('isinstance SFInt32 =', isinstance(test,SFInt32))
print ('SFInt32 test.value =', test.value)
print ('SFInt32 test.XML() =', test.XML())
print ('SFInt32 test.VRML()=', test.VRML())
print ('SFInt32 test.JSON()=', test.JSON())
print ('SFInt32 regex match=',
             # 're.fullmatch(      SFInt32.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFInt32.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFInt32.REGEX_PYTHON(),          str(test.value)))
print ('SFInt32     isValidSFInt32(test)=' + str(isValidSFInt32(test)), flush=True)
print ('SFInt32 assertValidSFInt32(test)', assertionComment,flush=True); assertValidSFInt32(test)
print()

print ('MFInt32.NAME()         = ' +     MFInt32.NAME());
print ('MFInt32.DEFAULT_VALUE()= ' + str(MFInt32.DEFAULT_VALUE()));
print ('MFInt32.ARRAY_TYPE()   = ' + str(MFInt32.ARRAY_TYPE()));
print ('MFInt32.TUPLE_SIZE()   = ' + str(MFInt32.TUPLE_SIZE()));
print ('MFInt32.REGEX_PYTHON() = ' + str(MFInt32.REGEX_PYTHON()));
print ('MFInt32.REGEX_XML()    = ' + str(MFInt32.REGEX_XML()));
print ('MFInt32.TOOLTIP_URL()  = ' + str(MFInt32.TOOLTIP_URL()));
test = MFInt32()
test = MFInt32(11)
test = MFInt32('-22')
test = MFInt32(SFInt32('+99'))
test = MFInt32([11,22,33])
test.append(44)
test.append('-55')
test.append(SFInt32('-66'))
test.append(77)
test.append('-88')
test.append(SFInt32('+99'))
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFInt32 " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
#test.append(MFInt32(SFInt32('+99'))) # TODO make MFInt32 iterable
#test = MFInt32( 1,2,3,4 ) # always fails, invalid positional arguments
#test.value = ['1',2,3,4,5,6] # TODO mixed types
#test.value = [1,2,3,4,5,6]
print ('MFInt32 test       =', test)
print ('MFInt32 value type =', type(test.value))
print ('isinstance MFInt32 =', isinstance(test,MFInt32))
print ('MFInt32 test.value =', test.value)
print ('MFInt32 test.XML() =', test.XML())
print ('MFInt32 test.VRML()=', test.VRML())
print ('MFInt32 test.JSON()=', test.JSON())
print ('MFInt32 regex match=',
             # 're.fullmatch(      MFInt32.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFInt32.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFInt32.REGEX_PYTHON(),          str(test.value)))
print ('MFInt32     isValidMFInt32(test)=' + str(isValidMFInt32(test)), flush=True)
print ('MFInt32 assertValidMFInt32(test)', assertionComment,flush=True); assertValidMFInt32(test)
print ('MFInt32 bool(test)=' + str(bool(test)) + ', len(test)=' + str(len(test))); # must be array

test = SFInt32(MFInt32([1])) # downcast legal singleton
print ('SFInt32 test downcast legal singleton: SFInt32(MFInt32([1]))=' + str(test) + ', type=' + str(type(test)))
test = MFInt32(SFInt32(2)) # upcast legal SF value
print ('MFInt32 test   upcast legal SF value:  MFInt32(SFInt32(2))=' + str(test) + ', type=' + str(type(test)))

#exit()

print ('- - - - - - - - - -')

print ('SFFloat.NAME()         = ' +     SFFloat.NAME());
print ('SFFloat.DEFAULT_VALUE()= ' + str(SFFloat.DEFAULT_VALUE()));
print ('SFFloat.ARRAY_TYPE()   = ' + str(SFFloat.ARRAY_TYPE()));
print ('SFFloat.TUPLE_SIZE()   = ' + str(SFFloat.TUPLE_SIZE()));
print ('SFFloat.REGEX_PYTHON() = ' + str(SFFloat.REGEX_PYTHON()));
print ('SFFloat.REGEX_XML()    = ' + str(SFFloat.REGEX_XML()));
print ('SFFloat.TOOLTIP_URL()  = ' + str(SFFloat.TOOLTIP_URL()));
test = SFFloat()
test = SFFloat(-11)
test = SFFloat('-22')
test.value = 33
test.value = '44'
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFFloat " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFFloat test       =', test)
print ('SFFloat value type =', type(test.value))
print ('isinstance SFFloat =', isinstance(test,SFFloat))
print ('SFFloat test.value =', test.value)
print ('SFFloat test.XML() =', test.XML())
print ('SFFloat test.VRML()=', test.VRML())
print ('SFFloat regex match=',
             # 're.fullmatch(      SFFloat.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFFloat.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFFloat.REGEX_PYTHON(),          str(test.value)))
print ('SFFloat     isValidSFFloat(test)=' + str(isValidSFFloat(test)), flush=True)
print ('SFFloat assertValidSFFloat(test)', assertionComment,flush=True); assertValidSFFloat(test)
print()

print ('MFFloat.NAME()         = ' +     MFFloat.NAME());
print ('MFFloat.DEFAULT_VALUE()= ' + str(MFFloat.DEFAULT_VALUE()));
print ('MFFloat.ARRAY_TYPE()   = ' + str(MFFloat.ARRAY_TYPE()));
print ('MFFloat.TUPLE_SIZE()   = ' + str(MFFloat.TUPLE_SIZE()));
print ('MFFloat.REGEX_PYTHON() = ' + str(MFFloat.REGEX_PYTHON()));
print ('MFFloat.REGEX_XML()    = ' + str(MFFloat.REGEX_XML()));
print ('MFFloat.TOOLTIP_URL()  = ' + str(MFFloat.TOOLTIP_URL()));
test = MFFloat()
test = MFFloat([0,1,2])
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFFloat " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFFloat( 1,2,3,4 )
print ('MFFloat test       =', test)
print ('MFFloat value type =', type(test.value))
print ('isinstance MFFloat =', isinstance(test,MFFloat))
print ('MFFloat test.value =', test.value)
print ('MFFloat test.XML() =', test.XML())
print ('MFFloat test.VRML()=', test.VRML())
print ('MFFloat test.JSON()=', test.JSON())
print ('MFFloat regex match=',
             # 're.fullmatch(      MFFloat.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFFloat.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFFloat.REGEX_PYTHON(),          str(test.value)))
print ('MFFloat     isValidMFFloat(test)=' + str(isValidMFFloat(test)), flush=True)
print ('MFFloat assertValidMFFloat(test)', assertionComment,flush=True); assertValidMFFloat(test)

#test = SFFloat(MFFloat([1])) # downcast legal singleton
#print ('SFFloat test downcast legal singleton: SFFloat(MFFloat([1]))=' + str(test) + ', type=' + str(type(test)))
#test = MFFloat(SFFloat(2)) # upcast legal SF value
#print ('MFFloat test   upcast legal SF value:  MFFloat(SFFloat(2))=' + str(test) + ', type=' + str(type(test)))

print ('- - - - - - - - - -')

print ('SFDouble.NAME()         = ' +     SFDouble.NAME());
print ('SFDouble.DEFAULT_VALUE()= ' + str(SFDouble.DEFAULT_VALUE()));
print ('SFDouble.ARRAY_TYPE()   = ' + str(SFDouble.ARRAY_TYPE()));
print ('SFDouble.TUPLE_SIZE()   = ' + str(SFDouble.TUPLE_SIZE()));
print ('SFDouble.REGEX_PYTHON() = ' + str(SFDouble.REGEX_PYTHON()));
print ('SFDouble.REGEX_XML()    = ' + str(SFDouble.REGEX_XML()));
print ('SFDouble.TOOLTIP_URL()  = ' + str(SFDouble.TOOLTIP_URL()));
test = SFDouble()
test = SFDouble(-11)
test = SFDouble('-55')
test.value = 1
test.value = '66'
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFDouble " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFDouble test       =', test)
print ('SFDouble value type =', type(test.value))
print ('isinstance SFDouble =', isinstance(test,SFDouble))
print ('SFDouble test.value =', test.value)
print ('SFDouble test.XML() =', test.XML())
print ('SFDouble test.VRML()=', test.VRML())
print ('SFDouble test.JSON()=', test.JSON())
print ('SFDouble regex match=',
             # 're.fullmatch(      SFDouble.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFDouble.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFDouble.REGEX_PYTHON(),          str(test.value)))
print ('SFDouble     isValidSFDouble(test)=' + str(isValidSFDouble(test)), flush=True)
print ('SFDouble assertValidSFDouble(test)', assertionComment,flush=True); assertValidSFDouble(test)
print()

print ('MFDouble.NAME()         = ' +     MFDouble.NAME());
print ('MFDouble.DEFAULT_VALUE()= ' + str(MFDouble.DEFAULT_VALUE()));
print ('MFDouble.ARRAY_TYPE()   = ' + str(MFDouble.ARRAY_TYPE()));
print ('MFDouble.TUPLE_SIZE()   = ' + str(MFDouble.TUPLE_SIZE()));
print ('MFDouble.REGEX_PYTHON() = ' + str(MFDouble.REGEX_PYTHON()));
print ('MFDouble.REGEX_XML()    = ' + str(MFDouble.REGEX_XML()));
print ('MFDouble.TOOLTIP_URL()  = ' + str(MFDouble.TOOLTIP_URL()));
test = MFDouble()
test = MFDouble([0,1,2])
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFDouble " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFDouble( 1,2,3,4 )
print ('MFDouble test       =', test)
print ('MFDouble value type =', type(test.value))
print ('isinstance MFDouble =', isinstance(test,MFDouble))
print ('MFDouble test.value =', test.value)
print ('MFDouble test.XML() =', test.XML())
print ('MFDouble test.VRML()=', test.VRML())
print ('MFDouble test.JSON()=', test.JSON())
print ('MFDouble regex match=',
             # 're.fullmatch(      MFDouble.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFDouble.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFDouble.REGEX_PYTHON(),          str(test.value)))
print ('MFDouble     isValidMFDouble(test)=' + str(isValidMFDouble(test)), flush=True)
print ('MFDouble assertValidMFDouble(test)', assertionComment,flush=True); assertValidMFDouble(test)

#test = SFDouble(MFDouble([1])) # downcast legal singleton
#print ('SFDouble test downcast legal singleton: SFDouble(MFDouble(1))=' + str(test) + ', type=' + str(type(test)))
#test = MFDouble(SFDouble(2)) # upcast legal SF value
#print ('MFDouble test   upcast legal SF value:  MFDouble(SFDouble(2))=' + str(test) + ', type=' + str(type(test)))

print ('- - - - - - - - - -')

print ('SFString.NAME()         = ' +     SFString.NAME());
print ('SFString.DEFAULT_VALUE()= "' + str(SFString.DEFAULT_VALUE()) + '"');
print ('SFString.ARRAY_TYPE()   = ' + str(SFString.ARRAY_TYPE()));
print ('SFString.TUPLE_SIZE()   = ' + str(SFString.TUPLE_SIZE()));
print ('SFString.REGEX_PYTHON() = ' + str(SFString.REGEX_PYTHON()));
print ('SFString.REGEX_XML()    = ' + str(SFString.REGEX_XML()));
print ('SFString.TOOLTIP_URL()  = ' + str(SFString.TOOLTIP_URL()));
test = SFString()
test = SFString('test constructor')
test.value = 'test setter'
print ('SFString test       =', test)
print ('SFString value type =', type(test.value))
print ('isinstance SFString =', isinstance(test,SFString))
print ('SFString test.value =', test.value)
print ('SFString test.XML() =', test.XML())
print ('SFString test.VRML()=', test.VRML())
print ('SFString test.JSON()=', test.JSON())
print ('SFString regex match=',
             # 're.fullmatch(      SFString.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFString.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFString.REGEX_PYTHON(),          str(test.value)))
print ('SFString     isValidSFString(test)=' + str(isValidSFString(test)), flush=True)
print ('SFString assertValidSFString(test)', assertionComment,flush=True); assertValidSFString(test)
print()

print ('MFString.NAME()         = ' +     MFString.NAME());
print ('MFString.DEFAULT_VALUE()= ' + str(MFString.DEFAULT_VALUE()));
print ('MFString.ARRAY_TYPE()   = ' + str(MFString.ARRAY_TYPE()));
print ('MFString.TUPLE_SIZE()   = ' + str(MFString.TUPLE_SIZE()));
print ('MFString.REGEX_PYTHON() = ' + str(MFString.REGEX_PYTHON()));
print ('MFString.REGEX_XML()    = ' + str(MFString.REGEX_XML()));
print ('MFString.TOOLTIP_URL()  = ' + str(MFString.TOOLTIP_URL()));
test = MFString()
# test = MFString( 'hello', 'test' ) # TODO
# test.value = ['test', 'setters and getters']
test = MFString(['test', 'constructor','with\'apostrophe']) # comma necessary or python catenates strings
print ('MFString test       =', test)
print ('MFString value type =', type(test.value))
print ('isinstance MFString =', isinstance(test,MFString))
print ('MFString test.value =', test.value)
print ('MFString test.XML() =', test.XML())
print ('MFString test.VRML()=', test.VRML())
print ('MFString test.JSON()=', test.JSON())
print ('MFString regex match=',
             # 're.fullmatch(      MFString.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFString.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFString.REGEX_PYTHON(),          str(test.value)))
print ('MFString     isValidMFString(test)=' + str(isValidMFString(test)), flush=True)
print ('MFString assertValidMFString(test)', assertionComment,flush=True); assertValidMFString(test)

#test = SFString(MFString(["one"])) # downcast legal singleton
#print ('SFString test downcast legal singleton: SFString(MFString(["one"]))=' + str(test) + ', type=' + str(type(test)))
#test = MFString(SFString("two")) # upcast legal SF value
#print ('MFString test   upcast legal SF value:  MFString(SFString("two"))=' + str(test) + ', type=' + str(type(test)))

print ('- - - - - - - - - -')

print ('SFVec2f.NAME()         = ' +     SFVec2f.NAME());
print ('SFVec2f.DEFAULT_VALUE()= ' + str(SFVec2f.DEFAULT_VALUE()));
print ('SFVec2f.ARRAY_TYPE()   = ' + str(SFVec2f.ARRAY_TYPE()));
print ('SFVec2f.TUPLE_SIZE()   = ' + str(SFVec2f.TUPLE_SIZE()));
print ('SFVec2f.REGEX_PYTHON() = ' + str(SFVec2f.REGEX_PYTHON()));
print ('SFVec2f.REGEX_XML()    = ' + str(SFVec2f.REGEX_XML()));
print ('SFVec2f.TOOLTIP_URL()  = ' + str(SFVec2f.TOOLTIP_URL()));
test = SFVec2f()
test = SFVec2f((-1, -2)) # commas required
test.value = (1, 2)      # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec2f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec2f test       =', test)
print ('SFVec2f value type =', type(test.value))
print ('isinstance SFVec2f =', isinstance(test,SFVec2f))
print ('SFVec2f test.value =', test.value)
print ('SFVec2f test.XML() =', test.XML())
print ('SFVec2f test.VRML()=', test.VRML())
print ('SFVec2f test.JSON()=', test.JSON())
print ('SFVec2f regex match=',
             # 're.fullmatch(      SFVec2f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec2f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec2f.REGEX_PYTHON(),          str(test.value)))
print ('SFVec2f     isValidSFVec2f(test)=' + str(isValidSFVec2f(test)), flush=True)
print ('SFVec2f assertValidSFVec2f(test)', assertionComment,flush=True); assertValidSFVec2f(test)
print()

print ('MFVec2f.NAME()         = ' +     MFVec2f.NAME());
print ('MFVec2f.DEFAULT_VALUE()= ' + str(MFVec2f.DEFAULT_VALUE()));
print ('MFVec2f.ARRAY_TYPE()   = ' + str(MFVec2f.ARRAY_TYPE()));
print ('MFVec2f.TUPLE_SIZE()   = ' + str(MFVec2f.TUPLE_SIZE()));
print ('MFVec2f.REGEX_PYTHON() = ' + str(MFVec2f.REGEX_PYTHON()));
print ('MFVec2f.REGEX_XML()    = ' + str(MFVec2f.REGEX_XML()));
print ('MFVec2f.TOOLTIP_URL()  = ' + str(MFVec2f.TOOLTIP_URL()));
test = MFVec2f()
# commas are typically required
test = MFVec2f((1,-2)) 
#test = MFVec2f([(1,-2)]) 
#test = MFVec2f([(-1,-2),(-3,-4)])
#test.value =   [(0,1),(2,3)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec2f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec2f( 1,2,3,4 )
print ('MFVec2f test       =', test)
print ('MFVec2f value type =', type(test.value))
print ('isinstance MFVec2f =', isinstance(test,MFVec2f))
print ('MFVec2f test.value =', test.value)
print ('MFVec2f test.XML() =', test.XML())
print ('MFVec2f test.VRML()=', test.VRML())
print ('MFVec2f test.JSON()=', test.JSON())
print ('MFVec2f regex match=',
             # 're.fullmatch(      MFVec2f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec2f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec2f.REGEX_PYTHON(),          str(test.value)))
print ('MFVec2f     isValidMFVec2f(test)=' + str(isValidMFVec2f(test)), flush=True)
print ('MFVec2f assertValidMFVec2f(test)', assertionComment,flush=True); assertValidMFVec2f(test)

#test = SFVec2f(MFVec2f([(11,12)])) # downcast legal singleton
#print ('SFVec2f test downcast legal singleton: SFVec2f(MFVec2f([(11,12)]))=' + str(test) + ', type=' + str(type(test)))
#test = MFVec2f(SFVec2f((21,22))) # upcast legal SF value
#print ('MFVec2f test   upcast legal SF value:  MFVec2f(SFVec2f((21,22)))=' + str(test) + ', type=' + str(type(test)))

# exit()

print ('- - - - - - - - - -')

print ('SFVec2d.NAME()         = ' +     SFVec2d.NAME());
print ('SFVec2d.DEFAULT_VALUE()= ' + str(SFVec2d.DEFAULT_VALUE()));
print ('SFVec2d.ARRAY_TYPE()   = ' + str(SFVec2d.ARRAY_TYPE()));
print ('SFVec2d.TUPLE_SIZE()   = ' + str(SFVec2d.TUPLE_SIZE()));
print ('SFVec2d.REGEX_PYTHON() = ' + str(SFVec2d.REGEX_PYTHON()));
print ('SFVec2d.REGEX_XML()    = ' + str(SFVec2d.REGEX_XML()));
print ('SFVec2d.TOOLTIP_URL()  = ' + str(SFVec2d.TOOLTIP_URL()));
test = SFVec2d()
test = SFVec2d((-1, -2)) # commas required
test.value = (1, 2)      # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec2d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec2d test       =', test)
print ('SFVec2d value type =', type(test.value))
print ('isinstance SFVec2d =', isinstance(test,SFVec2d))
print ('SFVec2d test.value =', test.value)
print ('SFVec2d test.XML() =', test.XML())
print ('SFVec2d test.VRML()=', test.VRML())
print ('SFVec2d test.JSON()=', test.JSON())
print ('SFVec2d regex match=',
             # 're.fullmatch(      SFVec2d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec2d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec2d.REGEX_PYTHON(),          str(test.value)))
print ('SFVec2d     isValidSFVec2d(test)=' + str(isValidSFVec2d(test)), flush=True)
print ('SFVec2d assertValidSFVec2d(test)', assertionComment,flush=True); assertValidSFVec2d(test)
print()

print ('MFVec2d.NAME()         = ' +     MFVec2d.NAME());
print ('MFVec2d.DEFAULT_VALUE()= ' + str(MFVec2d.DEFAULT_VALUE()));
print ('MFVec2d.ARRAY_TYPE()   = ' + str(MFVec2d.ARRAY_TYPE()));
print ('MFVec2d.TUPLE_SIZE()   = ' + str(MFVec2d.TUPLE_SIZE()));
print ('MFVec2d.REGEX_PYTHON() = ' + str(MFVec2d.REGEX_PYTHON()));
print ('MFVec2d.REGEX_XML()    = ' + str(MFVec2d.REGEX_XML()));
print ('MFVec2d.TOOLTIP_URL()  = ' + str(MFVec2d.TOOLTIP_URL()));
test = MFVec2d()
test = MFVec2d([(-1,-2),(-3,-4)]) # commas required
test.value =   [(0,1),(2,3)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec2d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec2d( 1,2,3,4 )
print ('MFVec2d test       =', test)
print ('MFVec2d value type =', type(test.value))
print ('isinstance MFVec2d =', isinstance(test,MFVec2d))
print ('MFVec2d test.value =', test.value)
print ('MFVec2d test.XML() =', test.XML())
print ('MFVec2d test.VRML()=', test.VRML())
print ('MFVec2d test.JSON()=', test.JSON())
print ('MFVec2d regex match=',
             # 're.fullmatch(      MFVec2d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec2d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec2d.REGEX_PYTHON(),          str(test.value)))
print ('MFVec2d     isValidMFVec2d(test)=' + str(isValidMFVec2d(test)), flush=True)
print ('MFVec2d assertValidMFVec2d(test)', assertionComment,flush=True); assertValidMFVec2d(test)

print ('- - - - - - - - - -')

print ('SFVec3f.NAME()         = ' +     SFVec3f.NAME());
print ('SFVec3f.DEFAULT_VALUE()= ' + str(SFVec3f.DEFAULT_VALUE()));
print ('SFVec3f.ARRAY_TYPE()   = ' + str(SFVec3f.ARRAY_TYPE()));
print ('SFVec3f.TUPLE_SIZE()   = ' + str(SFVec3f.TUPLE_SIZE()));
print ('SFVec3f.REGEX_PYTHON() = ' + str(SFVec3f.REGEX_PYTHON()));
print ('SFVec3f.REGEX_XML()    = ' + str(SFVec3f.REGEX_XML()));
print ('SFVec3f.TOOLTIP_URL()  = ' + str(SFVec3f.TOOLTIP_URL()));
test = SFVec3f()
test = SFVec3f((-1, -2, -3)) # commas required
test.value = (1, 2, 3)       # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec3f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec3f test       =', test)
print ('SFVec3f value type =', type(test.value))
print ('isinstance SFVec3f =', isinstance(test,SFVec3f))
print ('SFVec3f test.value =', test.value)
print ('SFVec3f test.XML() =', test.XML())
print ('SFVec3f test.VRML()=', test.VRML())
print ('SFVec3f test.JSON()=', test.JSON())
print ('SFVec3f regex match=',
             # 're.fullmatch(      SFVec3f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec3f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec3f.REGEX_PYTHON(),          str(test.value)))
print ('SFVec3f     isValidSFVec3f(test)=' + str(isValidSFVec3f(test)), flush=True)
print ('SFVec3f assertValidSFVec3f(test)', assertionComment,flush=True); assertValidSFVec3f(test)
print()

print ('MFVec3f.NAME()         = ' +     MFVec3f.NAME());
print ('MFVec3f.DEFAULT_VALUE()= ' + str(MFVec3f.DEFAULT_VALUE()));
print ('MFVec3f.ARRAY_TYPE()   = ' + str(MFVec3f.ARRAY_TYPE()));
print ('MFVec3f.TUPLE_SIZE()   = ' + str(MFVec3f.TUPLE_SIZE()));
print ('MFVec3f.REGEX_PYTHON() = ' + str(MFVec3f.REGEX_PYTHON()));
print ('MFVec3f.REGEX_XML()    = ' + str(MFVec3f.REGEX_XML()));
print ('MFVec3f.TOOLTIP_URL()  = ' + str(MFVec3f.TOOLTIP_URL()));
test = MFVec3f()
test = MFVec3f([(-1,-2,-3),(-4,-5,-6)]) # commas required
test.value =   [(0,1,2),(3,4,5)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec3f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec3f( 1,2,3,4,5,6 )
print ('MFVec3f test       =', test)
print ('MFVec3f value type =', type(test.value))
print ('isinstance MFVec3f =', isinstance(test,MFVec3f))
print ('MFVec3f test.value =', test.value)
print ('MFVec3f test.XML() =', test.XML())
print ('MFVec3f test.VRML()=', test.VRML())
print ('MFVec3f test.JSON()=', test.JSON())
print ('MFVec3f regex match=',
             # 're.fullmatch(      MFVec3f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec3f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec3f.REGEX_PYTHON(),          str(test.value)))
print ('MFVec3f     isValidMFVec3f(test)=' + str(isValidMFVec3f(test)), flush=True)
print ('MFVec3f assertValidMFVec3f(test)', assertionComment,flush=True); assertValidMFVec3f(test)

print ('- - - - - - - - - -')

print ('SFVec3d.NAME()         = ' +     SFVec3d.NAME());
print ('SFVec3d.DEFAULT_VALUE()= ' + str(SFVec3d.DEFAULT_VALUE()));
print ('SFVec3d.ARRAY_TYPE()   = ' + str(SFVec3d.ARRAY_TYPE()));
print ('SFVec3d.TUPLE_SIZE()   = ' + str(SFVec3d.TUPLE_SIZE()));
print ('SFVec3d.REGEX_PYTHON() = ' + str(SFVec3d.REGEX_PYTHON()));
print ('SFVec3d.REGEX_XML()    = ' + str(SFVec3d.REGEX_XML()));
print ('SFVec3d.TOOLTIP_URL()  = ' + str(SFVec3d.TOOLTIP_URL()));
test = SFVec3d()
test = SFVec3d((-1, -2, -3)) # commas required
test.value = (1, 2, 3)       # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec3d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec3d test       =', test)
print ('SFVec3d value type =', type(test.value))
print ('isinstance SFVec3d =', isinstance(test,SFVec3d))
print ('SFVec3d test.value =', test.value)
print ('SFVec3d test.XML() =', test.XML())
print ('SFVec3d test.VRML()=', test.VRML())
print ('SFVec3d test.JSON()=', test.JSON())
print ('SFVec3d regex match=',
             # 're.fullmatch(      SFVec3d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec3d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec3d.REGEX_PYTHON(),          str(test.value)))
print ('SFVec3d     isValidSFVec3d(test)=' + str(isValidSFVec3d(test)), flush=True)
print ('SFVec3d assertValidSFVec3d(test)', assertionComment,flush=True); assertValidSFVec3d(test)
print()

print ('MFVec3d.NAME()         = ' +     MFVec3d.NAME());
print ('MFVec3d.DEFAULT_VALUE()= ' + str(MFVec3d.DEFAULT_VALUE()));
print ('MFVec3d.ARRAY_TYPE()   = ' + str(MFVec3d.ARRAY_TYPE()));
print ('MFVec3d.TUPLE_SIZE()   = ' + str(MFVec3d.TUPLE_SIZE()));
print ('MFVec3d.REGEX_PYTHON() = ' + str(MFVec3d.REGEX_PYTHON()));
print ('MFVec3d.REGEX_XML()    = ' + str(MFVec3d.REGEX_XML()));
print ('MFVec3d.TOOLTIP_URL()  = ' + str(MFVec3d.TOOLTIP_URL()));
test = MFVec3d()
test = MFVec3d([(-1,-2,-3),(-4,-5,-6)]) # commas required
test.value =   [(0,1,2),(3,4,5)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec3d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec3d( 1,2,3,4,5,6 )
print ('MFVec3d test       =', test)
print ('MFVec3d value type =', type(test.value))
print ('isinstance MFVec3d =', isinstance(test,MFVec3d))
print ('MFVec3d test.value =', test.value)
print ('MFVec3d test.XML() =', test.XML())
print ('MFVec3d test.VRML()=', test.VRML())
print ('MFVec3d test.JSON()=', test.JSON())
print ('MFVec3d regex match=',
             # 're.fullmatch(      MFVec3d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec3d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec3d.REGEX_PYTHON(),          str(test.value)))
print ('MFVec3d     isValidMFVec3d(test)=' + str(isValidMFVec3d(test)), flush=True)
print ('MFVec3d assertValidMFVec3d(test)', assertionComment,flush=True); assertValidMFVec3d(test)

print ('- - - - - - - - - -')

print ('SFVec4f.NAME()         = ' +     SFVec4f.NAME());
print ('SFVec4f.DEFAULT_VALUE()= ' + str(SFVec4f.DEFAULT_VALUE()));
print ('SFVec4f.ARRAY_TYPE()   = ' + str(SFVec4f.ARRAY_TYPE()));
print ('SFVec4f.TUPLE_SIZE()   = ' + str(SFVec4f.TUPLE_SIZE()));
print ('SFVec4f.REGEX_PYTHON() = ' + str(SFVec4f.REGEX_PYTHON()));
print ('SFVec4f.REGEX_XML()    = ' + str(SFVec4f.REGEX_XML()));
print ('SFVec4f.TOOLTIP_URL()  = ' + str(SFVec4f.TOOLTIP_URL()));
test = SFVec4f()
test = SFVec4f((-1,-2,-3,-4)) # commas required
test.value = (1, 2, 3, 4)     # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec4f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec4f test       =', test)
print ('SFVec4f value type =', type(test.value))
print ('isinstance SFVec4f =', isinstance(test,SFVec4f))
print ('SFVec4f test.value =', test.value)
print ('SFVec4f test.XML() =', test.XML())
print ('SFVec4f test.VRML()=', test.VRML())
print ('SFVec4f test.JSON()=', test.JSON())
print ('SFVec4f regex match=',
             # 're.fullmatch(      SFVec4f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec4f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec4f.REGEX_PYTHON(),          str(test.value)))
print ('SFVec4f     isValidSFVec4f(test)=' + str(isValidSFVec4f(test)), flush=True)
print ('SFVec4f assertValidSFVec4f(test)', assertionComment,flush=True); assertValidSFVec4f(test)
print()

print ('MFVec4f.NAME()         = ' +     MFVec4f.NAME());
print ('MFVec4f.DEFAULT_VALUE()= ' + str(MFVec4f.DEFAULT_VALUE()));
print ('MFVec4f.ARRAY_TYPE()   = ' + str(MFVec4f.ARRAY_TYPE()));
print ('MFVec4f.TUPLE_SIZE()   = ' + str(MFVec4f.TUPLE_SIZE()));
print ('MFVec4f.REGEX_PYTHON() = ' + str(MFVec4f.REGEX_PYTHON()));
print ('MFVec4f.REGEX_XML()    = ' + str(MFVec4f.REGEX_XML()));
print ('MFVec4f.TOOLTIP_URL()  = ' + str(MFVec4f.TOOLTIP_URL()));
test = MFVec4f()
test = MFVec4f([(-1,-2,-3,-4),(-5,-6,-7,-8)]) # commas required
test.value =   [(0,1,2,3),(4,5,6,7)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec4f " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec4f( 1,2,3,4,5,6,7,8 )
print ('MFVec4f test       =', test)
print ('MFVec4f value type =', type(test.value))
print ('isinstance MFVec4f =', isinstance(test,MFVec4f))
print ('MFVec4f test.value =', test.value)
print ('MFVec4f test.XML() =', test.XML())
print ('MFVec4f test.VRML()=', test.VRML())
print ('MFVec4f test.JSON()=', test.JSON())
print ('MFVec4f regex match=',
             # 're.fullmatch(      MFVec4f.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec4f.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec4f.REGEX_PYTHON(),          str(test.value)))
print ('MFVec4f     isValidMFVec4f(test)=' + str(isValidMFVec4f(test)), flush=True)
print ('MFVec4f assertValidMFVec4f(test)', assertionComment,flush=True); assertValidMFVec4f(test)

print ('- - - - - - - - - -')

print ('SFVec4d.NAME()         = ' +     SFVec4d.NAME());
print ('SFVec4d.DEFAULT_VALUE()= ' + str(SFVec4d.DEFAULT_VALUE()));
print ('SFVec4d.ARRAY_TYPE()   = ' + str(SFVec4d.ARRAY_TYPE()));
print ('SFVec4d.TUPLE_SIZE()   = ' + str(SFVec4d.TUPLE_SIZE()));
print ('SFVec4d.REGEX_PYTHON() = ' + str(SFVec4d.REGEX_PYTHON()));
print ('SFVec4d.REGEX_XML()    = ' + str(SFVec4d.REGEX_XML()));
print ('SFVec4d.TOOLTIP_URL()  = ' + str(SFVec4d.TOOLTIP_URL()));
test = SFVec4d()
test = SFVec4d((-1,-2,-3,-4)) # commas required
test.value = (1, 2, 3, 4)     # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFVec4d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFVec4d test       =', test)
print ('SFVec4d value type =', type(test.value))
print ('isinstance SFVec4d =', isinstance(test,SFVec4d))
print ('SFVec4d test.value =', test.value)
print ('SFVec4d test.XML() =', test.XML())
print ('SFVec4d test.VRML()=', test.VRML())
print ('SFVec4d test.JSON()=', test.JSON())
print ('SFVec4d regex match=',
             # 're.fullmatch(      SFVec4d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFVec4d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFVec4d.REGEX_PYTHON(),          str(test.value)))
print ('SFVec4d     isValidSFVec4d(test)=' + str(isValidSFVec4d(test)), flush=True)
print ('SFVec4d assertValidSFVec4d(test)', assertionComment,flush=True); assertValidSFVec4d(test)
print()

print ('MFVec4d.NAME()         = ' +     MFVec4d.NAME());
print ('MFVec4d.DEFAULT_VALUE()= ' + str(MFVec4d.DEFAULT_VALUE()));
print ('MFVec4d.ARRAY_TYPE()   = ' + str(MFVec4d.ARRAY_TYPE()));
print ('MFVec4d.TUPLE_SIZE()   = ' + str(MFVec4d.TUPLE_SIZE()));
print ('MFVec4d.REGEX_PYTHON() = ' + str(MFVec4d.REGEX_PYTHON()));
print ('MFVec4d.REGEX_XML()    = ' + str(MFVec4d.REGEX_XML()));
print ('MFVec4d.TOOLTIP_URL()  = ' + str(MFVec4d.TOOLTIP_URL()));
test = MFVec4d()
test = MFVec4d([(-1,-2,-3,-4),(-5,-6,-7,-8)]) # commas required
test.value =   [(0,1,2,3),(4,5,6,7)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFVec4d " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFVec4d( 1,2,3,4,5,6,7,8 )
print ('MFVec4d test       =', test)
print ('MFVec4d value type =', type(test.value))
print ('isinstance MFVec4d =', isinstance(test,MFVec4d))
print ('MFVec4d test.value =', test.value)
print ('MFVec4d test.XML() =', test.XML())
print ('MFVec4d test.VRML()=', test.VRML())
print ('MFVec4d test.JSON()=', test.JSON())
print ('MFVec4d regex match=',
             # 're.fullmatch(      MFVec4d.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFVec4d.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFVec4d.REGEX_PYTHON(),          str(test.value)))
print ('MFVec4d     isValidMFVec4d(test)=' + str(isValidMFVec4d(test)), flush=True)
print ('MFVec4d assertValidMFVec4d(test)', assertionComment,flush=True); assertValidMFVec4d(test)

print ('- - - - - - - - - -')

print ('SFColor.NAME()         = ' +     SFColor.NAME());
print ('SFColor.DEFAULT_VALUE()= ' + str(SFColor.DEFAULT_VALUE()));
print ('SFColor.ARRAY_TYPE()   = ' + str(SFColor.ARRAY_TYPE()));
print ('SFColor.TUPLE_SIZE()   = ' + str(SFColor.TUPLE_SIZE()));
print ('SFColor.REGEX_PYTHON() = ' + str(SFColor.REGEX_PYTHON()));
print ('SFColor.REGEX_XML()    = ' + str(SFColor.REGEX_XML()));
print ('SFColor.TOOLTIP_URL()  = ' + str(SFColor.TOOLTIP_URL()));
test = SFColor()
print ('SFColor isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test.value = (1, 1, 1)      # commas required
print ('SFColor isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test = SFColor((1, 1, 1))   # commas required
test = SFColor((0, .5, 1))  # commas required
test.value = (0, .5, 1)     # commas required
#test.value = (0, .5, 1, 5) # 4 elements, illegal tupleSize
#test.value = (0, .5, 5)    # illegal value 5
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFColor " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFColor test       =', test)
print ('SFColor value type =', type(test.value))
print ('isinstance SFColor =', isinstance(test,SFColor))
print ('SFColor test.value =', test.value)
print ('SFColor test.XML() =', test.XML())
print ('SFColor test.VRML()=', test.VRML())
print ('SFColor test.JSON()=', test.JSON())
print ('SFColor regex match=',
             # 're.fullmatch(      SFColor.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFColor.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFColor.REGEX_PYTHON(),          str(test.value)))
print ('SFColor   isValidSFColor(test)=' + str(isValidSFColor(test)), flush=True)
print ('SFColor      isZeroToOne(test)=' + str(isZeroToOne(test)), flush=True)
print ('SFColor assertValidSFColor(test)', assertionComment,flush=True); assertValidSFColor(test)
print()

print ('MFColor.NAME()         = ' +     MFColor.NAME());
print ('MFColor.DEFAULT_VALUE()= ' + str(MFColor.DEFAULT_VALUE()));
print ('MFColor.ARRAY_TYPE()   = ' + str(MFColor.ARRAY_TYPE()));
print ('MFColor.TUPLE_SIZE()   = ' + str(MFColor.TUPLE_SIZE()));
print ('MFColor.REGEX_PYTHON() = ' + str(MFColor.REGEX_PYTHON()));
print ('MFColor.REGEX_XML()    = ' + str(MFColor.REGEX_XML()));
print ('MFColor.TOOLTIP_URL()  = ' + str(MFColor.TOOLTIP_URL()));
test = MFColor()
print ('MFColor isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test = MFColor([(0, .5, 1),(1, .5, 0)]) # commas required
print ('MFColor isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test.value =   [(0, .5, 1),(1, .5, 0)]  # commas required
# test.value = (0, .5, 1, 5)    # illegal value 5
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFColor " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFColor([0, .5, 1, 1, .5, 0])
print ('MFColor test       =', test)
print ('MFColor value type =', type(test.value))
print ('isinstance MFColor =', isinstance(test,MFColor))
print ('MFColor test.value =', test.value)
print ('MFColor test.XML() =', test.XML())
print ('MFColor test.VRML()=', test.VRML())
print ('MFColor test.JSON()=', test.JSON())
print ('MFColor regex match=',
             # 're.fullmatch(      MFColor.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFColor.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFColor.REGEX_PYTHON(),          str(test.value)))
print ('MFColor     isValidMFColor(test)=' + str(isValidMFColor(test)), flush=True)
print ('MFColor        isZeroToOne(test)=' + str(isZeroToOne(test)), flush=True)
print ('MFColor assertValidMFColor(test)', assertionComment,flush=True); assertValidMFColor(test)

print ('- - - - - - - - - -')

print ('SFColorRGBA.NAME()         = ' +     SFColorRGBA.NAME());
print ('SFColorRGBA.DEFAULT_VALUE()= ' + str(SFColorRGBA.DEFAULT_VALUE()));
print ('SFColorRGBA.ARRAY_TYPE()   = ' + str(SFColorRGBA.ARRAY_TYPE()));
print ('SFColorRGBA.TUPLE_SIZE()   = ' + str(SFColorRGBA.TUPLE_SIZE()));
print ('SFColorRGBA.REGEX_PYTHON() = ' + str(SFColorRGBA.REGEX_PYTHON()));
print ('SFColorRGBA.REGEX_XML()    = ' + str(SFColorRGBA.REGEX_XML()));
print ('SFColorRGBA.TOOLTIP_URL()  = ' + str(SFColorRGBA.TOOLTIP_URL()));
test = SFColorRGBA()
print ('SFColorRGBA isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test.value = (1, 1, 1, 1)            # commas required
print ('SFColorRGBA isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test = SFColorRGBA((1, 1, 1, 1))     # commas required
test = SFColorRGBA((0, .5, 1, 0.75)) # commas required
test.value = (0, .5, 1, 0.75)        # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFColorRGBA " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO     # commas required
#test = SFColorRGBA((2, 3, 4, 5)) # fails assertZeroToOne requirements:
print ('SFColorRGBA test       =', test)
print ('SFColorRGBA value type =', type(test.value))
print ('isinstance SFColorRGBA =', isinstance(test,SFColorRGBA))
print ('SFColorRGBA test.value =', test.value)
print ('SFColorRGBA test.XML() =', test.XML())
print ('SFColorRGBA test.VRML()=', test.VRML())
print ('SFColorRGBA test.JSON()=', test.JSON())
print ('SFColorRGBA regex match=',
             # 're.fullmatch(      SFColorRGBA.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFColorRGBA.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFColorRGBA.REGEX_PYTHON(),          str(test.value)))
print ('SFColorRGBA     isValidSFColorRGBA(test)=' + str(isValidSFColorRGBA(test)), flush=True)
print ('SFColorRGBA            isZeroToOne(test)=' + str(isZeroToOne(test)), flush=True)
print ('SFColorRGBA assertValidSFColorRGBA(test)', assertionComment,flush=True); assertValidSFColorRGBA(test)
print()

print ('MFColorRGBA.NAME()         = ' +     MFColorRGBA.NAME());
print ('MFColorRGBA.DEFAULT_VALUE()= ' + str(MFColorRGBA.DEFAULT_VALUE()));
print ('MFColorRGBA.ARRAY_TYPE()   = ' + str(MFColorRGBA.ARRAY_TYPE()));
print ('MFColorRGBA.TUPLE_SIZE()   = ' + str(MFColorRGBA.TUPLE_SIZE()));
print ('MFColorRGBA.REGEX_PYTHON() = ' + str(MFColorRGBA.REGEX_PYTHON()));
print ('MFColorRGBA.REGEX_XML()    = ' + str(MFColorRGBA.REGEX_XML()));
print ('MFColorRGBA.TOOLTIP_URL()  = ' + str(MFColorRGBA.TOOLTIP_URL()));
test = MFColorRGBA()
print ('MFColorRGBA isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test = MFColorRGBA([(0, .5, 1, 0.75),(1, .5, 0, 0.75)]) # commas required
print ('MFColorRGBA isZeroToOne(' + str(test.value) + ')=' + str(isZeroToOne(test)), flush=True)
test.value =   [(0, .5, 1, 0.75),(1, .5, 0, 0.75)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFColorRGBA " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFColorRGBA( 0, .5, 1, 0.75, 1, .5, 0, 0.75 )
print ('MFColorRGBA test       =', test)
print ('MFColorRGBA value type =', type(test.value))
print ('isinstance MFColorRGBA =', isinstance(test,MFColorRGBA))
print ('MFColorRGBA test.value =', test.value)
print ('MFColorRGBA test.XML() =', test.XML())
print ('MFColorRGBA test.VRML()=', test.VRML())
print ('MFColorRGBA test.JSON()=', test.JSON())
print ('MFColorRGBA regex match=',
             # 're.fullmatch(      MFColorRGBA.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFColorRGBA.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFColorRGBA.REGEX_PYTHON(),          str(test.value)))
print ('MFColorRGBA     isValidMFColorRGBA(test)=' + str(isValidMFColorRGBA(test)), flush=True)
print ('MFColorRGBA            isZeroToOne(test)=' + str(isZeroToOne(test)), flush=True)
print ('MFColorRGBA assertValidMFColorRGBA(test)', assertionComment,flush=True); assertValidMFColorRGBA(test)

print ('- - - - - - - - - -')

print ('SFRotation.NAME()         = ' +     SFRotation.NAME());
print ('SFRotation.DEFAULT_VALUE()= ' + str(SFRotation.DEFAULT_VALUE()));
print ('SFRotation.ARRAY_TYPE()   = ' + str(SFRotation.ARRAY_TYPE()));
print ('SFRotation.TUPLE_SIZE()   = ' + str(SFRotation.TUPLE_SIZE()));
print ('SFRotation.REGEX_PYTHON() = ' + str(SFRotation.REGEX_PYTHON()));
print ('SFRotation.REGEX_XML()    = ' + str(SFRotation.REGEX_XML()));
print ('SFRotation.TOOLTIP_URL()  = ' + str(SFRotation.TOOLTIP_URL()));
test = SFRotation()
test = SFRotation((0, .5, 1, 0.75)) # commas required
test.value = (0, .5, 1, 0.75)    # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("SFRotation " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
print ('SFRotation test       =', test)
print ('SFRotation value type =', type(test.value))
print ('isinstance SFRotation =', isinstance(test,SFRotation))
print ('SFRotation test.value =', test.value)
print ('SFRotation test.XML() =', test.XML())
print ('SFRotation test.VRML()=', test.VRML())
print ('SFRotation test.JSON()=', test.JSON())
print ('SFRotation regex match=',
             # 're.fullmatch(      SFRotation.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + SFRotation.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      SFRotation.REGEX_PYTHON(),          str(test.value)))
print ('SFRotation     isValidSFRotation(test)=' + str(isValidSFRotation(test)), flush=True)
print ('SFRotation assertValidSFRotation(test)', assertionComment,flush=True); assertValidSFRotation(test)
print()

print ('MFRotation.NAME()         = ' +     MFRotation.NAME());
print ('MFRotation.DEFAULT_VALUE()= ' + str(MFRotation.DEFAULT_VALUE()));
print ('MFRotation.ARRAY_TYPE()   = ' + str(MFRotation.ARRAY_TYPE()));
print ('MFRotation.TUPLE_SIZE()   = ' + str(MFRotation.TUPLE_SIZE()));
print ('MFRotation.REGEX_PYTHON() = ' + str(MFRotation.REGEX_PYTHON()));
print ('MFRotation.REGEX_XML()    = ' + str(MFRotation.REGEX_XML()));
print ('MFRotation.TOOLTIP_URL()  = ' + str(MFRotation.TOOLTIP_URL()));
test = MFRotation()
test = MFRotation([(0, .5, 1, 0.75),(1, .5, 0, 0.75)]) # commas required
test.value =   [(0, .5, 1, 0.75),(1, .5, 0, 0.75)]  # commas required
try:
    test.value = PLAIN_TEXT # always fails, overrides object type as ordinary string
except Exception as exception:
    print("MFRotation " + exception.__class__.__name__ + " exception correctly thrown when test.value = '" + PLAIN_TEXT + "'")
#TODO
# test = MFRotation( 0, .5, 1, 0.75, 1, .5, 0, 0.75 )
print ('MFRotation test       =', test)
print ('MFRotation value type =', type(test.value))
print ('isinstance MFRotation =', isinstance(test,MFRotation))
print ('MFRotation test.value =', test.value)
print ('MFRotation test.XML() =', test.XML())
print ('MFRotation test.VRML()=', test.VRML())
print ('MFRotation test.JSON()=', test.JSON())
print ('MFRotation regex match=',
             # 're.fullmatch(      MFRotation.REGEX_PYTHON(),          str(test.value))=',
             # 're.fullmatch(\'' + MFRotation.REGEX_PYTHON() + '\',' + str(test.value) + ')=',
                re.fullmatch(      MFRotation.REGEX_PYTHON(),          str(test.value)))
print ('MFRotation     isValidMFRotation(test)=' + str(isValidMFRotation(test)), flush=True)
print ('MFRotation assertValidMFRotation(test)', assertionComment,flush=True); assertValidMFRotation(test)

print ('- - - - - - - - - -')

print ('SFNode.NAME()         = ' +     SFNode.NAME());
print ('SFNode.DEFAULT_VALUE()= ' + str(SFNode.DEFAULT_VALUE()));
print ('SFNode.ARRAY_TYPE()   = ' + str(SFNode.ARRAY_TYPE()));
print ('SFNode.TUPLE_SIZE()   = ' + str(SFNode.TUPLE_SIZE()));
print ('SFNode.REGEX_PYTHON() = ' + str(SFNode.REGEX_PYTHON()));
print ('SFNode.REGEX_XML()    = ' + str(SFNode.REGEX_XML()));
print ('SFNode.TOOLTIP_URL()  = ' + str(SFNode.TOOLTIP_URL()));
test = SFNode()
test = SFNode(WorldInfo(DEF='A',title='Smoky World'))
print ('SFNode test                   =', test)
print ('SFNode test.value             =', test.value)
print ('-----')
print ('SFNode test.XML()  =')
print (        test.XML())
print ('-----')
print ('SFNode test.VRML() =')
print (        test.VRML())
print ('-----')
print ('SFNode test.JSON() =')
print (        test.JSON())
print ('-----')
print ('SFNode     isValidSFNode(test)=' + str(isValidSFNode(test)), flush=True)
print ('SFNode assertValidSFNode(test)', assertionComment,flush=True); assertValidSFNode(test)
print()

print ('MFNode.NAME()         = ' +     MFNode.NAME());
print ('MFNode.DEFAULT_VALUE()= ' + str(MFNode.DEFAULT_VALUE()));
print ('MFNode.ARRAY_TYPE()   = ' + str(MFNode.ARRAY_TYPE()));
print ('MFNode.TUPLE_SIZE()   = ' + str(MFNode.TUPLE_SIZE()));
print ('MFNode.REGEX_PYTHON() = ' + str(MFNode.REGEX_PYTHON()));
print ('MFNode.REGEX_XML()    = ' + str(MFNode.REGEX_XML()));
print ('MFNode.TOOLTIP_URL()  = ' + str(MFNode.TOOLTIP_URL()));
test = MFNode([Group(DEF='B'),Shape(DEF='C',appearance=Appearance(DEF='D',material=Material(DEF='E'))),WorldInfo(DEF='F'),
               ROUTE(fromNode="B",fromField="bboxSize",toNode="C",toField="bboxCenter")])
print ('MFNode test                   =', test)
print ('-----')
print ('MFNode test.XML()  =')
print (        test.XML())
print ('-----')
print ('MFNode test.VRML() =')
print (        test.VRML())
print ('-----')
print ('MFNode test.JSON() =')
print (        test.JSON())
print ('-----')
print ('MFNode str(test.value)        =', str(test.value), 'TODO get result to match by adding MFNode.__repl__; questionable use case')
print ('MFNode     isValidMFNode(test)=' + str(isValidMFNode(test)), flush=True)
print ('MFNode assertValidMFNode(test)', assertionComment,flush=True); assertValidMFNode(test)

print ('- - - - - - - - - -')

# caution: some output-flush trickiness might intersperse exception messages in console output
print()
print ('Range function tests:',flush=True)

if not(isPositive(-1)) and not(isPositive(0)) and isPositive(1):
    print('isPositive()    tests passed')
else:
    print('*** isPositive() tests failed')

if not(isNonNegative(-1)) and isNonNegative(0) and isNonNegative(1) and isNonNegative((0, 0, 0)):
    print('isNonNegative() tests passed')
else:
    print('*** isNonNegative() tests failed')

if not(isZeroToOne(-1)) and isZeroToOne(0) and isZeroToOne(1) and not(isZeroToOne(2)):
    print('isZeroToOne()   tests passed')
else:
    print('*** isZeroToOne() tests failed')

if not(isBoundingBox((-1, -2, -3))) and isBoundingBox((-1, -1, -1)) and isBoundingBox((0, 0, 0)): # and isBoundingBox((10, 10, 10)) and not(isBoundingBox((1, 1, -1))):
    print('isBoundingBox() tests passed')
else:
    print('*** isBoundingBox() tests failed')

print ('isPositive   (None)=', isPositive(None));
print ('isNonNegative(None)=', isNonNegative(None));
print ('isZeroToOne  (None)=', isZeroToOne(None));
print ('isBoundingBox(None)=', isBoundingBox(None));

# - - - - - - -

# caution: some output-flush trickiness might intersperse exception messages in console output
print()
print ('Assertion tests:',flush=True)

# these are tested to  pass:
print('test AssertionError assertBoundingBox:       Group(bboxSize=(+3, +2, +1)) expected to pass'); Group(bboxSize=(+3, +2, +1))
print('test AssertionError assertZeroToOne:         SpotLight(ambientIntensity=0.5) expected to pass'); SpotLight(ambientIntensity=0.5)
print('test AssertionError assertNonNegative:       SpotLight(radius=1) expected to pass'); SpotLight(radius=1)
print('test AssertionError assertPositive:          unit(conversionFactor=1) expected to pass'); unit(conversionFactor=1)
print('test AssertionError assertGreaterThanEquals: component(level=1) expected to pass'); component(level=1)
print('test AssertionError assertLessThanEquals:    component(level=5) expected to pass'); component(level=5)
print('test AssertionError assertGreaterThan:       Arc2D(startAngle=-6.28) expected to pass'); Arc2D(startAngle=-6.28)
print('test AssertionError assertLessThan:          Arc2D(startAngle=+6.28) expected to pass'); Arc2D(startAngle=+6.28)

# - - - - - - -

# these have been tested to fail:
print ()
print ('(Assertion tests expected to fail are commented out and require individual confirmation checks)',flush=True)
#print('test AssertionError assertBoundingBox:       Group(bboxSize=(-3, -2, -1)) expected to fail...'); Group(bboxSize=(-3, -2, -1))
#print('test AssertionError assertZeroToOne:         SpotLight(ambientIntensity=-0.1) expected to fail...'); SpotLight(ambientIntensity=-0.1)
#print('test AssertionError assertNonNegative:       SpotLight(radius=-0.1) expected to fail...'); SpotLight(radius=-0.1)
#print('test AssertionError assertPositive:          unit(conversionFactor=0) expected to fail...'); unit(conversionFactor=0)
#print('test AssertionError assertGreaterThanEquals: component(level=0) expected to fail...'); component(level=0)
#print('test AssertionError assertLessThanEquals:    component(level=6) expected to fail...'); component(level=6)
#print('test AssertionError assertGreaterThan:       Arc2D(startAngle=-6.2832) expected to fail...'); Arc2D(startAngle=-6.2832)
#print('test AssertionError assertLessThan:          Arc2D(startAngle=+6.2832) expected to fail...'); Arc2D(startAngle=+6.2832)

print()
print('test X3DField type mismatch:  isValidSFVec3f(SFColor()) expected to return False, actual return: ' + str(    isValidSFVec3f(SFColor())))
# print('test AssertionError X3DField type mismatch:  assertValidSFVec3f(SFColor()) expected to fail...'); assertValidSFVec3f(SFColor());

# - - - - - - -

print ()
print ('Node and field tests:')

materialInstance = Material()
materialInstance = Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey')
print('materialInstance.NAME=', materialInstance.NAME())

print('field accessor test, including default value emissiveColor:')
print('materialInstance=' + materialInstance.NAME() +
    '(DEF=\'' + str(materialInstance.DEF) + '\'' +
    ',diffuseColor='  + str(materialInstance.diffuseColor) +
    ',emissiveColor=' + str(materialInstance.emissiveColor) + # exposes default value
    ',transparency='  + str(materialInstance.transparency) + ')')
print('must use str() function when concatenating:')
print('    materialInstance  =',       materialInstance)
print('str(materialInstance) = ' + str(materialInstance) + ' (should match)', flush=True)

print('assertValidSFNode (materialInstance) =' + str(assertValidSFNode (materialInstance)))
print('isX3DNode         (materialInstance) =' + str(isX3DNode     (materialInstance)))
print('isX3DStatement    (materialInstance) =' + str(isX3DStatement(materialInstance)))

# print('type(materialInstance) =',type(materialInstance))
            
# import inspect
# from inspect import signature
# print(inspect.getmembers(str))
            
print("WorldInfo(USE='useful',class_='classic')=",WorldInfo(USE='useful',class_='classic'))
print("    Group() =",    Group() )
print("str(Group())=",str(Group()) + ' (should match)', flush=True)

routeInstance = ROUTE(fromField='Here',toField='There')
print('    routeInstance =',     routeInstance)
print('str(routeInstance)=', str(routeInstance) + ' (should match)', flush=True)

print('    ROUTE()  =',      ROUTE())
print('str(ROUTE()) =',  str(ROUTE()) + ' (should match)', flush=True) # must use str() function when concatenating in print statement

print('isX3DNode     (routeInstance)=' + str(isX3DNode     (routeInstance)))
print('isX3DNode     (ROUTE())      =' + str(isX3DNode     (ROUTE())) + ' (should match)', flush=True)
print('isX3DStatement(routeInstance)=' + str(isX3DStatement(routeInstance)))
print('isX3DStatement(ROUTE())      =' + str(isX3DStatement(ROUTE())) + ' (should match)', flush=True)
            
nestedNodesTest = Shape(
    appearance=Appearance(
        material=Material(diffuseColor=(0.3,0.4,0.5,), transparency=0.2, DEF='Grey')),
    geometry=Sphere(radius=2),
    metadata=MetadataString(value=['checking']))

## test cases:
##      material=Material(diffuseColor=(0.3,0.4,0.5,.6), transparency=0.2, DEF='Grey')), # illegal diffuseColor
##  metadata=MetadataString(value='checking')) # assertValidMFString should fail when not a list

print ('    nestedNodesTest =',     nestedNodesTest)
print ('str(nestedNodesTest)=', str(nestedNodesTest) + ' (should match)', flush=True)

groupTest = Group(bboxSize=(1,2,3))
#groupTest = Group(bboxSize=[1,2,3]) # fails because it is a list, rather than tuple

groupTest = Group(
   bboxSize=(1,2,3),                        # simple fields and
   children=[WorldInfo(),Group(),Shape()])  # MFNode child list
print ('    groupTest  =',     groupTest)
print ('str(groupTest) =', str(groupTest) + ' (should match)', flush=True)
print ('length of MFNode list groupTest.children =', str(len(groupTest.children)))

# Group(WorldInfo(),bboxSize=[1,2,3]) # possible? maybe not needed

headTest = head()
headTest = head(children=[component(),unit(),meta(name='1',content='2'),meta()])
#headtest.children=[component(),unit(),meta(name='1',content='2'),meta()] # TODO fails
print ('     headTest  =',     headTest )
print (' str(headTest) =', str(headTest) + ' (should match)', flush=True)

sceneTest = Scene() # children=[WorldInfo(),Group()]
sceneTest = Scene(children=[WorldInfo(),Group()])
#sceneTest.children=[WorldInfo(),Group(),Shape()]
print ('    sceneTest  =',     sceneTest)
print ('str(sceneTest) =', str(sceneTest) + ' (should match)', flush=True)

# smoke test adapted from Andreas Plesch 12 May 2020
# http://web3d.org/pipermail/x3d-public_web3d.org/2020-May/012596.html
# x3d.py solution adapted from Vince Marchetti and Loren Peitso
print()
testScene1 = Scene()
print('initialization testScene1.XML()=')
print(testScene1.XML())
print('*** testScene1 Scene with no children() test:    hasChild() =', testScene1.hasChild())
print()
testScene2 = Scene()
testScene2.children.append(Group())
print('initialization testScene2.XML()=')
print(testScene2.XML())
print('*** testScene2 Scene with single children() test: hasChild() =', testScene2.hasChild())
print()
testScene3 = Scene()
testScene3.children.append(Transform())
print('initialization testScene3.XML()=')
print(testScene3.XML())
print('*** testScene3 Scene with different single children() test: hasChild() =', testScene3.hasChild())

modelTest = X3D(
    head=head(
        children=[
            # enumerations test diagnostic: name='Group' vice name='Grouping'
            component(name='Grouping',level=2),
            Comment("hello persistent comment in head children"),
            unit(category='length',conversionFactor=0.001,name='MILLIMETER'),
            meta(name='description', content='name-value pair & solitary-ampersand test'),
            meta(name='info',   content='diagnostic test 1'),
            meta(name='hint',   content='diagnostic test 2'),
            meta(name='warning',content='diagnostic test 3'),
            meta(name='error',  content='diagnostic test 4')]
    ),
    Scene=Scene(children=[
        WorldInfo(DEF='TestWorldInfo', title='modelTest sample scene'),
        WorldInfo(USE='TestWorldInfo'),
        Comment("hello persistent comment in Scene children"),
        NavigationInfo(type=["EXAMINE","FLY","ANY"]),
        Group(DEF='EmptyGroup', bboxSize=(1,2,3)),
        Transform(translation=(0,2,0),children=[
            Shape(geometry=Text(string=["Smoke","Test"],fontStyle=FontStyle(style_='BOLD'))),
            Comment("hello persistent comment in Transform children")
        ]),
        Shape(
            DEF='TestShape',
            appearance=Appearance(DEF='TestAppearance',
                material=Material(DEF='TestMaterial',transparency=0.5,diffuseColor=(0.4, 0.6, 0.8))),
            geometry=Box(DEF='TestBox')),
        Comment(value='note that comment objects are persistent and valid children nodes'),
        Inline(url=["HelloWorld.x3d","https://www.web3d.org/x3d/content/examples/HelloWorld.x3d"]),
        ROUTE(fromNode='TestGroup',fromField='bboxSize',toNode='TestBox',toField='size'),
        ProtoDeclare(name="SmokeProto",
            ProtoInterface=ProtoInterface(
                field=[
                field(accessType='inputOutput',appinfo='offset 1',name='offset1',type='SFVec3f',value=(0,0,-5)),
                field(accessType='inputOutput',appinfo='offset 2',name='offset2',type='SFFloat',value=0.5)]),
            ProtoBody=ProtoBody(
                children=[
                    Material(ambientIntensity=0.254777,diffuseColor=(0.685208,0.134679,0.332385),shininess=0.071429,specularColor=(0.122449,0.050035,0.050035),
                        IS=IS(
                            connect=[
                            connect(nodeField='shininess',protoField='offset2')]))])),
                            # TODO validation of connect field values
        ProtoInstance(name="SmokeProto",
                fieldValue=[
                fieldValue(name='offset1',value=(0,7,8)),
                fieldValue(name='offset2',value=0.78)]),
        Script(DEF='SmokeScript',sourceCode="""
ecmascript:
// testing multi-line text block support for Script sourceCode field
""")
    ])
    )

print ()
print ('metaDiagnostics utility function:')
print ( metaDiagnostics(modelTest))

print ()
print ('    modelTest     =',     modelTest)
print ('str(modelTest)    =', str(modelTest) + ' (should match)', flush=True)

print ()
print ('===================')
print ('    (default) XML(syntax="XML") allows self-closing singleton elements')
print ('    modelTest.XML(syntax="XML") =')
print (     prependLineNumbers(modelTest.XML(syntax="XML")))
xmlfile = open("examples/PythonX3dSmokeTestsModelTest.xml","wt")
xmlfile.write(modelTest.XML())
xmlfile.close()
print ('===================')
print ('    alternate HTML5() produces closing elements, invokes XML(syntax="HTML5")')
print ('    modelTest.HTML5() =')
print (     prependLineNumbers(modelTest.HTML5()))
print ('===================')
print ('              VRML() produces Virtual Reality Modeling Language syntax')
print ('    modelTest.VRML() =')
print (     prependLineNumbers(modelTest.VRML()))
vrmlfile = open("examples/PythonX3dSmokeTestsModelTest.wrl","wt")
vrmlfile.write(modelTest.VRML())
vrmlfile.close()
print ('===================')
print ('              JSON() produces JavaScript Object Notation (JSON) syntax')
print ('    modelTest.JSON() =')
print (     prependLineNumbers(modelTest.JSON()))
jsonfile = open("examples/PythonX3dSmokeTestsModelTest.json","wt")
jsonfile.write(modelTest.JSON())
jsonfile.close()
#print ('===================')
#print ('              X_ITE() produces HTML for X_ITE')
#print ('    modelTest.X_ITE() =')
#print (     modelTest.X_ITE())
print ('===================')
print ('              X3DOM() produces HTML for X3DOM')
print ('    modelTest.X3DOM() =')
print (     prependLineNumbers(modelTest.X3DOM()))
print ('===================')

print ('Current work:')
print ('DONE value range checks for simple types')
print ('TEST .XML()   .x3d recursive serializer unit testing validation')
print ('TEST .HTML5() .x3d recursive serializer')
print ('TEST .VRML()       recursive serializer unit testing export')
print ('TEST .JSON()       recursive serializer unit testing export')
print ('TODO X3D.X_ITE()   saved as .xhtml')
print ('TEST X3D.X3DOM()   saved as .html')
print ('TODO check node types when building scene graph')
print ('TODO add and invoke validation methods that walk model tree')
print ('TODO add regex checks on field export for XML attributes')
            
# TODO requires *arg and node-type-checking support
Appearance(      material=Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey')) # explicit
Appearance(      material=Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey'), alphaMode='BLEND', alphaCutoff=0.6)

# TODO is better constructor pattern possible for mixed node/field content?
# Appearance(         Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey'))   # implicit: problem due to alphaMode
# Appearance(material=Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey'))   # explicit

# print ('The following unit test fails due to incorrect node typing:')
# Appearance(lineProperties=Material(diffuseColor=(0.5,0.5,0.5), transparency=0.2, DEF='Grey')) # should fail

print ()
print ('Build results are maintained at')
print ('https://sourceforge.net/p/x3d/code/HEAD/tree/www.web3d.org/x3d/stylesheets/python/build.examples.log.txt')

print ()
print ('PythonX3dSmokeTests execution complete.')
