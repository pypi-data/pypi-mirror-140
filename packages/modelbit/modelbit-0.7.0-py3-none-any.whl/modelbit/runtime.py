from typing import Union, List, Dict, Any, cast, Callable
import inspect, re, pickle, codecs
from ipywidgets import FileUpload
from IPython.display import display, clear_output

from .modelbit_core import ModelbitCore
from .utils import printMk, printError
from .session import anyAuthenticatedSession as untypedAnyAuthenticatedSession
from .helpers import RuntimePythonState, RuntimeType


def anyAuthedModelbitCore():
  clientSession = cast(Union[Any, None], untypedAnyAuthenticatedSession())
  if clientSession:
    return cast(ModelbitCore, clientSession._mbCore)
  return None

class RuntimeStatusNotes:
  deployable: bool
  notes: List[str]

  def __init__(self, deployable: bool, notes: List[str]):
    self.deployable = deployable
    self.notes = notes

  def statusMsg(self):
    if self.deployable: return 'Ready'
    return 'Not Ready'

  def statusStyle(self):
    if self.deployable: return "color:green; font-weight: bold;"
    return "color:gray; font-weight: bold;"


class NamespaceCollection:
  functions: Dict[str, str] = {}
  vars: Dict[str, Any] = {}
  imports: Dict[str, str] = {}
  froms: Dict[str, str] = { "*": "typing" }


