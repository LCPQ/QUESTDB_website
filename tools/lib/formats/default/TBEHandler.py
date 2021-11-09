from ..formatHandlerBase import formatHandlerBase
from ..formatName import formatName
from ...data import dataFileBase,DataType,method,excitationValue,datafileSelector,getSubtablesRange
from ...utils import getValFromCell, checkFloat
@formatName("TBE")
class TBEHandler(formatHandlerBase):
  def _readFromTableCore(self,table):
    datalist=list()
    subtablesRange=getSubtablesRange(table)
    for myrange in subtablesRange:
      datacls=dict()
      mymolecule=str(table[myrange[0],0])
      initialState=self.TexOps.initialStates[mymolecule]
      mymethod=(method("TBE",self.TexOps.defaultBasis),method("TBE(Full)","CBS"))
      finsts=dataFileBase.convertState(table[myrange,1],initialState,default=self.TexOps.defaultType,commands=self.Commands)
      for index,row in enumerate(table[myrange,]):
        oscilatorForces=checkFloat(str(row[2]))
        T1 = checkFloat(str(row[3]))
        val,unsafe = getValFromCell(row[4])
        corr,unsafecorr = getValFromCell(row[7])
        finst=finsts[index]
        dt=finst[1]
        if dt in datacls:
          datamtbe = datacls[dt]
        else:
          cl=datafileSelector(dt)
          datamtbe=[]
          for met in mymethod:
            data=cl()
            data.molecule=mymolecule
            data.method=met
            datamtbe.append(data)
          datacls[dt]=datamtbe
        vs=[val,corr]
        uns=[unsafe,unsafecorr]
        for i in range(2):
          datamtbe[i].excitations.append(excitationValue(initialState,finst[0],vs[i],type=finst[2],T1=T1,oscilatorForces=oscilatorForces,isUnsafe=uns[i]))
      for value in datacls.values():
        for dat in value:
          datalist.append(dat)
    return datalist