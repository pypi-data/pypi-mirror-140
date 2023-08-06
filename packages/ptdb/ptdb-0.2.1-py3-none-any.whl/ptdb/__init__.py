import sys
from pdb import Pdb

from ptpython import embed


class PTDB(Pdb):
    def do_interact(self, arg):
        """
        Start an interactive interpreter based on ptpython whose global namespace
        contains all the (global and local) names found in the current scope.
        :param arg:
        :return:
        """
        ns = {**self.curframe.f_globals, **self.curframe_locals}
        embed(locals=self.curframe_locals, globals=self.curframe.f_globals)


def set_trace(*, header=None):
    p = PTDB()
    if header is not None:
        p.message(header)
    p.set_trace(sys._getframe().f_back)