class Runtime:
  _runtimeTypeName = "runtime"
  _requirementsTxt: Union[str, None] = None
  _deployName: Union[str, None] = None
  _deployFunc: Union[Callable[..., Any], None] = None
  _pythonVersion = '3.8' # Default version
  rtType: RuntimeType

  ALLOWED_PY_VERSIONS = ['3.6', '3.7', '3.8', '3.9']
  _CODE_STYLE = "font-family: monospace; font-size: 0.95em; font-weight: medium; color: #714488;"

  MAX_REQUIREMENTS_TXT = 20_000
  LAMBDA_RAM_MAX_MB = 10_240
  LAMBDA_RAM_MIN_MB = 128

  def __init__(self, rtType: RuntimeType, name: Union[str, None] = None, main_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None):
    self.rtType = rtType
    if name: self.set_name(name)
    if main_function: self._set_main_function(main_function)
    if python_version: self.set_python_version(python_version)

  def _repr_markdown_(self):
    return self._describe()

  def set_name(self, name: str):
    if not re.match('^[a-zA-Z0-9_]+$', name):
      raise Exception("Names should be alphanumeric with underscores.")
    self._deployName = name
    return self

  def set_python_version(self, version: str):
    if version not in self.ALLOWED_PY_VERSIONS:
      return self._selfError(f'Python version should be one of {self.ALLOWED_PY_VERSIONS}.')
    self._pythonVersion = version
    return self

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
              mbMain.getJson("jupyter/v1/runtimes/prep_environment", {
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

  def _set_main_function(self, func: Callable[..., Any]):
    self._deployFunc = func
    if callable(func) and self._deployName == None: self.set_name(func.__name__)
    return self

  def train(self, mbMain: Union[ModelbitCore, None] = None):
    self.deploy(mbMain)

  def deploy(self, mbMain: Union[ModelbitCore, None] = None):
    if not mbMain:
      mbMain = anyAuthedModelbitCore()
    if not mbMain:
      printError("Unable to continue because session isn't authenticated.")
      return self

    status = self._getStatusNotes()
    rtState, errors = self._getFuncProps(self._deployFunc)
    if not status.deployable or len(errors) > 0:
      printError("Unable to continue because errors are present.")
      return self

    resp = mbMain.getJsonOrPrintError("jupyter/v1/runtimes/create", {
      "runtime": {
        "name": self._deployName,
        "type": self.rtType,
        "pyState": {
          **rtState.asDict(),
          "requirementsTxt": self._requirementsTxt,
          "pythonVersion": self._pythonVersion
        }}})
    if not resp:
      printMk(f'Error processing request: no response from server.')
    elif resp.error:
      printMk(f'Error processing request: {resp.error}')
    elif resp.runtimeOverviewUrl:
      if resp.message: printMk(resp.message)
      message = "View status and integration options."
      if self.rtType == 'TrainingJob':
        message = "View training status and output."
      printMk(f'<a href="{resp.runtimeOverviewUrl}" target="_blank">{message}</a>')
    else:
      printMk(f"Unknown error while processing request (server response in unexpected format).")
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
    nsImports: List[str] = []
    if funcProps != None:
      if funcProps.name and funcProps.argNames:
        funcSig = f"{funcProps.name}({', '.join(funcProps.argNames)})"
      if funcProps.namespaceFunctions and len(funcProps.namespaceFunctions) > 0:
        nsFuncs = "<br/>".join([k for k,_ in funcProps.namespaceFunctions.items()])
      if funcProps.namespaceVarsDesc and len(funcProps.namespaceVarsDesc) > 0:
        nsVars = "<br/>".join([f'{k}: {v}' for k,v in funcProps.namespaceVarsDesc.items()])
      if funcProps.namespaceFroms and len(funcProps.namespaceFroms) > 0:
        for k,v in funcProps.namespaceFroms.items():
          nsImports.append(f'from {v} import {k}')
      if funcProps.namespaceImports and len(funcProps.namespaceImports) > 0:
        for k,v in funcProps.namespaceImports.items():
          nsImports.append(f'import {v} as {k}')
    md += f"| Function | {codeWrap(funcSig)} |\n"
    if nsFuncs != nonStr: md += f"| Helpers | {codeWrap(nsFuncs)} |\n"
    if nsVars != nonStr: md += f"| Values | {codeWrap(nsVars)} |\n"
    if len(nsImports) > 0: md += f"| Imports | {codeWrap('<br/>'.join(nsImports))} |\n"
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
    return md

  def _getFuncProps(self, func: Union[Callable[..., Any], None]):
    errors: List[str] = []
    props: RuntimePythonState = RuntimePythonState()
    if not callable(func):
      errors.append('The main_function parameter does not appear to be a function.')
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
      props.namespaceFroms = nsCollection.froms
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
        if "__module__" in dir(maybeFuncVar):
          if maybeFuncVar.__module__ == "__main__": # the user's functions
            argNames = list(maybeFuncVar.__code__.co_varnames or [])
            funcSig = f"{maybeFuncVar.__name__}({', '.join(argNames)})"
            if funcSig not in collection.functions:
              collection.functions[funcSig] = inspect.getsource(maybeFuncVar)
              self._collectNamespaceDeps(maybeFuncVar, collection)
          else: # functions imported by the user from elsewhere
            if inspect.isclass(maybeFuncVar):
              collection.froms[maybeFuncVarName] = maybeFuncVar.__module__
            elif callable(maybeFuncVar):
              collection.froms[maybeFuncVarName] = maybeFuncVar.__module__
            elif isinstance(maybeFuncVar, object):
              collection.froms[maybeFuncVar.__class__.__name__] = maybeFuncVar.__module__
              collection.vars[maybeFuncVarName] = maybeFuncVar
            else:
              collection.froms[maybeFuncVarName] = f"NYI: {maybeFuncVar.__module__}"
        elif str(maybeFuncVar).startswith('<module'):
          collection.imports[maybeFuncVarName] = maybeFuncVar.__name__
        else:
          collection.vars[maybeFuncVarName] = maybeFuncVar

  def _getStatusNotes(self):
    notes: List[str] = []
    if not self._deployName:
      cmd = self._wrapStyle(".set_name('name')", self._CODE_STYLE)
      notes.append(f'Run {cmd} to specify the {self._runtimeTypeName}\'s name.')
    if not self._deployFunc:
      funcName = "set_deploy_function"
      if self.rtType == 'TrainingJob': funcName = "set_train_function"
      cmd = self._wrapStyle("." + funcName + "(func, args = {\"arg1\": value1, ...})", self._CODE_STYLE)
      notes.append(f'Run {cmd} to specify the {self._runtimeTypeName}\'s runtime.')
    else:
      _, errors = self._getFuncProps(self._deployFunc)
      if len(errors) > 0: notes.extend(errors)
    if not self._pythonVersion:
      cmd = self._wrapStyle(".set_python_version('version')", self._CODE_STYLE)
      notes.append(f'Run {cmd} to set the python version to one of {self.ALLOWED_PY_VERSIONS}.')
    if len(notes) > 0:
      return RuntimeStatusNotes(False, notes)
    else:
      cmd = self._wrapStyle("mb.deploy(...)", self._CODE_STYLE)  
      if self.rtType == 'TrainingJob':
        cmd = self._wrapStyle("mb.train(...)", self._CODE_STYLE)
      notes.append(f'Run {cmd} to send this function to Modelbit.')
      return RuntimeStatusNotes(True, notes)

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
      newDict[k] = re.sub(r'\s+', " ", str(v))
    return newDict


class Deployment(Runtime):
  _runtimeTypeName = "deployment"

  def __init__(self, name: Union[str, None] = None, deploy_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None):
      Runtime.__init__(self, 'Deployment', name=name, main_function=deploy_function, python_version=python_version)

  def set_deploy_function(self, func: Callable[..., Any]): self._set_main_function(func)

class TrainingJob(Runtime):
  _runtimeTypeName = "training job"

  def __init__(self, name: Union[str, None] = None, train_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None):
      Runtime.__init__(self, 'TrainingJob', name=name, main_function=train_function, python_version=python_version)

  def set_train_function(self, func: Callable[..., Any]): self._set_main_function(func)
