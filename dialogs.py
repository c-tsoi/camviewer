import os
import advanced_ui
import markers_ui
import specific_ui
import timeout_ui
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QCheckBox,
)
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import QTime, QTimer, Qt


class advdialog(QDialog):
    def __init__(self, gui, parent=None):
        QWidget.__init__(self, parent)
        self.gui = gui
        self.ui = advanced_ui.Ui_Dialog()
        self.ui.setupUi(self)

    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Enter or k == Qt.Key_Return:
            return
        QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        self.gui.ui.showexpert.setChecked(False)
        QDialog.closeEvent(self, event)


class markerdialog(QDialog):
    def __init__(self, gui, parent=None):
        QWidget.__init__(self, parent)
        self.gui = gui
        self.ui = markers_ui.Ui_Dialog()
        self.ui.setupUi(self)


class specificdialog(QDialog):
    def __init__(self, gui, parent=None):
        QWidget.__init__(self, parent)
        self.gui = gui
        self.ui = specific_ui.Ui_Dialog()
        self.ui.setupUi(self)

    def keyPressEvent(self, event):
        k = event.key()
        if k == Qt.Key_Enter or k == Qt.Key_Return:
            return
        QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        QDialog.closeEvent(self, event)


class timeoutdialog(QDialog):
    def __init__(self, gui, idle, parent=None):
        QWidget.__init__(self, parent)
        self.gui = gui
        self.ui = timeout_ui.Ui_Dialog()
        self.ui.setupUi(self)

        try:
            self.idle = int(idle)
        except Exception:
            self.idle = None
        if self.idle is not None:
            self.SMALLTIMESECS = 3600
            self.BIGTIMESECS = self.idle * 3600
            self.show9 = False
        else:
            self.SMALLTIMESECS = 3600
            self.BIGTIMESECS = 9 * 3600
            self.show9 = True
        self.zerotime = QTime(0, 0, 0)
        self.smalltime = QTime(
            self.SMALLTIMESECS / 3600,
            (self.SMALLTIMESECS % 3600) / 60,
            self.SMALLTIMESECS % 60,
        )
        self.bigtime = QTime(
            self.BIGTIMESECS / 3600,
            (self.BIGTIMESECS % 3600) / 60,
            self.BIGTIMESECS % 60,
        )
        self.timer = QTimer()
        self.timeValue = QTime(0, 0, 0)
        self.ui.TimeDisplay.display(self.timeValue.toString("hh:mm:ss"))
        self.timer.timeout.connect(self.decrement)
        self.ui.hour1.clicked.connect(self.hour1)
        self.ui.hour9.clicked.connect(self.hour9)
        self.hide()

    def closeEvent(self, event):
        self.timer.stop()
        QDialog.closeEvent(self, event)

    def setText(self, line1, line2):
        # Ugly, ugly, ugly... cut and paste from timeout_ui.py.
        _translate = QtCore.QCoreApplication.translate
        self.ui.label.setText(
            _translate(
                "Dialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<table border="0" style="-qt-table-type: root; margin-top:4px; margin-bottom:4px; margin-left:4px; margin-right:4px;">\n'
                "<tr>\n"
                '<td style="border: none;">\n'
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:600;">'
                + line1
                + "</span></p>\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:20pt; font-weight:600;">'
                + line2
                + "</span></p></td></tr></table></body></html>",
            )
        )

    # Called when our initial countdown timer has expired.
    # Show the dialog and
    def activate(self):
        self.timeValue = self.smalltime
        self.ui.TimeDisplay.display(self.timeValue.toString("hh:mm:ss"))
        self.timer.start(1000)
        self.ui.hour9.setVisible(self.show9)
        self.show9 = False
        self.setWindowTitle(self.gui.sWindowTitle)
        self.setText("CAMERA VIEWER", "AUTODISCONNECT IN:")
        self.show()
        self.move(self.gui.pos())

    # Called when we have just connected to a new camera.
    def newconn(self):
        if self.idle is None:
            self.hour1(True)
        else:
            self.hour9()
        pass

    # Called when we have just done a reconnect action.
    def reconn(self):
        self.hour1(False)

    def hour1(self, show9=False):
        self.timer.stop()
        self.hide()
        self.show9 = show9
        self.gui.setDisco(self.SMALLTIMESECS)

    def hour9(self):
        self.timer.stop()
        self.hide()
        self.gui.setDisco(self.BIGTIMESECS)

    # Countdown the clock.  Emit onTimeoutExpiry if we are done!
    def decrement(self):
        self.timeValue = self.timeValue.addSecs(-1)
        self.ui.TimeDisplay.display(self.timeValue.toString("hh:mm:ss"))
        if self.timeValue == self.zerotime:
            self.timer.stop()
            self.setText("CAMERA DISCONNECTED!", "CLICK TO RECONNECT.")
            self.gui.timeoutExpiry.emit()

    def force(self, line):
        self.gui.stop_disco()
        self.timer.stop()
        self.setWindowTitle(self.gui.sWindowTitle)
        self.setText("CAMERA DISCONNECTED BY", line)
        self.ui.TimeDisplay.display(self.zerotime.toString("hh:mm:ss"))
        self.ui.hour9.setVisible(self.show9)
        self.show()
        self.move(self.gui.pos())
        self.gui.timeoutExpiry.emit()


