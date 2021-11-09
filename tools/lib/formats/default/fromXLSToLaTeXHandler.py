from .. import *
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector,getSubtablesRange,state
from ...utils import getValFromCell
from TexSoup import TexSoup,TexNode
from ...LaTeX import newCommand,extractMath
import numpy as np
import json
import itertools
@formatName("fromXLSToLaTeX")
class fromXLSToLaTeXHandler(formatHandlerBase):
  def GetTypeFromAcronym(self,acronym):
    ra = r'\rightarrow'
    acroDict={
      "npi":rf'n {ra} \pi^\star',
      "ppi":rf'\pi {ra} \pi^\star',
      "n3s":rf'n {ra} 3s',
      "n3p":rf'n {ra} 3p',
      "dou":"double",
      "p3s":rf'\pi {ra} 3s',
      "p3p":rf'\pi {ra} 3p',
      "spi":rf'\sigma {ra} \pi^\star',
      "CT":r'CT',
      "non-d":None,
      "n.d.":None
    }
    try:
      value = acroDict[acronym]
      if self.TexOps.isDouble and ra in value:
        lr = [i.strip() for i in value.split(ra)]
        return f'{lr[0]},{lr[0]} {ra} {lr[1]},{lr[1]}'
      else:
       return value
    except KeyError  as ex:
      raise ValueError(f"Unrecognized acronym: {acronym}") from ex
  def GetFullState(self,TexState,defaultDatatype=DataType.ABS,VR=None,typeAcronym=None,Soup=True):
    datatype=defaultDatatype
    lst=list(TexState)
    if len(lst)>1 and lst[1].value=="F":
      datatype=DataType.FLUO
    statemath=str(list(lst[0].contents)[0])
    resultstr=statemath
    fulltype=[]
    if datatype==DataType.FLUO:
      resultstr+=r"[\mathrm{F}]"
    if VR!=None:
      fulltype.append(r"\mathrm{"+VR+"}")
    if typeAcronym!=None:
      _type=self.GetTypeFromAcronym(typeAcronym)
      if _type!=None:
        fulltype.append(_type)
      if len(fulltype)>0:
        resultstr+=" ("+";".join(fulltype)+")"
    resultstr="$"+resultstr+"$"
    if Soup:
      return TexSoup(resultstr)
    else:
      return resultstr

  def _readFromTableCore(self,table):
    datalist=list()
    subtablesRange=getSubtablesRange(table,firstindex=1,column=1)
    for myrange in subtablesRange:
      valDic=dict()
      mymolecule=str(table[myrange[0],1])
      initialState=self.TexOps.initialStates[mymolecule]
      for col in itertools.chain(range(8,11), range(14,np.size(table,1))):
        col=table[:,col]
        basis=self.TexOps.defaultBasis
        mymethcell=list(col[0])
        if len(mymethcell)==0:
          continue
        if isinstance(mymethcell[0],TexNode) and mymethcell[0].name=="$":
          kindSoup=TexSoup("".join(list(mymethcell[0].expr.all)))
          newCommand.runAll(kindSoup,self.Commands)
          kind=str(kindSoup)
          methodnameSoup=TexSoup(mymethcell[1].value)
          newCommand.runAll(methodnameSoup,self.Commands)
          methodname=str(methodnameSoup)
        else:
          kind=""
          methtex=col[0]
          newCommand.runAll(methtex,self.Commands)
          methodname=str(methtex)
        mymethod=method(methodname,basis)
        methkey=json.dumps(mymethod.__dict__)
        mathstates=[self.GetFullState(table[i,4],VR=str(table[i,6]),typeAcronym=str(table[i,7]),Soup=True) for i in myrange]
        finsts=dataFileBase.convertState(mathstates,initialState,default=self.TexOps.defaultType,commands=self.Commands)
        for index,cell in enumerate(col[myrange]):
          if str(cell)!="":
            val=str(cell)
            safedat=str(table[index+myrange[0],12])
            if safedat=="Y":
              unsafe=False
            elif safedat=="N":
              unsafe=True
            else:
              ValueError("Safe value error")
            finst=finsts[index]
            dt=finst[1]
            if dt in valDic:
              dtDic=valDic[dt]
            else:
              dtDic=dict()
              valDic[dt]=dtDic
            if not methkey in dtDic:
              dtDic[methkey]=dict()
            dataDic=dtDic[methkey]
            exkey=(json.dumps(finst[0].__dict__,),finst[2])
            if not exkey in dataDic:
              dataDic[exkey]=dict()
            if kind=='':
              dataDic[exkey][kind]=(val,unsafe)
            else:
              dataDic[exkey][kind]=val
      for dt,methdic in valDic.items():
        for methstring,exdic in methdic.items():
          data=datafileSelector(dt)()
          data.molecule=mymolecule
          methdic=json.loads(methstring)
          data.method=method(methdic["name"],methdic["basis"])
          for exstr,values in exdic.items():
            stDict=json.loads(exstr[0])
            ty=exstr[1]
            st=state(stDict["number"],stDict["multiplicity"],stDict["symmetry"])
            T1=values["\\%T_1"] if "\\%T_1" in values  else None
            oF= values["f"] if "f" in values  else None
            val,unsafe= values[""] if "" in values  else [None,False]
            data.excitations.append(excitationValue(initialState,st,val,type=ty,T1=T1,isUnsafe=unsafe,oscilatorForces=oF))
            datalist.append(data)
    return datalist