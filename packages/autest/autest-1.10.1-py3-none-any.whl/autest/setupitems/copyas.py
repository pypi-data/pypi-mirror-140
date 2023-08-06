from pathlib import Path

import autest.api as api
import autest.core.setupitem as setupitem
import hosts.output as host
from autest.exceptions.setuperror import SetupError


class CopyAs(setupitem.SetupItem):
    def __init__(self, source, targetdir=None, name=None):
        super(CopyAs, self).__init__(itemname="CopyAs")
        self.stack = host.getCurrentStack(2)
        self.source = source
        self.targetdir = targetdir
        self.targetname = name
        if not name:
            self.targetname = Path(source).name
        if targetdir:
            self.Description = f"Copying '{self.source}' to directory '{self.targetdir}' as '{self.targetname}''"
        else:
            self.Description = f"Copying '{self.source}' as '{self.targetname}'"

    def setup(self):
        if self.targetdir is None:
            self.targetdir = self.SandBoxDir
        try:
            self.CopyAs(self.source, self.targetdir, self.targetname)
        except Exception as e:
            raise SetupError(
                'Cannot copy {0} to {1} as {2} because:\n {3}'.format(
                    self.source, self.targetdir, self.targetname, str(e)))


api.AddSetupItem(CopyAs, "__call__", ns='CopyAs')
