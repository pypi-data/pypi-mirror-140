from typing import Union, List, Dict, Any, cast, Callable
import inspect, re, pickle, codecs
from ipywidgets import FileUpload
from IPython.display import display, clear_output

from .modelbit_core import ModelbitCore
from .utils import printMk, printError
from .session import anyAuthenticatedSession as untypedAnyAuthenticatedSession
from .helpers import DeploymentPythonState


def anyAuthedModelbitCore():
  clientSession = cast(Union[Any, None], untypedAnyAuthenticatedSession())
  if clientSession:
    return cast(ModelbitCore, clientSession._mbCore)
  return None

class DeployStatusNotes:
  deployable: bool
  notes: List[str]

  def __init__(self, deployable: bool, notes: List[str]):
    self.deployable = deployable
    self.notes = notes

  def statusMsg(self):
    if self.deployable: return 'Ready to Deploy'
    return 'Not Ready to Deploy'

  def statusStyle(self):
    if self.deployable: return "color:green; font-weight: bold;"
    return "color:gray; font-weight: bold;"


class NamespaceCollection:
  functions: Dict[str, str] = {}
  vars: Dict[str, Any] = {}
  imports: Dict[str, str] = {}


class Deployment:
  _requirementsTxt: Union[str, None] = None
  _deployName: Union[str, None] = None
  _deployFunc: Union[Callable[..., Any], None] = None
  _pythonVersion = '3.9' # Default version
  _ramMb: Union[int, None] = None

  ALLOWED_PY_VERSIONS = ['3.6', '3.7', '3.8', '3.9']
  _CODE_STYLE = "font-family: monospace; font-size: 0.95em; font-weight: medium; color: #714488;"

  MAX_REQUIREMENTS_TXT = 20_000
  LAMBDA_RAM_MAX_MB = 10_240
  LAMBDA_RAM_MIN_MB = 128

  # Keep these kwargs in sync with __init__.py/.Deployment(...)
  def __init__(self, name: Union[str, None] = None, deploy_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None, ram_mb: Union[int, None] = None):
    if name: self.set_name(name)
    if deploy_function: self.set_deploy_function(deploy_function)
    if python_version: self.set_python_version(python_version)
    if ram_mb: self.set_ram_mb(ram_mb)

  def _repr_markdown_(self):
    return self._describe()

  def set_name(self, name: str):
    if not re.match('^[a-zA-Z0-9_]+$', name):
      raise Exception("Deployment names should be alphanumeric with underscores.")
    self._deployName = name
    return self

  def set_python_version(self, version: str):
    if version not in self.ALLOWED_PY_VERSIONS:
      return self._selfError(f'Python version should be one of {self.ALLOWED_PY_VERSIONS}.')
    self._pythonVersion = version
    return self

  def set_ram_mb(self, ramMb: int):
    if type(ramMb) != int or ramMb < self.LAMBDA_RAM_MIN_MB or ramMb > self.LAMBDA_RAM_MAX_MB:
      return self._selfError(f'ram_mb must be an integer between {self.LAMBDA_RAM_MIN_MB} and {self.LAMBDA_RAM_MAX_MB}.')
    self._ramMb = ramMb

  def set_requirements_txt(self):
    upload = FileUpload(accept='.txt', multiple=False)
    display(upload)
    def onUploadChange(change: Dict[str, str]):
        clear_output(wait=True)
        newContent = cast(Dict[str, Any], change['new'])
        for v in newContent.values():
          content = cast(str, v['content'].decode('utf-8'))
          if len(content) < self.MAX_REQUIREMENTS_TXT:
            self._requirementsTxt = content
            mbMain = anyAuthedModelbitCore()
            if mbMain:
              mbMain.getJson("jupyter/v1/deployments/prep_environment", {
                "environment": {
                  "requirementsTxt": self._requirementsTxt,
                  "pythonVersion": self._pythonVersion
                }
              })
          else:
            printError("The requirements.txt file is too large.")
        printMk(self._describe())
    upload.observe(onUploadChange, names=['value']) # type: ignore
    return None

  def set_deploy_function(self, func: Callable[..., Any]):
    self._deployFunc = func
    if callable(func) and self._deployName == None: self.set_name(func.__name__)
    return self

  def deploy(self, mbMain: Union[ModelbitCore, None] = None):
    if not mbMain:
      mbMain = anyAuthedModelbitCore()
    if not mbMain:
      printError("Unable to deploy because session isn't authenticated.")
      return self

    status = self._getStatusNotes()
    depState, errors = self._getFuncProps(self._deployFunc)
    if not status.deployable or len(errors) > 0:
      printError("Deployment has errors and cannot be deployed.")
      return self

    resp = mbMain.getJsonOrPrintError("jupyter/v1/deployments/create", {
      "deployment": {
        "name": self._deployName,
        "ramMb": self._ramMb,
        "pyState": {
          **depState.asDict(),
          "requirementsTxt": self._requirementsTxt,
          "pythonVersion": self._pythonVersion
        }}})
    if not resp:
      printMk(f'Error while deploying.')
    elif resp.error:
      printMk(f'Error while deploying: {resp.error}')
    elif resp.deployOverviewUrl:
      if resp.message: printMk(resp.message)
      printMk(f'<a href="{resp.deployOverviewUrl}" target="_blank">View status and integration options.</a>')
    else:
      printMk(f'Unknown error while deploying.')
    return None

  def _selfError(self, txt: str):
    printError(txt)
    return None

  def _describe(self):
    nonStr = '(None)'
    def codeWrap(txt: str):
      if txt == nonStr: return nonStr
      return self._wrapStyle(txt, self._CODE_STYLE)

    status = self._getStatusNotes()
    statusWithStyle = self._wrapStyle(status.statusMsg(), status.statusStyle())
    md = ""
    if self._deployName != None: md += f'**{self._deployName}**: '
    md += f'{statusWithStyle}\n\n'
    statusList = "\n".join([f'* {n}' for n in status.notes])
    if len(statusList) > 0: md += statusList + "\n\n"

    md += "| Property | Value |\n" + "|:-|:-|\n"
    funcProps, _ = self._getFuncProps(self._deployFunc)
    funcSig = nonStr
    nsFuncs = nonStr
    nsVars = nonStr
    nsImports = nonStr
    if funcProps != None:
      if funcProps.name and funcProps.argNames:
        funcSig = f"{funcProps.name}({', '.join(funcProps.argNames)})"
      if funcProps.namespaceFunctions and len(funcProps.namespaceFunctions) > 0:
        nsFuncs = "<br/>".join([k for k,_ in funcProps.namespaceFunctions.items()])
      if funcProps.namespaceVarsDesc and len(funcProps.namespaceVarsDesc) > 0:
        nsVars = "<br/>".join([f'{k}: {v}' for k,v in funcProps.namespaceVarsDesc.items()])
      if funcProps.namespaceImports and len(funcProps.namespaceImports) > 0:
        nsImports = "<br/>".join([f'{v} as {k}' for k,v in funcProps.namespaceImports.items()])
    md += f"| Function | {codeWrap(funcSig)} |\n"
    if nsFuncs != nonStr: md += f"| Helpers | {codeWrap(nsFuncs)} |\n"
    if nsVars != nonStr: md += f"| Values | {codeWrap(nsVars)} |\n"
    if nsImports != nonStr: md += f"| Imports | {codeWrap(nsImports)} |\n"
    md += f"| Python Version | {codeWrap(self._pythonVersion or nonStr)} |\n"

    deps = nonStr
    if self._requirementsTxt and len(self._requirementsTxt) > 0:
      depsList = self._requirementsTxt.splitlines()
      maxDepsShown = 7
      if len(depsList) > maxDepsShown:
        deps = "<br/>".join([d for d in depsList[:maxDepsShown]])
        numLeft = len(depsList) - maxDepsShown
        deps += f'<br/><span style="font-style: italic;">...and {numLeft} more.</span>'
      else:
        deps = "<br/>".join([d for d in depsList])
    md += f"| requirements.txt | {codeWrap(deps)} |\n"
    if self._ramMb != None:
      ramDesc = f"{self._ramMb} MB"
      md += f"| RAM | {codeWrap(ramDesc)} | \n"
    return md

  def _getFuncProps(self, func: Union[Callable[..., Any], None]):
    errors: List[str] = []
    props: DeploymentPythonState = DeploymentPythonState()
    if not callable(func):
      errors.append('The deploy_function parameter does not appear to be a function.')
    else:
      props.name = func.__name__
      props.source = inspect.getsource(func)
      props.argNames = list(func.__code__.co_varnames[:func.__code__.co_argcount] or [])
      props.argTypes = self._annotationsToTypeStr(func.__annotations__)
      nsCollection = NamespaceCollection()
      self._collectNamespaceDeps(func, nsCollection)
      props.namespaceFunctions = nsCollection.functions
      props.namespaceVars = self._pickleValues(nsCollection.vars)
      props.namespaceVarsDesc = self._strValues(nsCollection.vars)
      props.namespaceImports = nsCollection.imports
    return (props, errors)

  def _annotationsToTypeStr(self, annotations: Dict[str, Any]):
    annoStrs: Dict[str, str] = {}
    for name, tClass in annotations.items():
      annoStrs[name] = tClass.__name__
    return annoStrs

  def _collectNamespaceDeps(self, func: Callable[..., Any], collection: NamespaceCollection):
    if not callable(func): return collection
    globalsDict = func.__globals__ # type: ignore
    for maybeFuncVarName in func.__code__.co_names:
      if maybeFuncVarName in globalsDict:
        maybeFuncVar = globalsDict[maybeFuncVarName]
        if str(maybeFuncVar).startswith('<function'):
          argNames = list(maybeFuncVar.__code__.co_varnames or [])
          funcSig = f"{maybeFuncVar.__name__}({', '.join(argNames)})"
          if funcSig not in collection.functions:
            collection.functions[funcSig] = inspect.getsource(maybeFuncVar)
            self._collectNamespaceDeps(maybeFuncVar, collection)
        elif str(maybeFuncVar).startswith('<module'):
          collection.imports[maybeFuncVarName] = maybeFuncVar.__name__
        else:
          collection.vars[maybeFuncVarName] = maybeFuncVar

  def _getStatusNotes(self):
    notes: List[str] = []
    if not self._deployName:
      cmd = self._wrapStyle(".set_name('name')", self._CODE_STYLE)
      notes.append(f'Run {cmd} to specify the deployment\'s name.')
    if not self._deployFunc:
      cmd = self._wrapStyle(".set_deploy_function(func, args = {\"arg1\": value1, ...})", self._CODE_STYLE)
      notes.append(f'Run {cmd} to specify the deployment\'s runtime.')
    else:
      _, errors = self._getFuncProps(self._deployFunc)
      if len(errors) > 0: notes.extend(errors)
    if not self._pythonVersion:
      cmd = self._wrapStyle(".set_python_version('version')", self._CODE_STYLE)
      notes.append(f'Run {cmd} to set the python version to one of {self.ALLOWED_PY_VERSIONS}.')
    if len(notes) > 0:
      return DeployStatusNotes(False, notes)
    else:
      cmd = self._wrapStyle("mb.deploy(dep)", self._CODE_STYLE)
      notes.append(f'Run {cmd} to deploy this function to Modelbit.')
      return DeployStatusNotes(True, notes)

  def _wrapStyle(self, text: str, style: str):
    return f'<span style="{style}">{text}</span>'

  def _pickleValues(self, args: Dict[str, Any]):
    newDict: Dict[str, str] = {}
    for k, v in args.items():
      newDict[k] = codecs.encode(pickle.dumps(v), "base64").decode()
    return newDict

  def _strValues(self, args: Dict[str, Any]):
    newDict: Dict[str, str] = {}
    for k, v in args.items():
      newDict[k] = str(v)
    return newDict
