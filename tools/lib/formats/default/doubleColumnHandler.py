from ..formatHandlerBase import formatHandlerBase
from ..formatName import formatName
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector,AbsDataFile,getSubtablesRange,state
from ...LaTeX import newCommand,extractMath
import re
from TexSoup import TexSoup
import numpy as np
from ...utils import getValFromCell
@formatName("doubleColumn")
class doubleColumnHandler(formatHandlerBase):
  def _readFromTableCore(self,table):
    datalist=list()
    datacls=dict()
    subtablesMol=getSubtablesRange(table)
    for rangeMol in subtablesMol:
      mymolecule=str(table[rangeMol[0],0])
      moltable=table[rangeMol,:]
      subtablestrans=getSubtablesRange(moltable,firstindex=0,column=1,count=2)
      for rangeTrans in subtablestrans:
        mytrans=moltable[rangeTrans,:]
        mytransdesc=mytrans[0:2,1]

        for i in range(2):
          mathsoup=extractMath(mytransdesc[i],Soup=True,commands=self.Commands)
          mytransdesc[i]=str(mathsoup)
        for colindex in range(3,np.size(table,1)):
          col=mytrans[:,colindex]
          mybasis=str(table[1,colindex])
          for index,cell in enumerate(col):
            methodnameAT1=str(mytrans[index,2])
            PTString=r"($\%T_1$)"
            HasT1=methodnameAT1.endswith(PTString)
            if HasT1:
              methodname=methodnameAT1[:-len(PTString)]
            else:
              methodname=str(methodnameAT1)
            mymethod=method(methodname,mybasis)
            strcell=str(cell)
            if strcell!="":
              if HasT1:
                m=re.match(r"^(?P<value>[-+]?\d+\.?\d*)\s*(?:\((?P<T1>\d+\.?\d*)\\\%\))?",strcell)
                val,unsafe=getValFromCell(TexSoup(m.group("value")))
                T1=m.group("T1")
              else:
                m=re.match(r"^[-+]?\d+\.?\d*",strcell)
                val,unsafe=getValFromCell(TexSoup(m.group(0)))
                T1=None
              if (mymolecule,mymethod.name,mymethod.basis) in datacls:
                data=datacls[(mymolecule,mymethod.name,mymethod.basis)]
              else:
                data=AbsDataFile()
                data.molecule=mymolecule
                data.method=mymethod
                datacls[(mymolecule,mymethod.name,mymethod.basis)]=data
              infin=mytransdesc[0].split(r"\rightarrow")
              for i,item in enumerate(infin):
                m=re.match(r"^(?P<number>\d)\\[,:;\s]\s*\^(?P<multiplicity>\d)(?P<sym>\S*)",item.strip())
                infin[i]=state(m.group("number"),m.group("multiplicity"),m.group("sym"))
              data.excitations.append(excitationValue(infin[0],infin[1],val,type=mytransdesc[1],isUnsafe=unsafe,T1=T1))
      for value in datacls.values():
        datalist.append(value)
    return datalist