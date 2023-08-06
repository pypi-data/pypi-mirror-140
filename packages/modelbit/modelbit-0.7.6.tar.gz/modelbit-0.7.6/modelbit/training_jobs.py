from typing import List, Dict, Union
import json, pickle, codecs

from .utils import formatImageTag
from .helpers import RuntimeInfo, ResultDownloadInfo, RuntimeResultInfo, ResultDescription
from .modelbit_core import ModelbitCore
from .secure_storage import getSecureData

class TrainingJobResult:
  def __init__(self, rdi: ResultDownloadInfo, tjName: str, tjVersion: str, tjResultId: Union[str, int, None]):
    self._tjName = tjName
    self._tjVersion = tjVersion
    self._tjResultId = tjResultId
    self._results: Union[List[ResultDescription], None] = None
    if self._tjResultId:
      downloadName = f"{self._tjName}'s result {self._tjResultId}"
    else:
      downloadName = f"{self._tjName}'s latest result"
    stream = getSecureData(rdi, downloadName)
    if stream != None:
      asSimpleVal = json.loads(stream.read().decode())
      resultsList = json.loads(asSimpleVal["v"])
      self._results = [ResultDescription(r) for r in resultsList["results"]]
    else:
      raise Exception("Unable to fetch result.")

  def load(self):
    if self._results == None or len(self._results) != 1 or len(self._results[0].resultDesc) != 2:
      raise Exception("Multi- and many-return functions are not yet supported.")
    pickleVal = self._results[0].resultPickle
    if pickleVal == None:
      raise Exception("No data to load.")
    unpickle = pickle.loads(codecs.decode(pickleVal[1].encode(), "base64"))
    return unpickle


class TrainingJobDetails:
  def __init__(self, mbMain: ModelbitCore, name: str, version: Union[str, int, None] = None):
    self._mbMain = mbMain
    resp = self._mbMain.getJsonOrPrintError("jupyter/v1/runtimes/get", {
      "runtimeType": "TrainingJob",
      "runtimeName": name,
      "runtimeVersion": version
    })
    if resp and resp.trainingJobs and len(resp.trainingJobs) == 1:
      self._tj = resp.trainingJobs[0]
    else:
      raise Exception(f"Unable to locate training job '{name}'")

  def get_result(self, result_id: Union[str, int, None] = None):
    if result_id: result_id = str(result_id)
    resp = self._mbMain.getJsonOrPrintError("jupyter/v1/runtimes/get_result", {
      "runtimeType": "TrainingJob",
      "runtimeName": self._tj.name,
      "runtimeVersion": self._tj.version,
      "resultId": result_id,
    })
    if resp and resp.tjResultDownloadInfo:
      tjr = TrainingJobResult(resp.tjResultDownloadInfo, self._tj.name, self._tj.version, result_id)
      return tjr.load()

  def _repr_markdown_(self):
    return self._describe()

  def _resultStatus(self, rr: RuntimeResultInfo):
    if rr.completedAtMs:
      return '<span style="color:green; font-weight: bold;">Complete</b>'
    elif rr.failedAtMs:
      return '<span style="color:gray; font-weight: bold;">Failed</b>'
    else:
      return "Running..."

  def _resultOutputs(self, rr: RuntimeResultInfo):
    if rr.results == None or type(rr.results) != list or len(rr.results) == 0: return ""
    if len(rr.results) == 1: return ", ".join(rr.results[0].resultDesc[1:])
    return "Not Yet Implemented" # NIY

  def _describe(self):
    md: List[str] = []
    md.append(f"<b>{self._tj.name}</b> (v{self._tj.version})")
    if self._tj.runtimeResults and len(self._tj.runtimeResults) > 0:
      md.append("")
      md.append("| Result ID | Owner | Status | Results |")
      md.append("|:-|:-:|:-|:-|")
      for rr in self._tj.runtimeResults:
        ownerImageTag = formatImageTag(rr.ownerInfo.imageUrl, rr.ownerInfo.name)
        md.append(f"| {rr.createdAtMs} | { ownerImageTag } | { self._resultStatus(rr) } | { self._resultOutputs(rr) } ")
      md.append("")
    return "\n".join(md)


class TrainingJobs:
  def __init__(self, mbMain: ModelbitCore):
      self._mbMain = mbMain
      self._trainingJobs: List[RuntimeInfo] = []
      resp = self._mbMain.getJsonOrPrintError("jupyter/v1/runtimes/list?runtimeType=TrainingJob")
      if resp and resp.trainingJobs:
          self._trainingJobs = resp.trainingJobs

  def _repr_markdown_(self):
      return self._makeTrainingJobsMkTable()

  def _makeTrainingJobsMkTable(self):
      import timeago, datetime
      from collections import defaultdict

      if len(self._trainingJobs) == 0:
          return "There are no training jobs to show."
      tjByName: Dict[str, List[RuntimeInfo]] = defaultdict(lambda: [])
      for t in self._trainingJobs:
          tjByName[t.name].append(t)

      formatStr = (
          "| Name | Owner | Status | Versions | Updated | \n" + "|:-|:-:|:-|-:|:-|\n"
      )
      for tList in tjByName.values():
          lt = tList[0] # latest training job
          versionCount = len(tList)
          connectedAgo = timeago.format(
              datetime.datetime.fromtimestamp(lt.createdAtMs / 1000),
              datetime.datetime.now(),
          )
          ownerImageTag = formatImageTag(lt.ownerInfo.imageUrl, lt.ownerInfo.name)
          formatStr += f'| { lt.name } | { ownerImageTag } | {lt.environmentStatus} | { versionCount } |  { connectedAgo } |\n'
      return formatStr

  def get(self, name: str, version: Union[str, int, None] = None):
    return TrainingJobDetails(self._mbMain, name, version)
