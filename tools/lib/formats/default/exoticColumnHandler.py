from ..formatHandlerBase import formatHandlerBase
from ..formatName import formatName
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector,getSubtablesRange,state
from ...utils import getValFromCell
from TexSoup import TexSoup,TexNode
from ...LaTeX import newCommand
import numpy as np
import json
@formatName("exoticColumn")
class exoticColumnHandler(formatHandlerBase):
  def _readFromTableCore(self,table):
    datalist=list()
    subtablesRange=getSubtablesRange(table)
    for myrange in subtablesRange:
      valDic=dict()
      mymolecule=str(table[myrange[0],0])
      initialState=self.TexOps.initialStates[mymolecule]
      for col in range(2,np.size(table,1)):
        col=table[:,col]
        basis=str(col[0])
        mymethcell=list(col[1])
        if isinstance(mymethcell[0],TexNode) and mymethcell[0].name=="$":
          kindSoup=TexSoup("".join(list(mymethcell[0].expr.all)))
          newCommand.runAll(kindSoup,self.Commands)
          kind=str(kindSoup)
          methodnameSoup=TexSoup(mymethcell[1].value)
          newCommand.runAll(methodnameSoup,self.Commands)
          methodname=str(methodnameSoup)
        else:
          kind=""
          methtex=col[1]
          newCommand.runAll(methtex,self.Commands)
          methodname=str(methtex)
        mymethod=method(methodname,basis)
        methkey=json.dumps(mymethod.__dict__)
        finsts=dataFileBase.convertState(table[myrange,1],initialState,default=self.TexOps.defaultType,commands=self.Commands)
        for index,cell in enumerate(col[myrange]):
          if str(cell)!="":
            val,unsafe=getValFromCell(cell)
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
            #data.excitations.append(excitationValue(initialState,finst[0],val,type=finst[2]))
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
            val,unsafe=values[""]
            data.excitations.append(excitationValue(initialState,st,val,type=ty,T1=T1,isUnsafe=unsafe,oscilatorForces=oF))
            datalist.append(data)
    return datalist