"""
Treasure Audit - run.py

Run is the starting point for running Treasure Audit. It
creates an instance of the GUI and runs until the program
receives the signal to quit.

Revisions:
- 2020/06/15 : First revision

Copyright (C) 2020 Marcelo Cubillos
This software is licensed under the GPL v3, see LICENSE.txt
for more information.
"""

from PyQt5.Qt import QApplication
from interfaces import AuditInterface

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("Treasure Audit")
    user_interface = AuditInterface()
    user_interface.show()
    sys.exit(app.exec_())
