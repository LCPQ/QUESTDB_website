from collections import OrderedDict
from TexSoup import TexSoup
from .LaTeX import newCommand,extractMath
from .utils import getValFromCell,checkFloat
from TexSoup import TexNode,TexEnv
from enum import IntEnum,auto,unique,IntFlag
from .formats import getFormatHandlers
import re
import os
import numpy as np
import json

class state:
  def __init__(self,number, multiplicity, symmetry):
    self.number = number
    self.multiplicity = multiplicity
    self.symmetry = symmetry
  @staticmethod
  def fromString(string):
    m=re.match(r"^(?P<number>\d)\s*\^(?P<multiplicity>\d)(?P<sym>\S*)",string)
    num=m.group('number')
    mul=m.group('multiplicity')
    sym=m.group('sym')
    return state(num,mul,sym)
@unique
class DataType(IntEnum):
  ABS=auto()
  FLUO=auto()
  
def datafileSelector(dataType):
  switcher={
    DataType.ABS:AbsDataFile,
    DataType.FLUO:FluoDataFile,
  }
  return switcher[dataType]

def getSubtablesRange(table,firstindex=2,column=0,count=1):
  subtablesRange=list()
  i=firstindex+count
  while i<np.size(table,0):
    if str(table[i,column])!="":
      subtablesRange.append(range(firstindex,i))
      firstindex=i
      i+=count
    else:
      i+=1
  subtablesRange.append(range(firstindex,np.size(table,0)))
  return subtablesRange

class exSet(object):
  def __init__(self,name,index=0):
    self.name=name
    self.index=index
  
  def __str__(self):
    return f"{self.name},{self.index}"

  @staticmethod
  def fromString(string):
    vals = string.split(",")
    if len(vals)>1:
      return exSet(vals[0],int(vals[1]))
    else:
      return exSet(vals[0])

  def getDOI(self):
    import yaml
    from pathlib import Path
    yamlpath=Path(__file__)/"../../statics/data/index.yaml"
    with yamlpath.open("r") as f:
      db = yaml.load(f,yaml.loader.FullLoader)
      sets=db["sets"]
      if self.name in db["sets"]:
        return sets[self.name][self.index]       

  def isSameSet(self,otherSet):
    return self.name == otherSet.name

  def isSameArticle(self,otherSet):
    if (self.name==otherSet.name and self.index==otherSet.index):
      return True
    else:
      return self.getDOI() == otherSet.getDOI()

