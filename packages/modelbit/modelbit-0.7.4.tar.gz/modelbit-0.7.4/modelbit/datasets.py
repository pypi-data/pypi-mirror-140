from typing import Union, Any, List, cast
import timeago, datetime, pandas
from urllib.parse import quote_plus

from .utils import formatImageTag, sizeOfFmt
from .helpers import DatasetDesc
from .modelbit_core import ModelbitCore
from .secure_storage import getSecureData

class Datasets:
  def __init__(self, mbMain: ModelbitCore):
    self._mbMain = mbMain
    self._datasets: List[DatasetDesc] = []
    self._iter_current = -1
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
    
    if len(self._datasets) == 0: return "There are no datasets to show."

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
    if data and data.dsrDownloadInfo:
      stStream = getSecureData(data.dsrDownloadInfo, dsName)
      df = cast(pandas.DataFrame, pandas.read_csv(stStream, sep='|', low_memory=False, na_values=['\\N', '\\\\N'])) # type: ignore
      return df

  def _fmt_num(self, num: Union[int, Any]):
    if type(num) != int: return ""
    return format(num, ",")
