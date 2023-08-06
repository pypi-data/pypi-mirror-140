from typing import Dict, Any, Union, List
import pandas, numpy

from .utils import pandasTypeToPythonType, simplifyArgName
from .runtime import Deployment

class PyCaretClassification:
  _pickleArgs = ["modelName", "pickleFileData", "modelInputs"]

  def __init__(self, modelName: str):
    self.modelName = modelName
    self.loadedModel: Union[Any, None] = None

  def makeDeployment(self, name: Union[str, None] = None):
    if not name: name = self.modelName
    return Deployment(
      deploy_function=self.makeDeployFunc(),
      source_override=self.getDeployFuncSource(),
      python_version="3.8",
      requirements_txt_contents=["pycaret==2.3.6"],
      name=name
    )

  def getDeployFuncSource(self):
    self._captureModelInfo()
    codeParts: List[str] = []
    funcArgs = ",\n    ".join([f"{simplifyArgName(k)}: {v}" for k, v in self.modelInputs.items()])
    dfArgs = ",\n      ".join([simplifyArgName(k) for k in self.modelInputs.keys()])
    globals()["pyc"] = self
    codeParts.append(f"def predict(\n    {funcArgs}) -> float:")
    codeParts.append(f"  return pyc.predict(\n      {dfArgs})")
    return "\n".join(codeParts)

  def makeDeployFunc(self):
    exec(self.getDeployFuncSource())
    return locals()["predict"]

  def __str__(self): return f'PyCaretClassification("{self.modelName}")'
  
  def __getstate__(self):
    pickleState: Dict[str, Any] = {}
    for pArg in self._pickleArgs:
      pickleState[pArg] = self.__getattribute__(pArg)
    return pickleState

  def __setstate__(self, pickledState: Dict[str, Any]):
    for pArg in self._pickleArgs:
      self.__setattr__(pArg, pickledState[pArg])
    self.writePickleFileToTmp()

  def _captureModelInfo(self):
    self.pickleFileData = self.readPickleFile()
    self.writePickleFileToTmp()
    self.modelInputs = self.getModelInputs()
  
  def loadModelFromTmp(self) -> Any:
    import pycaret.classification # type: ignore
    if not hasattr(self, "loadedModel") or self.loadedModel == None:
      self.loadedModel = pycaret.classification.load_model(f"/tmp/{self.modelName}", verbose=False) # type: ignore
    return self.loadedModel # type: ignore

  def readPickleFile(self):
    f = open(f"{self.modelName}.pkl", "rb")
    data = f.read()
    f.close()
    return data

  def writePickleFileToTmp(self):
    f = open(f"/tmp/{self.modelName}.pkl", "wb")
    f.write(self.pickleFileData)
    f.close()

  def getModelInputs(self):
    colTypes: Dict[str, str] = {}
    dtypeDict: Dict[str, str] = self.loadModelFromTmp().named_steps['dtypes'].learned_dtypes
    for argName, pandasType in dtypeDict.items():
      colTypes[argName] = pandasTypeToPythonType(pandasType)
    return colTypes

  def makeDfFromArgs(self, *args: Any):
    if len(args) != len(self.modelInputs):
      raise Exception(f"Expected {len(self.modelInputs)} arguments but received {len(args)}.")
    inputNames = [k for k in self.modelInputs.keys()]
    df = pandas.DataFrame(columns = inputNames)
    for i, name in enumerate(inputNames):
      df[name] = numpy.array([args[i]], dtype=self.modelInputs[name]) # type: ignore
    return df

  def predict(self, *args: Any):
    return float(self.loadModelFromTmp().predict(self.makeDfFromArgs(*args))[0])