class dataFileBase(object):
  def __init__(self):
    self.molecule = ''
    self.comment = ''
    self.code = None
    self.method = None
    self.excitations = []
    self.set = ''

  @property
  def IsTBE(self):
    return self.method.name=="TBE"

  @staticmethod
  def GetFileType():
    pass

  @staticmethod
  def convertState(StateTablelist,initialState,default=DataType.ABS,commands=[]):
    tmplst=[]
    for TexState in StateTablelist:
      st=str(extractMath(TexState,Soup=True,commands=commands))
      m=re.match(r"^\^(?P<multiplicity>\d)(?P<symm>[^\s\[(]*)\s*(?:\[(?:\\mathrm{)?(?P<special>\w)(?:})\])?\s*(:?\((?P<type>[^\)]*)\))?",st)
      mul=int(m.group("multiplicity"))
      symm=m.group("symm")
      spgrp=m.group("special")
      if spgrp is not None and spgrp=="F":
        trsp=DataType.FLUO
      else:
        trsp=default
      tygrp=m.group("type")
      tmplst.append((mul,symm,trsp,tygrp))
    lst=[]
    for index,item in enumerate(tmplst):
      unforminitialstate=(int(initialState.multiplicity),initialState.symmetry)
      countlst=[unforminitialstate]+[(it[0],it[1]) for it in tmplst[:index+1]]
      countitem=(item[0],item[1])
      count=countlst.count(countitem)
      lst.append((state(count,item[0],item[1]),item[2],item[3]))
    return lst
  def _OnReadMetaPair(self, key, value):
      if key == "molecule":
        self.molecule = value
      elif key == "comment":
        self.comment = value
      elif key == "code":
        self.code = code.fromString(value)
      elif key == "method":
        self.method = method.fromString(value)
      elif key == "set":
        self.set = exSet.fromString(value)

  @staticmethod
  def readFromTable(table,TexOps, commands=[]):
    for formatName,Cls in getFormatHandlers():
      if formatName.lower()==TexOps.format.lower():
        handler=Cls(TexOps,commands)
        break
    else:
      raise ValueError()
    return handler.readFromTable(table)
  def getMetadata(self):
    dic=OrderedDict()
    dic["Molecule"]=self.molecule
    dic["Comment"]=self.comment
    dic["code"]="" if self.code is None else self.code.toDataString()
    dic["method"]="" if self.method is None else self.method.toDataString()
    dic["set"]="" if self.set is None else self.set
    return dic
  
  def _OnReadMeta(self,line,dataType):
    #get key value
    match = dataFileBase._GetMetaRexEx().match(line)
    # normalize key to lower
    key = match.group(1).lower()
    # if data has value
    if match.group(2):
      val = match.group(2)
      self._OnReadMetaPair(key, val)
  @staticmethod
  def _OnReadRow(line):
    vals = re.findall(r"\([^\)]+\)|\S+",line)
    start = state(int(vals[0]), int(vals[1]), vals[2])
    end = state(int(vals[3]), int(vals[4]), vals[5])
    Type = vals[6] if (len(vals) >= 7) else None
    if Type == "_":
      Type = None
    if Type:
      m = re.match(r"^\(([^\)]*)\)$",Type)
      if m:
        Type = m[1]
    val = vals[7] if len(vals) >= 8 else str(np.NaN)
    T1 = vals[8] if len(vals) >= 9  else str(np.NaN)
    oscilatorForces = vals[9] if len(vals) >= 10 else str(np.NaN)
    isUnsafe = vals[10] == json.dumps(True) if  len(vals) >= 11 else False
    ex = excitationValue(start, end, val, Type,T1,isUnsafe,oscilatorForces)
    return ex

  @staticmethod
  def _GetMetaRexEx():
    #metadata RegExp (start with #; maybe somme spaces; : ; maybe somme space; datas)
    return re.compile(r"^#\s*([A-Za-z_]+)\s*:\s*(.*)$")

  @staticmethod
  def readFile(stream,dataType):
    lines = stream.readlines()
    # for each line with metadata
    ismetaArea = True
    dat = datafileSelector(dataType)()
    for line in lines:
      #if it's not empty line
      line = line.strip()
      if line:
        # if # may be metadata or comment
        if line[0] == "#":
          # if it's metadata
          if ismetaArea and dataFileBase._GetMetaRexEx().match(line):
            dat._OnReadMeta(line,dataType)
        else: # else its row
          ismetaArea = False
          dat.excitations.append(dat._OnReadRow(line))
    return dat
    
  def toFile(self,datadir,suffix=None):
    subpath=datadir/self.GetFileType().name.lower()
    if not subpath.exists():
      os.makedirs(str(subpath))
    molsoup=TexSoup(self.molecule)
    molfilename="".join(molsoup.text).replace("\\","")
    molfilename=molfilename.lower()
    fileNameComp=[molfilename,self.method.name]
    if self.method.basis:
      fileNameComp.append(self.method.basis)
    if suffix:
      fileNameComp.append(suffix)
    fileName="_".join(fileNameComp).replace(" ","_")+".dat"
    if os.sep in fileName:
      raise ValueError(f"fileName must be a pure file name not a path: {fileName}")
    file=subpath/fileName
    if not file.exists():
      with file.open("w") as f:
        for key,value in self.getMetadata().items():
          if value is not None:
            f.write("# {:9s}: {}\n".format(key,value))
        f.write("""
# Initial state            Final state                        Transition                    Energies (eV)   %T1    Oscillator strength    unsafe
#######################  #######################  ########################################  ############# ####### ##################### #############
# Number  Spin  Symm       Number  Spin  Symm         type                                    E_{:5s}       %T1            f            is unsafe\n""".format(self.GetFileType().name.lower()))
        for ex in self.excitations:
          mystr="  {:7s} {:5s} {:10s} {:7s} {:5s} {:12s} {:39s} {:13s} {:14s} {:13s}{}\n".format(
            str(ex.initial.number),
            str(ex.initial.multiplicity),
            ex.initial.symmetry,
            str(ex.final.number),
            str(ex.final.multiplicity),
            ex.final.symmetry,"("+str(ex.type)+")" if ex.type is not None else "_",
            str(ex.value) if ex.value is not None else "_",
            str(ex.T1) if ex.T1 is not None else "_",
            str(ex.oscilatorForces) if ex.oscilatorForces is not None else "_",
            json.dumps(ex.isUnsafe))
          f.write(mystr)
class method:
  def __init__(self,name, *args):
    self.name = name
    self.basis=args[0] if len(args)>0 else None

  @staticmethod
  def fromString(string):
    vals = string.split(",")
    return method(*vals)


  def __str__(self):
    string = self.name
    if (self.basis):
      string+= '/' + self.basis
    return string

  def toDataString(self):
    string=self.name
    if (self.basis):
      string+=","+self.basis
    return string

class code:
  def __init__(self,name, version=None):
    self.name = name
    self.version = version
  
  @staticmethod
  def fromString(string):
    vals = string.split(",")
    return code(*vals)

  def toDataString(self):
    string=self.name
    if (self.version):
      string+=","+self.version
    return string
  
class oneStateDataFileBase(dataFileBase):
  def __init__(self):
    super(oneStateDataFileBase,self).__init__()
    self.geometry = None

  def _OnReadMetaPair(self, key, value):
    if key == "geom":
      self.geometry = method.fromString(value)
    else:
      super(oneStateDataFileBase,self)._OnReadMetaPair(key, value)
  
  def getMetadata(self):
    dic=super(oneStateDataFileBase,self).getMetadata()
    dic["geom"]= "" if self.geometry is None else self.geometry.toDataString()
    dic.move_to_end("set")
    return dic

class AbsDataFile(oneStateDataFileBase):
  def __init__(self):
    super(AbsDataFile,self).__init__()
  
  @staticmethod
  def GetFileType():
    return DataType.ABS

class FluoDataFile(oneStateDataFileBase):
  def __init__(self):
    super(FluoDataFile,self).__init__()

  @staticmethod
  def GetFileType():
    return DataType.FLUO


class excitationBase:
  def __init__(self,initial, final,type=None, T1=None,isUnsafe=False):
    self.initial = initial
    self.final = final
    self.type = type
    self.T1  = T1
    self.isUnsafe = isUnsafe

class excitationValue(excitationBase):
  def __init__(self,initial, final, value, type=None, T1=None,isUnsafe=False,oscilatorForces=None):
    super(excitationValue,self).__init__(initial, final,type=type,T1=T1,isUnsafe=isUnsafe)
    self.value = value
    self.oscilatorForces = oscilatorForces
