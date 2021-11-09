from ..formatHandlerBase import formatHandlerBase
from ..formatName import formatName
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector,getSubtablesRange
from ...utils import getValFromCell
import numpy as np
@formatName("column")
class columnHandler(formatHandlerBase):
  def _readFromTableCore(self,table):
    datalist=list()
    subtablesRange=getSubtablesRange(table)
    for myrange in subtablesRange:
      for col in range(2,np.size(table,1)):
        datacls=dict()
        col=table[:,col]
        mymolecule=str(table[myrange[0],0])
        initialState=self.TexOps.initialStates[mymolecule]
        mymethod=method(str(col[1]),str(col[0]))
        finsts=dataFileBase.convertState(table[myrange,1],initialState,default=self.TexOps.defaultType,commands=self.Commands)
        for index,cell in enumerate(col[myrange]):
          if str(cell)!="":
            val,unsafe=getValFromCell(cell)
            finst=finsts[index]
            dt=finst[1]
            if dt in datacls:
              data=datacls[dt]
            else:
              cl=datafileSelector(dt)
              data=cl()
              data.molecule=mymolecule
              data.method=mymethod
              datacls[dt]=data
            data.excitations.append(excitationValue(initialState,finst[0],val,type=finst[2]))
        for value in datacls.values():
          datalist.append(value)
    return datalist