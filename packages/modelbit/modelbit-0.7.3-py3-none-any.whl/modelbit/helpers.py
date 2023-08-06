from typing import Union, Any, List, Dict
from enum import Enum

class OwnerInfo:
  def __init__(self, data: Dict[str, Any]):
    self.id: Union[str, None] = data.get("id", None)
    self.name: Union[str, None] = data.get("name", None)
    self.imageUrl: Union[str, None] = data.get("imageUrl", None)


class DatasetDesc:
  def __init__(self, data: Dict[str, Any]):
    self.name: str = data["name"]
    self.sqlModifiedAtMs: int = data["sqlModifiedAtMs"]
    self.query: str = data["query"]
    self.recentResultMs: Union[int, None] = data.get("recentResultMs", None)
    self.numRows: Union[int, None] = data.get("numRows", None)
    self.numBytes: Union[int, None] = data.get("numBytes", None)
    self.ownerInfo = OwnerInfo(data["ownerInfo"])

class ResultDownloadInfo:
  def __init__(self, data: Dict[str, Any]):
    self.id: str = data["id"]
    self.signedDataUrl: str = data["signedDataUrl"]
    self.key64: str = data["key64"]
    self.iv64: str = data["iv64"]

class WhType(Enum):
  Snowflake = 'Snowflake'
  Redshift = 'Redshift'
  Postgres = 'Postgres'

class GenericWarehouse:
  def __init__(self, data: Dict[str, Any]):
    self.type: WhType = data["type"]
    self.id: str = data["id"]
    self.displayName: str = data["displayName"]
    self.deployStatusPretty: str = data["deployStatusPretty"]
    self.createdAtMs: int = data["createdAtMs"]

class RuntimePythonState:
  excludeFromDict: List[str] = ['errors']

  def __init__(self):
    self.source: Union[str, None] = None
    self.name: Union[str, None] = None
    self.argNames: Union[List[str], None] = None
    self.argTypes: Union[Dict[str, str], None] = None
    self.namespaceVarsDesc: Union[Dict[str, str], None] = None
    self.namespaceFunctions: Union[Dict[str, str], None] = None
    self.namespaceImports: Union[Dict[str, str], None] = None
    self.namespaceFroms: Union[Dict[str, str], None] = None
    self.requirementsTxt: Union[str, None] = None
    self.pythonVersion: Union[str, None] = None
    self.errors: Union[List[str], None] = None # Not on TS version
    self.namespaceVars: Union[Dict[str, str], None] = None # Split in TS to S3DeploymentPythonState

  def asDict(self):
    d: Dict[str, Any] = {}
    for k, v in self.__dict__.items():
      if k not in self.excludeFromDict:
        d[k] = v
    return d

class RuntimeType(Enum):
   Deployment = 'Deployment'
   TrainingJob = 'TrainingJob'


class ResultDescription:
  def __init__(self, data: Dict[str, Any]):
    self.inputId: Union[str, int, bool, None] = data["inputId"]
    self.arguments: List[Union[str, int, bool, None]] = data["arguments"]
    self.resultDesc: List[str] = data["resultDesc"]
    self.resultPickle: Union[List[str], None] = data.get("resultPickle", None)

class RuntimeResultInfo:
  def __init__(self, data: Dict[str, Any]):
    self.runtimeId: str = data["runtimeId"]
    self.runtimeResultId: str = data["runtimeResultId"]
    self.createdAtMs: int = data["createdAtMs"]
    self.results: Union[List[ResultDescription], None] = None
    if "results" in data and type(data["results"]) == list: # can be None
      self.results = [ResultDescription(r) for r in data["results"]]
    self.runningAtMs: Union[int, None] = data.get("runningAtMs", None)
    self.completedAtMs: Union[int, None] = data.get("completedAtMs", None)
    self.failedAtMs: Union[int, None] = data.get("failedAtMs", None)
    self.ownerInfo = OwnerInfo(data["ownerInfo"])

class EnvironmentStatus(Enum):
  Updating = 'Updating'
  Ready = 'Ready'
  Error = 'Error'
  Unknown = 'Unknown'

class RuntimeInfo:
  def __init__(self, data: Dict[str, Any]):
    self.id: str = data["id"]
    self.name: str = data["name"]
    self.version: str = data["version"]
    self.restUrl: str = data["restUrl"]
    self.snowUrl: str = data["snowUrl"]
    self.forwardLambdaArn: Union[str, None] = data.get("forwardLambdaArn", None)
    self.pythonState: RuntimePythonState = data["pythonState"]
    self.createdAtMs: int = data["createdAtMs"]
    self.apiAvailableAtMs: Union[int, None] = data.get("apiAvailableAtMs", None)
    self.latest: bool = data["latest"]
    self.environmentStatus: EnvironmentStatus = data["environmentStatus"]
    self.ownerInfo = OwnerInfo(data["ownerInfo"])
    self.runtimeResults: Union[List[RuntimeResultInfo], None] = None
    if "runtimeResults" in data:
      self.runtimeResults = [RuntimeResultInfo(r) for r in data["runtimeResults"]]

class NotebookEnv:
  def __init__(self, data: Dict[str, Any]):
    self.userEmail: Union[str, None] = data.get("userEmail", None)
    self.signedToken: Union[str, None] = data.get("signedToken")
    self.uuid: Union[str, None] = data.get("uuid", None)
    self.authenticated: bool = data.get("authenticated", False)
    self.workspaceName: Union[str, None] = data.get("workspaceName", None)
    self.mostRecentVersion: Union[str, None] = data.get("mostRecentVersion", None)


class NotebookResponse:
  def __init__(self, data: Dict[str, Any]):
    self.error: Union[str, None] = data.get("error", None)
    self.message: Union[str, None] = data.get("message", None)
    self.notebookEnv: Union[NotebookEnv, None] = None
    if "notebookEnv" in data: self.notebookEnv = NotebookEnv(data["notebookEnv"])
    self.datasets: Union[List[DatasetDesc], None] = None
    if "datasets" in data: self.datasets = [DatasetDesc(d) for d in data["datasets"]]
    self.dsrDownloadInfo: Union[ResultDownloadInfo, None] = None
    if "dsrDownloadInfo" in data: self.dsrDownloadInfo = ResultDownloadInfo(data["dsrDownloadInfo"])
    self.warehouses: Union[List[GenericWarehouse], None] = None
    if "warehouses" in data: self.warehouses = [GenericWarehouse(w) for w in data["warehouses"]]
    self.runtimeOverviewUrl: Union[str, None] = None
    if "runtimeOverviewUrl" in data: self.runtimeOverviewUrl = data["runtimeOverviewUrl"]
    self.deployments: Union[List[RuntimeInfo], None] = None
    if "deployments" in data: self.deployments = [RuntimeInfo(d) for d in data["deployments"]]
    self.trainingJobs: Union[List[RuntimeInfo], None] = None
    if "trainingJobs" in data: self.trainingJobs = [RuntimeInfo(t) for t in data["trainingJobs"]]
    self.tjResultDownloadInfo: Union[ResultDownloadInfo, None] = None
    if "tjResultDownloadInfo" in data: self.tjResultDownloadInfo = ResultDownloadInfo(data["tjResultDownloadInfo"])
