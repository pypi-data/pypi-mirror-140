from typing import Union, Any, List, Literal, Dict

class OwnerInfo:
  id: Union[str, None] = None
  name: Union[str, None] = None
  imageUrl: Union[str, None] = None

  def __init__(self, data: Dict[str, Any]):
    if "id" in data: self.id = data["id"]
    if "name" in data: self.name = data["name"]
    if "imageUrl" in data: self.imageUrl = data["imageUrl"]


class DatasetDesc:
  name: str
  sqlModifiedAtMs: int
  query: str
  recentResultMs: Union[int, None] = None
  numRows: Union[int, None] = None
  numBytes: Union[int, None] = None
  ownerInfo: OwnerInfo

  def __init__(self, data: Dict[str, Any]):
    self.name = data["name"]
    self.sqlModifiedAtMs = data["sqlModifiedAtMs"]
    self.query = data["query"]
    if "recentResultMs" in data: self.recentResultMs = data["recentResultMs"]
    if "numRows" in data: self.numRows = data["numRows"]
    if "numBytes" in data: self.numBytes = data["numBytes"]
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


class ResultDownloadInfo:
  id: str
  signedDataUrl: str
  key64: str
  iv64: str

  def __init__(self, data: Dict[str, Any]):
    self.id = data["id"]
    self.signedDataUrl = data["signedDataUrl"]
    self.key64 = data["key64"]
    self.iv64 = data["iv64"]

class GenericWarehouse:
  type: Union[Literal['Snowflake'], Literal['Redshift'], Literal['postgres']]
  id: str
  displayName: str
  deployStatusPretty: str
  createdAtMs: int

  def __init__(self, data: Dict[str, Any]):
    self.type = data["type"]
    self.id = data["id"]
    self.displayName = data["displayName"]
    self.deployStatusPretty = data["deployStatusPretty"]
    self.createdAtMs = data["createdAtMs"]


class RuntimePythonState:
  source: Union[str, None] = None
  name: Union[str, None] = None
  argNames: Union[List[str], None] = None
  argTypes: Union[Dict[str, str], None] = None
  namespaceVarsDesc: Union[Dict[str, str], None] = None
  namespaceFunctions: Union[Dict[str, str], None] = None
  namespaceImports: Union[Dict[str, str], None] = None
  namespaceFroms: Union[Dict[str, str], None] = None
  requirementsTxt: Union[str, None] = None
  pythonVersion: Union[str, None] = None
  errors: Union[List[str], None] = None # Not on TS version
  namespaceVars: Union[Dict[str, str], None] = None # Split in TS to S3DeploymentPythonState

  def asDict(self):
    d: Dict[str, Any] = {}
    for k, v in self.__dict__.items():
      d[k] = v
    return d

RuntimeType = Union[Literal['Deployment'], Literal['TrainingJob']]


class ResultDescription:
  inputId: Union[str, int, bool, None]
  arguments: List[Union[str, int, bool, None]]
  resultDesc: List[str]
  resultPickle: Union[List[str], None]

  def __init__(self, data: Dict[str, Any]):
    self.inputId = data["inputId"]
    self.arguments = data["arguments"]
    self.resultDesc = data["resultDesc"]
    self.resultPickle = data.get("resultPickle", None)


class RuntimeResultInfo:
  runtimeId: str
  runtimeResultId: str
  createdAtMs: int
  results: Union[List[ResultDescription], None] = None
  runningAtMs: Union[int, None]
  completedAtMs: Union[int, None]
  failedAtMs: Union[int, None]
  ownerInfo: OwnerInfo

  def __init__(self, data: Dict[str, Any]):
    self.runtimeId = data["runtimeId"]
    self.runtimeResultId = data["runtimeResultId"]
    self.createdAtMs = data["createdAtMs"]
    if "results" in data and type(data["results"]) == list: # can be None
      self.results = [ResultDescription(r) for r in data["results"]]
    self.runningAtMs = data.get("runningAtMs", None)
    self.completedAtMs = data.get("completedAtMs", None)
    self.failedAtMs = data.get("failedAtMs", None)
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


class RuntimeInfo:
  id: str
  name: str
  version: str
  restUrl: str
  snowUrl: str
  forwardLambdaArn: Union[str, None]
  pythonState: RuntimePythonState
  createdAtMs: int
  apiAvailableAtMs: Union[int, None]
  latest: bool
  environmentStatus: Union[Literal['Updating'], Literal['Ready'], Literal['Error'], Literal['Unknown']]
  ownerInfo: OwnerInfo
  runtimeResults: Union[List[RuntimeResultInfo], None] = None

  def __init__(self, data: Dict[str, Any]):
    self.id = data["id"]
    self.name = data["name"]
    self.version = data["version"]
    self.restUrl = data["restUrl"]
    self.snowUrl = data["snowUrl"]
    self.forwardLambdaArn = data["forwardLambdaArn"]
    self.pythonState = data["pythonState"]
    self.createdAtMs = data["createdAtMs"]
    self.apiAvailableAtMs = data["apiAvailableAtMs"]
    self.latest = data["latest"]
    self.environmentStatus = data["environmentStatus"]
    self.ownerInfo = OwnerInfo(data["ownerInfo"])
    if "runtimeResults" in data: self.runtimeResults = [RuntimeResultInfo(r) for r in data["runtimeResults"]]



class NotebookEnv:
  userEmail: Union[str, None] = None
  signedToken: Union[str, None] = None
  uuid: Union[str, None] = None
  authenticated: bool = False
  workspaceName: Union[str, None] = None
  mostRecentVersion: Union[str, None] = None

  def __init__(self, data: Union[Dict[str, Any], None]):
    if not data: return
    self.userEmail = data["userEmail"]
    self.signedToken = data["signedToken"]
    self.uuid = data["uuid"]
    self.authenticated = data["authenticated"]
    self.workspaceName = data["workspaceName"]
    self.mostRecentVersion = data["mostRecentVersion"]


class NotebookResponse:
  error: Union[str, None] = None
  message: Union[str, None] = None
  notebookEnv: Union[NotebookEnv, None] = None
  datasets: Union[List[DatasetDesc], None] = None
  dsrDownloadInfo: Union[ResultDownloadInfo, None] = None
  warehouses: Union[List[GenericWarehouse], None] = None
  runtimeOverviewUrl: Union[str, None] = None
  deployments: Union[List[RuntimeInfo], None] = None
  trainingJobs: Union[List[RuntimeInfo], None] = None
  tjResultDownloadInfo: Union[ResultDownloadInfo, None] = None

  def __init__(self, data: Dict[str, Any]):
    if "error" in data: self.error = data["error"]
    if "message" in data: self.message = data["message"]
    if "notebookEnv" in data: self.notebookEnv = NotebookEnv(data["notebookEnv"])
    if "datasets" in data: self.datasets = [DatasetDesc(d) for d in data["datasets"]]
    if "dsrDownloadInfo" in data: self.dsrDownloadInfo = ResultDownloadInfo(data["dsrDownloadInfo"])
    if "warehouses" in data: self.warehouses = [GenericWarehouse(w) for w in data["warehouses"]]
    if "runtimeOverviewUrl" in data: self.runtimeOverviewUrl = data["runtimeOverviewUrl"]
    if "deployments" in data: self.deployments = [RuntimeInfo(d) for d in data["deployments"]]
    if "trainingJobs" in data: self.trainingJobs = [RuntimeInfo(t) for t in data["trainingJobs"]]
    if "tjResultDownloadInfo" in data: self.tjResultDownloadInfo = ResultDownloadInfo(data["tjResultDownloadInfo"])
