from TexSoup import TexSoup,TexCmd
from . import formats
from .data import dataFileBase,DataType, method, state, exSet
from collections import defaultdict

class dfbOptions(object):
  def __init__(self):
    self.defaultType=DataType.ABS
    self.format="line"
    self.suffix=None
    self.initialStates=defaultdict(lambda : state(1,1,"A_1"))
    self.isDouble=False
    self.defaultBasis="aug-cc-pVTZ"
    self.geometries = defaultdict(lambda :method("CC3","aug-cc-pVTZ"))
    self.set = ''
    self.excludeColumns=set()
  @staticmethod
  def readFromEnv(lateEnv):
    dfb_Opt=dfbOptions()
    dfbDefaultTypeNode=lateEnv.defaultType
    if dfbDefaultTypeNode!=None:
      dfbDefaultType=dfbDefaultTypeNode.expr
      if type(dfbDefaultType) is TexCmd:
        dfb_Opt.defaultType=DataType[dfbDefaultType.args[0].value.upper()]

    dfbFormatNode=lateEnv.format
    if dfbFormatNode!=None:
      dfbFormat=dfbFormatNode.expr
      if type(dfbFormat) is TexCmd:
        dfb_Opt.format=dfbFormat.args[0].value

    dfbSuffixNode=lateEnv.suffix
    if dfbSuffixNode!=None:
      dfbSuffix=dfbSuffixNode.expr
      if type(dfbSuffix) is TexCmd:
        dfb_Opt.suffix=dfbSuffix.args[0].value
    dfbInitialStateNodes=list(lateEnv.find_all("initialState"))
    for node in dfbInitialStateNodes:
      initialState=node.expr
      if type(initialState) is TexCmd:
        vRArgs=[arg.value for arg in initialState.args if arg.type=="required"]
        vOArgs=[arg.value for arg in initialState.args if arg.type=="optional"]
        if len(vOArgs)==0:
          defaultgeometry=state.fromString("1 "+vRArgs[0])
          dfb_Opt.initialStates.default_factory=lambda : defaultgeometry
        else:
          mystate=state.fromString("1 "+vRArgs[0])
          dfb_Opt.initialStates[vOArgs[0]]=mystate
    dfbIsDouble=lateEnv.isDouble
    if dfbIsDouble!=None:
      dfbIsDouble=dfbIsDouble.expr
      if type(dfbIsDouble) is TexCmd:
        if len(dfbIsDouble.args)==0:
          dfb_Opt.isDouble = True
        elif len(dfbIsDouble.args)==1 and dfbIsDouble.args[0].type=="optional":
          isDoubleStr=dfbIsDouble.args[0].value
          if isDoubleStr == "true":
            dfb_Opt.isDouble = True
          elif isDoubleStr == "false":
            isDouble = False
          else:
            raise ValueError("\isDouble must be 'true' or 'false'.")
        else:
          raise ValueError("Arguments error on '\isDouble'. Only one optional argument is supported.")
    dfbDefaultBasisNode=lateEnv.defaultBasis
    if dfbDefaultBasisNode!=None:
      dfbDefaultBasis=dfbDefaultBasisNode.expr
      if type(dfbDefaultBasis) is TexCmd:
        dfb_Opt.defaultBasis=dfbDefaultBasis.args[0].value
    dfbgeometryNodes=list(lateEnv.find_all("geometry"))
    for node in dfbgeometryNodes:
      geometry=node.expr
      if type(geometry) is TexCmd:
        vRArgs=[arg.value for arg in geometry.args if arg.type=="required"]
        vOArgs=[arg.value for arg in geometry.args if arg.type=="optional"]
        if len(vOArgs)==0:
          defaultgeometry=method(vRArgs[0],vRArgs[1])
          dfb_Opt.geometries.default_factory=lambda : defaultgeometry
        else:
          mygeometry=method(vRArgs[0],vRArgs[1])
          dfb_Opt.geometries[vOArgs[0]]=mygeometry
    dfbSetNode=lateEnv.set
    if dfbSetNode!=None:
      dfbSet=dfbSetNode.expr
      if type(dfbSet) is TexCmd:
        setname=dfbSet.args[0].value
        index=dfbSet.args[1].value
        dfb_Opt.set=exSet(setname,index=int(index))
    else:
      dfbStrSetNode=lateEnv.strSet
      if dfbStrSetNode!=None:
        dfbStrSet=dfbStrSetNode.expr
        if type(dfbStrSet) is TexCmd:
          dfb_Opt.set=setname=dfbStrSet.args[0].value
    dfbexcludeColumnsNodes=list(lateEnv.find_all("excludecolumns"))
    for node in dfbexcludeColumnsNodes:
      excludeColumns=node.expr
      if type(excludeColumns) is TexCmd:
        commas_string=excludeColumns.args[0].value
        ints=[int(x.strip()) for x in commas_string.split(",")]
        dfb_Opt.excludeColumns.update(ints)
    return dfb_Opt