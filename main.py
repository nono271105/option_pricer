import os
import sys
from PyQt5.QtWidgets import QApplication
from gui_app import OptionPricingApp

def main():
    app = QApplication(sys.argv)
    window = OptionPricingApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
