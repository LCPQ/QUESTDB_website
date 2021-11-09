import re
from TexSoup import TexSoup,TexCmd,TexNode
from .utils import *
import itertools
from enum import Enum
from abc import ABCMeta

class commandBase(metaclass=ABCMeta):
  def __init__(self,source,supportedTexType):
    if not (source.name==supportedTexType):
      raise ValueError(source+" is not a "+supportedTexType)
    self.source=source
  
  def __str__(self):
    return self.source.__str__

  def __repr__(self):
    return self.source.__repr__()
class newCommand(commandBase):
  def __init__(self,source):
    super(newCommand, self).__init__(source,"newcommand")
    
  @property
  def commandName(self):
    return self.source.args[0].value[1:]

  @property
  def argNum(self):
    return 0 if self.source.args[1].type!='optional' else self.source.args[1].value

  @property
  def result(self):
    return nodify(list(self.source.args[len(self.source.args)-1].contents))

  def exist(self,tex):
    exist=tex.find(self.commandName)!=None
    return exist

  def run(self,tex):
    cmds=list(tex.find_all(self.commandName))
    if len(cmds)==0:
      raise ValueError("Command not found in tex")
    else:  
      for cmd in cmds:
        if self.argNum==0:
          fres=self.result
        else:
          resultstr=str(self.result)
          res=TexSoup(re.sub(f'\#([1-{self.argNum}])',lambda m: cmd.args[int(m.group(1))-1].value,resultstr))
          fres=TexSoup(res)
        if str(tex)==str(cmd):
          tex.expr=fres.expr
        else:
          try:
            tex.replace(cmd,fres)
          except:
            print(f"Unable to replace {str(cmd)}",file=sys.stderr)
            return False
        return True
  def tryRun(self,tex):
    cmds=list(tex.find_all(self.commandName))
    if len(cmds)!=0:
      for cmd in cmds:
        if self.argNum==0:
          res=self.result
        else:
          res=re.sub('#[1-{}]'.format(self.argNum),lambda m: cmd.args[int(m.group(1))-1],self.result)
        soup=TexSoup(res)
        tex.replace(cmd,soup)

  @staticmethod
  def runAll(tex,collection):
    cmds=[cmd for cmd in collection if cmd.exist(tex)]
    if(len(cmds)>0):
      for cmd in cmds:
        if not cmd.run(tex):
          cmds.remove(cmd)
          collection.remove(cmd)
      newCommand.runAll(tex,collection)
class columnAlignment(Enum):
  Left = "l"
  Right = "r"
  Center = "c"
class multiColumn(commandBase):
  def __init__(self,source):
    super(multiColumn,self).__init__(source,"multicolumn")

  @property
  def cols(self):
    return int(self.source.args[0].value)

  @property
  def align(self):
    return columnAlignment(self.source.args[1].value)

  @property
  def contents(self):
    return nodify(list(self.source.args[2].contents))
def tabularToData(table,commands=None,excludeColumn=set()):
  if table.name=="tabular":
    ctable=str(table)
    ctable=ctable.split("\n")
    ctable=ctable[1:len(ctable)-1]
    rows=[x.strip() for x in ''.join(ctable).split(r'\\') if x.strip()!='']  
    ltable=[]
    ltable=[[c.strip() for c in r.split("&")] for r in rows]
    lnewtable=[]
    for row in ltable:
      r=[]
      for item in row:
        texitem=TexSoup(item)
        child=list(texitem.children)
        if(len(child)==1 and child[0].name=="multicolumn"):
          mcolel=child[0]
          mcol=multiColumn(mcolel)
          el=mcol.contents
          el=desarg(el)
          if commands!=None:
            newCommand.runAll(el,commands)
          for i in range(int(mcol.cols)):
            r.append(el)
        else:
          if type(item) is str:
            el=TexSoup(item)
          else:
            el=item
          el=desarg(el)
          if commands!=None:
            newCommand.runAll(el,commands)
          r.append(el)
      lnewtable.append(r)
    lens=[len(x) for x in lnewtable]
    #Check if all rows have the same dimension
    slens=set(lens)
    if(len(slens)!=1):
      raise ValueError("This tabular is not supported because lines have not the same column numbers for each row the coulumns numbers are {}".format(lens))
    import numpy as np
    table=np.array(lnewtable,TexNode)
    table=np.delete(table,list(excludeColumn),1)
    return table
  else:
    raise ValueError("Only tabular LaTeX environment is supported")
  
def extractMath(TexMath,Soup=False,commands=[]):
  if not Soup and len(commands)>0:
    raise ValueError("Commandw are only usable when Soup is True")
  math=TexMath.find("$")
  lst=list(math.contents)
  mystr=str(lst[0])
  if not Soup:
    return mystr
  mathsoup=None
  try:
    mathsoup=TexSoup(mystr)
  except:
    raise ValueError(f"Error when parsing latex math: {mystr}")
  newCommand.runAll(mathsoup,commands)
  return mathsoup