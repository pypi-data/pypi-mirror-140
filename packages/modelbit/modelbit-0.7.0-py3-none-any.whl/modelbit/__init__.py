__version__ = "0.7.0"
__author__ = 'Modelbit'

from typing import cast, Union, Callable, Any, Dict

from . import modelbit_core
from . import datasets
from . import warehouses
from . import runtime
from . import deployments
from . import training_jobs
from . import secure_storage
from . import utils
from . import helpers
from . import session

# Nicer UX for customers: from modelbit import Deployment
class Deployment(runtime.Deployment): ...
class TrainingJob(runtime.TrainingJob): ...

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
      if type(obj) in [Deployment, TrainingJob, runtime.Deployment, runtime.TrainingJob]: return True
      # catch modelbit._reload() class differences
      if obj.__class__.__name__ in ['Deployment', 'TrainingJob']: return True
    except:
      return False
    return False

  # Public mb.* API
  def isAuthenticated(self): return self._mbCore.isAuthenticated()
  
  def printAuthenticatedMsg(self): return self._mbCore.printAuthenticatedMsg()
  
  def datasets(self): return datasets.Datasets(self._mbCore)
  
  def get_dataset(self, dataset_name: str): return datasets.Datasets(self._mbCore).get(dataset_name)

  def get_training_job(self, training_job_name: str, result_id: Union[str, int, None] = None):
    return training_jobs.TrainingJobs(self._mbCore).get(training_job_name, result_id)
  
  def warehouses(self): return warehouses.Warehouses(self._mbCore)  

  def Deployment(self, 
      name: Union[str, None] = None,
      deploy_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None):
    return Deployment(name=name, deploy_function=deploy_function, python_version=python_version)

  def TrainingJob(self,
      name: Union[str, None] = None,
      train_function: Union[Callable[..., Any], None] = None,
      python_version: Union[str, None] = None):
    return TrainingJob(name=name, train_function=train_function, python_version=python_version)
  
  def deployments(self): return deployments.Deployments(self._mbCore)

  def training_jobs(self): return training_jobs.TrainingJobs(self._mbCore)

  def _createRuntime(self,
      rtType: helpers.RuntimeType,
      deployableObj: Union[Callable[..., Any], runtime.Runtime, None],
      name: Union[str, None] = None,
      python_version: Union[str, None] = None):
    if not self.isAuthenticated():
      self._mbCore.performLogin()
      return
    if self._objIsDeployment(deployableObj):
      deployableObj = cast(runtime.Runtime, deployableObj)
      if deployableObj.rtType == 'TrainingJob' and rtType == 'Deployment':
        return print("Error: Use .train(...) instead of .deploy(...) with this Training Job")
      elif deployableObj.rtType == 'Deployment' and rtType == 'TrainingJob':
        return print("Error: Use .deploy(...) instead of .train(...) with this Deployment")
      return deployableObj.deploy(self._mbCore)
    if callable(deployableObj):
      if rtType == 'Deployment':
        dep = self.Deployment(name=name, deploy_function=deployableObj, python_version=python_version)
        return dep.deploy(self._mbCore)
      elif rtType == 'TrainingJob':
        tj = self.TrainingJob(name=name, train_function=deployableObj, python_version=python_version)
        return tj.deploy(self._mbCore)
    print("First argument doesn't looks like a deployable object.")

  def deploy(self,
      deployableObj: Union[Callable[..., Any], runtime.Deployment, None],
      name: Union[str, None] = None,
      python_version: Union[str, None] = None):
    return self._createRuntime('Deployment', deployableObj, name=name, python_version=python_version)

  def train(self,
      deployableObj: Union[Callable[..., Any], runtime.TrainingJob, None],
      name: Union[str, None] = None,
      python_version: Union[str, None] = None):
    return self._createRuntime('TrainingJob', deployableObj, name=name, python_version=python_version)


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
  importlib.reload(runtime)
  importlib.reload(deployments)
  importlib.reload(training_jobs)
  importlib.reload(secure_storage)
  importlib.reload(utils)
  importlib.reload(helpers)
  importlib.reload(importlib.import_module("modelbit"))
  print("All modules reloaded, except session.")
