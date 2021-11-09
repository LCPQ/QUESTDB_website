from ..formatHandlerBase import formatHandlerBase
from ..formatName import formatName
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector
from ...utils import getValFromCell
import numpy as np
@formatName("line")
class lineHandler(formatHandlerBase):
  def _readFromTableCore(self,table):
    datalist=list()
    for col in range(1,np.size(table,1)):
      col=table[:,col]
      mymolecule=str(col[0])
      mymethod=method(str(col[2]),str(col[1]))
      initialState=self.TexOps.initialStates[mymolecule]
      finsts=dataFileBase.convertState(table[3:,0],initialState,default=self.TexOps.defaultType,commands=self.Commands)
      datacls=dict()
      for index,cell in enumerate(col[3:]):
        if str(cell)!="":
          val,unsafe=getValFromCell(cell)
          finst=finsts[index]
          dt=finst[1]
          if dt in datacls:
            data=datacls[dt]
          else:
            cl=datafileSelector(dt)
            data=cl()
            datacls[dt]=data
            data.molecule=mymolecule
            data.method=mymethod
          data.excitations.append(excitationValue(initialState,finst[0],val,type=finst[2],isUnsafe=unsafe))
      for value in datacls.values():
        datalist.append(value)
    return datalist