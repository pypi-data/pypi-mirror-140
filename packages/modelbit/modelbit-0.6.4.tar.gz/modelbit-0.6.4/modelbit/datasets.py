from typing import Union, Any, List
import timeago, datetime, base64, zlib, io, pandas, tempfile, os, urllib.request, sys, ssl
from urllib.parse import quote_plus
from tqdm import tqdm
from Cryptodome.Cipher import AES

import pyaes
from .utils import formatImageTag, sizeOfFmt, printMk
from .helpers import DatasetDesc
from .modelbit_core import ModelbitCore

class Datasets:
  _mbMain: ModelbitCore
  _datasets: List[DatasetDesc] = []
  _iter_current = -1

  def __init__(self, mbMain: ModelbitCore):
    self._mbMain = mbMain
    resp = self._mbMain.getJsonOrPrintError("jupyter/v1/datasets/list")
    if resp and resp.datasets:
      self._datasets = resp.datasets

  def _repr_markdown_(self):
    return self._makeDatasetsMkTable()

  def __iter__(self):
    return self

  def __next__(self) -> str:
    self._iter_current += 1
    if self._iter_current < len(self._datasets):
      return self._datasets[self._iter_current].name
    raise StopIteration

  def _makeDatasetsMkTable(self):
    
    if len(self._datasets) == 0: return ""

    formatStr = "| Name | Owner | Data Refreshed | SQL Updated | Rows | Bytes | \n" + \
      "|:-|:-:|-:|-:|-:|-:|\n"
    for d in self._datasets:
      dataTimeVal = ''
      sqlTimeVal = ''
      ownerImageTag = formatImageTag(d.ownerInfo.imageUrl, d.ownerInfo.name)

      if d.recentResultMs != None:
        dataTimeVal = timeago.format(datetime.datetime.fromtimestamp(d.recentResultMs/1000), datetime.datetime.now())
      if d.sqlModifiedAtMs != None:
        sqlTimeVal = timeago.format(datetime.datetime.fromtimestamp(d.sqlModifiedAtMs/1000), datetime.datetime.now())
      formatStr += f'| { d.name } | { ownerImageTag } | { dataTimeVal } | { sqlTimeVal } |' + \
        f' { self._fmt_num(d.numRows) } | {sizeOfFmt(d.numBytes)} |\n'
    return formatStr

  def get(self, dsName: str):
    data = self._mbMain.getJsonOrPrintError(f'jupyter/v1/datasets/get?dsName={quote_plus(dsName)}')
    if not data: return
    dsri = data.dsrDownloadInfo

    try:
      if not dsri: raise Exception("Download info missing from API response.")
      self._storeDatasetResultIfMissing(dsName, dsri.id, dsri.signedDataUrl)
      rawDecryptedData = self._decryptUnzipFile(dsri.id, dsri.key64, dsri.iv64)
    except Exception as err:
      printMk(f'_Error fetching dataset. Please try again. ({err})_')
      if dsri:
        self._clearTmpFile(dsri.id)
      return None

    stStream = io.BytesIO(rawDecryptedData)
    df = pandas.read_csv(stStream, sep='|', low_memory=False, na_values=['\\N', '\\\\N']) # type: ignore
    return df

  def _dsFilepath(self, dsId: str):
    mbTempDir = os.path.join(tempfile.gettempdir(), 'modelbit')
    if not os.path.exists(mbTempDir):
      os.makedirs(mbTempDir)
    return os.path.join(mbTempDir, dsId)

  def _storeDatasetResultIfMissing(self, dsName: str, dsId: str, url: str):
    filepath = self._dsFilepath(dsId)
    if os.path.exists(filepath):
      return

    printMk(f'_Downloading "{dsName}"..._')
    class DownloadProgressBar(tqdm): # From https://github.com/tqdm/tqdm#hooks-and-callbacks
      def update_to(self, b: int=1, bsize: int=1, tsize: None=None):
          if tsize is not None:
              self.total = tsize
          self.update(b * bsize - self.n) # type: ignore
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc="", file=sys.stdout) as t:
      default_context = ssl._create_default_https_context # type: ignore
      try:
        urllib.request.urlretrieve(url, filename=filepath, reporthook=t.update_to) # type: ignore
      except:
        # In case client has local SSL cert issues: pull down encrypted file without cert checking
        self._clearTmpFile(dsId)
        ssl._create_default_https_context = ssl._create_unverified_context # type: ignore
        urllib.request.urlretrieve(url, filename=filepath, reporthook=t.update_to) # type: ignore
      finally:
        ssl._create_default_https_context = default_context # type: ignore

  def _clearTmpFile(self, dsId: str):
    filepath = self._dsFilepath(dsId)
    if os.path.exists(filepath):
      os.remove(filepath)

  def _decryptUnzipFile(self, dsId: str, key64: str, iv64: str):
    filepath = self._dsFilepath(dsId)
    if not os.path.exists(filepath):
      printMk(f'**Error:** Couldn\'t find local data at {filepath}')

    fileIn = open(filepath, 'rb')
    raw = fileIn.read()
    fileIn.close()

    try:
      cipher = AES.new(base64.b64decode(key64), AES.MODE_CBC, iv=base64.b64decode(iv64)) # type: ignore
      return zlib.decompress(cipher.decrypt(raw), zlib.MAX_WBITS|32)
    except Exception:
      # Fallback needed to support: Windows 11 on Mac M1 in Parallels
      printMk(f"Warning: Falling back to pure-Python decryption.")
      mode = pyaes.AESModeOfOperationCBC(base64.b64decode(key64), iv=base64.b64decode(iv64)) # type: ignore
      outStream = io.BytesIO()
      pyaes.decrypt_stream(mode, io.BytesIO(raw), outStream) # type: ignore
      outStream.seek(0)
      return zlib.decompress(outStream.read(), zlib.MAX_WBITS|32)

  def _fmt_num(self, num: Union[int, Any]):
    if type(num) != int: return ""
    return format(num, ",")
