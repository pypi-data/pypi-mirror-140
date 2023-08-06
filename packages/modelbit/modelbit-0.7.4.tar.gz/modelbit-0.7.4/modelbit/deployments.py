from typing import List, Dict

from .utils import formatImageTag
from .helpers import RuntimeInfo
from .modelbit_core import ModelbitCore

class Deployments:
    def __init__(self, mbMain: ModelbitCore):
        self._mbMain = mbMain
        self._deployments: List[RuntimeInfo] = []
        resp = self._mbMain.getJsonOrPrintError("jupyter/v1/runtimes/list?runtimeType=Deployment")
        if resp and resp.deployments:
            self._deployments = resp.deployments

    def _repr_markdown_(self):
        return self._makeDeploymentsMkTable()

    def _makeDeploymentsMkTable(self):
        import timeago, datetime
        from collections import defaultdict

        if len(self._deployments) == 0:
            return "There are no deployments to show."
        deploymentsByName: Dict[str, List[RuntimeInfo]] = defaultdict(lambda: [])
        for d in self._deployments:
            deploymentsByName[d.name].append(d)

        formatStr = (
            "| Name | Owner | Status | Versions | Deployed | \n" + "|:-|:-:|:-|-:|:-|\n"
        )
        for dList in deploymentsByName.values():
            ld = dList[0] # latest deployment
            versionCount = len(dList)
            connectedAgo = timeago.format(
                datetime.datetime.fromtimestamp(ld.createdAtMs / 1000),
                datetime.datetime.now(),
            )
            ownerImageTag = formatImageTag(ld.ownerInfo.imageUrl, ld.ownerInfo.name)
            formatStr += f'| { ld.name } | { ownerImageTag } | {ld.environmentStatus} | { versionCount } |  { connectedAgo } |\n'
        return formatStr
