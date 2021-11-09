from abc import ABCMeta, abstractmethod
class formatHandlerBase(object, metaclass=ABCMeta):
  def __init__(self,TexOps, commands=[]):
    self.TexOps=TexOps
    self.Commands=commands
  @abstractmethod
  def _readFromTableCore(self,table):
    raise NotImplementedError()

  def readFromTable(self,table):
    dataFiles=self._readFromTableCore(table)
    for file in dataFiles:
      self.__applyMetadataFromOptions(file)
    return dataFiles
  def __applyMetadataFromOptions(self,file):
    if hasattr(file, "geometry"):
      file.geometry = self.TexOps.geometries[file.molecule]
    file.set = self.TexOps.set
