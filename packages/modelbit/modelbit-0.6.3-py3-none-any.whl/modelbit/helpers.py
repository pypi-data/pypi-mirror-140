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


class DatasetResultDownloadInfo:
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


class DeploymentPythonState:
  source: Union[str, None] = None
  name: Union[str, None] = None
  argNames: Union[List[str], None] = None
  argTypes: Union[Dict[str, str], None] = None
  namespaceVarsDesc: Union[Dict[str, str], None] = None
  namespaceFunctions: Union[Dict[str, str], None] = None
  namespaceImports: Union[Dict[str, str], None] = None
  requirementsTxt: Union[str, None] = None
  pythonVersion: Union[str, None] = None
  ramMb: Union[int, None] = None
  errors: Union[List[str], None] = None # Not on TS version
  namespaceVars: Union[Dict[str, str], None] = None # Split in TS to S3DeploymentPythonState

  def asDict(self):
    d: Dict[str, Any] = {}
    for k, v in self.__dict__.items():
      d[k] = v
    return d


class DeploymentInfo:
  id: str
  name: str
  version: str
  restUrl: str
  snowUrl: str
  forwardLambdaArn: Union[str, None]
  pythonState: DeploymentPythonState
  createdAtMs: int
  deployedAtMs: Union[int, None]
  latest: bool
  environmentStatus: Union[Literal['Updating'], Literal['Ready'], Literal['Error'], Literal['Unknown']]
  ownerInfo: OwnerInfo

  def __init__(self, data: Dict[str, Any]):
    self.id = data["id"]
    self.name = data["name"]
    self.version = data["version"]
    self.restUrl = data["restUrl"]
    self.snowUrl = data["snowUrl"]
    self.forwardLambdaArn = data["forwardLambdaArn"]
    self.pythonState = data["pythonState"]
    self.createdAtMs = data["createdAtMs"]
    self.deployedAtMs = data["deployedAtMs"]
    self.latest = data["latest"]
    self.environmentStatus = data["environmentStatus"]
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


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
  dsrDownloadInfo: Union[DatasetResultDownloadInfo, None] = None
  warehouses: Union[List[GenericWarehouse], None] = None
  deployOverviewUrl: Union[str, None] = None
  deployments: Union[List[DeploymentInfo], None] = None

  def __init__(self, data: Dict[str, Any]):
    if "error" in data: self.error = data["error"]
    if "message" in data: self.message = data["message"]
    if "notebookEnv" in data: self.notebookEnv = NotebookEnv(data["notebookEnv"])
    if "datasets" in data: self.datasets = [DatasetDesc(d) for d in data["datasets"]]
    if "dsrDownloadInfo" in data: self.dsrDownloadInfo = DatasetResultDownloadInfo(data["dsrDownloadInfo"])
    if "warehouses" in data: self.warehouses = [GenericWarehouse(w) for w in data["warehouses"]]
    if "deployOverviewUrl" in data: self.deployOverviewUrl = data["deployOverviewUrl"]
    if "deployments" in data: self.deployments = [DeploymentInfo(d) for d in data["deployments"]]
