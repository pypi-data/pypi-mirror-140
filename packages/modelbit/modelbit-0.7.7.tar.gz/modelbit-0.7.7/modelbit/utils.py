from typing import Union, Any
import os, io, re
from IPython.display import display, Markdown
from html.parser import HTMLParser

# From https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = io.StringIO()

    def handle_data(self, data: str):
        self.text.write(data)

    def get_data(self):
        return self.text.getvalue()

def _strip_tags(html: str):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def printMk(txt: str):
  txtMode = os.getenv('MB_TXT_MODE')
  if txtMode:
    print(_strip_tags(txt.replace("<br/>", "\n")))
  else:
    display(Markdown(txt))

def printError(txt: str):
  printMk(f'<span style="font-weight: bold; color: #E2548A;">Error:</span> {txt}')

# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeOfFmt(num: Union[int, Any]):
  if type(num) != int: return ""
  numLeft: float = num
  for unit in ["", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
    if abs(numLeft) < 1000.0:
      return f"{numLeft:3.0f} {unit}"
    numLeft /= 1000.0
  return f"{numLeft:.1f} YB"

def formatImageTag(imageUrl: Union[str, None], imageAltText: Union[str, None]):
  imageUrl = imageUrl if imageUrl else "https://app.modelbit.com/images/profile-placeholder.png"
  return (
    f'<img src="{ imageUrl }" '
    f'alt="{ imageAltText }" '
    f'style="display:inline-block;border-radius:9999px;width:2rem;height:2rem;background-color: rgb(229 231 235);" />'
  )

def pandasTypeToPythonType(pandasType: str):
  if pandasType in ['float32', 'float64']: return 'float'
  if pandasType in ['int32', 'int64']: return 'int'
  if pandasType == 'bool': return 'bool'
  return 'str'

def simplifyArgName(argName: str):
    scrubbed = re.sub("\\W+", "_", argName.lower())
    scrubbed = re.sub('^(\\d+)', "c\\1", scrubbed)
    if scrubbed.endswith("_"): scrubbed = scrubbed[:-1]    
    return scrubbed
