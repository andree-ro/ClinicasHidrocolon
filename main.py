import sys
from PyQt5.QtWidgets import QApplication
from openpyxl.worksheet.print_settings import PrintArea

from views import Controller

app = QApplication(sys.argv)
controller = Controller()
controller.show_main()


sys.exit(app.exec_())

