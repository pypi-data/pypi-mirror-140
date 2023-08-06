__version__ = "0.6.4"
__author__ = 'Modelbit'

from typing import cast, Union, Callable, Any, Dict

from . import modelbit_core
from . import datasets
from . import warehouses
from . import deployment
from . import deployments
from . import utils
from . import helpers
from . import session

# Nicer UX for customers: from modelbit import Deployment
class Deployment(deployment.Deployment): ...

class _ClientSession:
  _mbCore: modelbit_core.ModelbitCore

  def _resetState(self):
    self._mbCore = modelbit_core.ModelbitCore(__version__)
    self._mbCore.performLogin()
    session.rememberSession(self)
  
  def __init__(self):
    self._resetState()

  # Interface for pickle. We don't currently _need_ to save anything, and explicitly don't want to save auth state
  def __getstate__(self):
    pickleState: Dict[str, str] = {}
    return pickleState # need to return something. Returning None won't call setstate

  def __setstate__(self, pickledState: Dict[str, str]):
    self._resetState()

  def __str__(self):
    return "modelbit.login()"

  def _objIsDeployment(self, obj: Any):
    try:
      if type(obj) == deployment.Deployment: return True
      if obj.__class__.__name__ == 'Deployment': return True # catch modelbit._reload() class differences
    except:
      return False
    return False

  # Public mb.* API
  def isAuthenticated(self): return self._mbCore.isAuthenticated()
  
  def printAuthenticatedMsg(self): return self._mbCore.printAuthenticatedMsg()
  
  def datasets(self): return datasets.Datasets(self._mbCore)
  
  def get_dataset(self, dataset_name: str): return datasets.Datasets(self._mbCore).get(dataset_name)
  
  def warehouses(self): return warehouses.Warehouses(self._mbCore)  

  def Deployment(self, 
      name: Union[str, None] = None,
      deploy_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None,
      ram_mb: Union[int, None] = None):
    return deployment.Deployment(name, deploy_function, python_version, ram_mb)
  
  def deployments(self): return deployments.Deployments(self._mbCore)

  def deploy(self,
      deployableObj: Union[Callable[..., Any], deployment.Deployment, None],
      name: Union[str, None] = None,
      # deploy_function is not here because it can be the first argument
      python_version: Union[str, None] = None,
      ram_mb: Union[int, None] = None):
    if not self.isAuthenticated():
      self._mbCore.performLogin()
      return
    if self._objIsDeployment(deployableObj):
      deployableObj = cast(deployment.Deployment, deployableObj)
      return deployableObj.deploy(self._mbCore)
    if callable(deployableObj):
      dep = self.Deployment(name=name, deploy_function=deployableObj, python_version=python_version, ram_mb=ram_mb)
      return dep.deploy(self._mbCore)
    print("First argument doesn't looks like a deployable object.")


def login():
  existingSession = cast(Union[_ClientSession, None], session.anyAuthenticatedSession())
  if existingSession:
    existingSession.printAuthenticatedMsg()
    return existingSession
  return _ClientSession()

def _reload(): # type: ignore
  import importlib
  importlib.reload(modelbit_core)
  importlib.reload(datasets)
  importlib.reload(warehouses)
  importlib.reload(deployment)
  importlib.reload(deployments)
  importlib.reload(utils)
  importlib.reload(helpers)
  importlib.reload(importlib.import_module("modelbit"))
  print("All modules reloaded, except session.")
