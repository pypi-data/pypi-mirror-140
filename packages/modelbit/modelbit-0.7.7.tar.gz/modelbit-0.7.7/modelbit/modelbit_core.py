from typing import Any, Dict
import os, requests, json

from .utils import printError, printMk, sizeOfFmt
from .helpers import NotebookEnv, NotebookResponse

class ModelbitCore:
  version: str
  _api_host = 'https://app.modelbit.com/'
  _login_host = _api_host
  _api_url = None
  _MAX_DATA_LEN = 10000000

  def __init__(self, version: str):
    self._state: NotebookEnv = NotebookEnv({})
    self.version = version
    osApiHost = os.getenv('MB_JUPYTER_API_HOST')
    if osApiHost: self._api_host = osApiHost
    osLoginHost = os.getenv('MB_JUPYTER_LOGIN_HOST')
    if osLoginHost: self._login_host = osLoginHost
    self._api_url = f'{self._api_host}api/'

  def isAuthenticated(self, testRemote: bool = True) -> bool:
    if testRemote and not self.isAuthenticated(False):
      nbResp = self.getJson("jupyter/v1/login")
      if nbResp.error:
        printError(nbResp.error)
        return False
      if nbResp.notebookEnv: self._state = nbResp.notebookEnv
      return self.isAuthenticated(False)
    return self._state.authenticated


  def getJson(self, path: str, body: Dict[str, Any] = {}) -> NotebookResponse:
    try:
      requestToken = os.getenv('MB_RUNTIME_TOKEN')
      if requestToken == None: requestToken = self._state.signedToken
      data: Dict[str, Any] = {
        "requestToken": requestToken,
        "version": self.version,
      }
      data.update(body)
      dataLen = len(json.dumps(data))
      if (dataLen > self._MAX_DATA_LEN):
        return NotebookResponse({ "error": f'API Error: Request is too large. (Request is {sizeOfFmt(dataLen)} Limit is {sizeOfFmt(self._MAX_DATA_LEN)})' })
      with requests.post(f'{self._api_url}{path}', json=data) as url:
        nbResp = NotebookResponse(url.json())
        if nbResp.notebookEnv: self._state = nbResp.notebookEnv
        return nbResp
    except BaseException as err:
      if type(err) == requests.exceptions.JSONDecodeError:
        return NotebookResponse({ "error": f'Unable to reach Modelbit. Bad response from server.' })
      else:
        return NotebookResponse({ "error": f'Unable to reach Modelbit: {type(err)}' })

  def getJsonOrPrintError(self, path: str, body: Dict[str, Any] = {}):
    nbResp = self.getJson(path, body)
    if not self.isAuthenticated():
      self.performLogin()
      return False
    if nbResp.error:
      printError(nbResp.error)
      return False
    return nbResp

  def _maybePrintUpgradeMessage(self):
    if os.getenv('MB_RUNTIME_TOKEN'): return # runtime environments don't get upgraded
    latestVer = self._state.mostRecentVersion
    nbVer = self.version
    if latestVer and latestVer.split('.') > nbVer.split('.'):
      pipCmd = '<span style="color:#E7699A; font-family: monospace;">pip install --upgrade modelbit</span>'
      printMk(f'Please run {pipCmd} to upgrade to the latest version. ' + 
        f'(Installed: <span style="font-family: monospace">{nbVer}</span>. ' + 
        f' Latest: <span style="font-family: monospace">{latestVer}</span>)')

  def printAuthenticatedMsg(self):
    connectedTag = '<span style="color:green; font-weight: bold;">connected</span>'
    email = self._state.userEmail
    workspace = self._state.workspaceName
    
    printMk(f'You\'re {connectedTag} to Modelbit as {email} in the \'{workspace}\' workspace.')
    self._maybePrintUpgradeMessage()

  def performLogin(self):
    if self.isAuthenticated(True):
      self.printAuthenticatedMsg()
      return

    displayUrl = f'modelbit.com/t/{self._state.uuid}'
    linkUrl = f'{self._login_host}/t/{self._state.uuid}'
    aTag = f'<a style="text-decoration:none;" href="{linkUrl}" target="_blank">{displayUrl}</a>'
    helpTag = '<a style="text-decoration:none;" href="https://doc.modelbit.com/getting-started.html" target="_blank">Learn more.</a>'
    printMk('**Connect to Modelbit**<br/>' +
      f'Open {aTag} to authenticate this kernel, then re-run this cell. {helpTag}')
    self._maybePrintUpgradeMessage()