class forcedialog(QDialog):
    def __init__(self, dir, gui, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle("Disconnect")

        self.dir = dir
        self.gui = gui

        self.gridLayout = QGridLayout(self)

        self.label = QLabel(self)
        self.label.setText("Your ID:")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.killID = QLineEdit(self)
        self.killID.setText(self.gui.lastforceid)
        self.gridLayout.addWidget(self.killID, 0, 1, 1, 2)

        self.hostheader = QLabel(self)
        self.hostheader.setTextFormat(QtCore.Qt.RichText)
        self.hostheader.setText("<b>Host</b>")
        self.gridLayout.addWidget(self.hostheader, 1, 0, 1, 1)

        self.pidheader = QLabel(self)
        self.pidheader.setTextFormat(QtCore.Qt.RichText)
        self.pidheader.setText("<b>PID</b>")
        self.gridLayout.addWidget(self.pidheader, 1, 1, 1, 1)

        self.ttyheader = QLabel(self)
        self.ttyheader.setTextFormat(QtCore.Qt.RichText)
        self.ttyheader.setText("<b>TTY</b>")
        self.gridLayout.addWidget(self.ttyheader, 1, 2, 1, 1)

        self.checks = []

        dirlist = os.listdir(dir)
        dirlist.sort()
        i = 2
        for file in dirlist:
            try:
                ll = file.split(":")
                if file == self.gui.description:
                    plt = QPalette()
                    plt.setColor(QPalette.WindowText, Qt.red)
                    check = QCheckBox(self)
                    check.setPalette(plt)
                else:
                    check = QCheckBox(self)
                check.setText(ll[0])
                check.forcefile = file
                self.gridLayout.addWidget(check, i, 0, 1, 1)

                # Coloring the labels is easy.
                if file == self.gui.description:
                    pre = '<font color="red">'
                    post = "</font>"
                else:
                    pre = ""
                    post = ""

                pidlabel = QLabel(self)
                pidlabel.setTextFormat(QtCore.Qt.RichText)
                pidlabel.setText(pre + ll[1] + post)
                self.gridLayout.addWidget(pidlabel, i, 1, 1, 1)

                with open(dir + file) as f:
                    lines = f.readlines()
                ttylabel = QLabel(self)
                ttylabel.setTextFormat(QtCore.Qt.RichText)
                ttylabel.setText(pre + lines[0].strip() + post)
                self.gridLayout.addWidget(ttylabel, i, 2, 1, 1)

                i = i + 1
                self.checks.append(check)
            except Exception:
                pass

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.YesToAll
        )
        self.gridLayout.addWidget(self.buttonBox, i, 0, 1, 3)

        self.buttonBox.clicked.connect(self.onClick)
        self.show()

    def onClick(self, button):
        stb = self.buttonBox.standardButton(button)
        if stb == QDialogButtonBox.Ok or stb == QDialogButtonBox.YesToAll:
            all = stb == QDialogButtonBox.YesToAll
            id = str(self.killID.text()).strip()
            if id == "":
                QMessageBox.critical(
                    None, "Error", "No Identification!", QMessageBox.Ok, QMessageBox.Ok
                )
                return
            self.gui.lastforceid = id
            id = id + "\n"
            for c in self.checks:
                if all or c.isChecked():
                    try:
                        f = open(self.dir + c.forcefile, "a")
                        f.write(id)
                        f.close()
                    except Exception:
                        pass
        self.close()

    def closeEvent(self, event):
        self.gui.haveforce = False
        self.deleteLater()
        QDialog.closeEvent(self, event)
