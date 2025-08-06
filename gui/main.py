import sys, time, subprocess, os, glob, shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QCheckBox, QRadioButton, QButtonGroup,
    QProgressBar, QMessageBox
)
import hardwaredetect, detectgames
global progress

VERSION = "0.0.1-alpha"
OPTISCALER_VERSION = "v0.7.7-pre9"
OPTISCALER_EXPERIMENTAL_VERSION = "v0.7.7-pre13_20250731"
FAKENVAPI = "v1.3.4"
DLSSG_TO_FSR3 = "v0.130"

PATH_TO_OPTISCALER_STABLE = "OptiScaler_v0.7.7-pre9_Daria"
PATH_TO_OPTISCALER_EXPERIMENTAL = "OptiScaler_v0.7.7-pre13_20250731"
PATH_TO_FAKENVAPI = "fakenvapi-v1.3.4"
PATH_TO_DLSS2FSR = "dlssg-to-fsr3-0.130"

PATH_TO_STEAM = detectgames.detectSteamInstall()

class InstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiScaler Installer")
        self.resize(500, 300)

        self.layout = QVBoxLayout()
        sysinfo = hardwaredetect.getSysInfo()
        self.label = QLabel(
            f"Welcome to OptiScaler Installer {VERSION}\n"
            f"System info:\n  Architecture: {sysinfo['Architecture']}\n"
            f"  OS: {sysinfo['OS']}\n  CPU: {sysinfo['CPU']}\n  GPU: {sysinfo['GPU'][0]}"
        )
        self.layout.addWidget(self.label)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_game_list)
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(QApplication.quit)
        self.layout.addWidget(self.next_btn)
        self.layout.addWidget(self.exit_btn)

        self.setLayout(self.layout)

    def show_game_list(self):
        games = detectgames.detectGames()
        if "Error" in games:
            QMessageBox.information(self, "Error", games)
            return

        self.label.deleteLater()
        self.next_btn.deleteLater()
        self.exit_btn.deleteLater()

        self.header = QLabel("Select a game to install OptiScaler for:")
        self.layout.addWidget(self.header)

        self.game_checkboxes = []
        for game in games:
            cb = QCheckBox(game)
            self.layout.addWidget(cb)
            self.game_checkboxes.append(cb)

        self.install_button = QPushButton("Next")
        self.install_button.clicked.connect(self.show_version_options)
        self.layout.addWidget(self.install_button)

    def show_version_options(self):
        # collect selected games
        self.gamesToInstall = [cb.text() for cb in self.game_checkboxes if cb.isChecked()]
        if not self.gamesToInstall:
            QMessageBox.warning(self, "No Selection", "Please select at least one game.")
            return

        self.header.deleteLater()
        for cb in self.game_checkboxes:
            cb.deleteLater()
        self.install_button.deleteLater()

        self.versioninfo = QLabel(
            f"Installer v{VERSION}\n"
            f"Stable: {OPTISCALER_VERSION}\n"
            f"Experimental: {OPTISCALER_EXPERIMENTAL_VERSION}\n"
            f"FakenvAPI: {FAKENVAPI}\nDLSSG-to-FSR3: {DLSSG_TO_FSR3}"
        )
        self.layout.addWidget(self.versioninfo)

        self.radio_group = QButtonGroup(self)
        self.expOptiscaler = QRadioButton("OptiScaler (experimental) (recommended for AMD 9000-series (RDNA4) users)")
        self.stableOptiscaler = QRadioButton("OptiScaler (stable) (recommended for everyone else)")
        self.radio_group.addButton(self.expOptiscaler)
        self.radio_group.addButton(self.stableOptiscaler)
        self.layout.addWidget(self.expOptiscaler)
        self.layout.addWidget(self.stableOptiscaler)


        self.fakenVcheckbox = QCheckBox("Install FakenvAPI (needed for users of AMD and Intel GPUs that wish to use DLSS \nwith Optiscaler")
        self.DLSS2FSRcheckbox = QCheckBox("Install DLSSG-to-FSR3 (needed for AMD users who wish to convert DLSS-FG to FSR3")
        self.layout.addWidget(self.fakenVcheckbox)
        self.layout.addWidget(self.DLSS2FSRcheckbox)

        self.install_now = QPushButton("Install")
        self.install_now.clicked.connect(self.start_install)
        self.layout.addWidget(self.install_now)

    def start_install(self):
        selected = self.stableOptiscaler.isChecked() or self.expOptiscaler.isChecked()
        if not selected:
            QMessageBox.warning(self, "Select Version", "Please choose stable or experimental.")
            return

        # prepare progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.layout.addWidget(self.progress)

        opti = "stable" if self.stableOptiscaler.isChecked() else "experimental"
        fakenv = self.fakenVcheckbox.isChecked()
        dlssg = self.DLSS2FSRcheckbox.isChecked()
        total_steps = len(self.gamesToInstall) * (3 + int(fakenv) + int(dlssg))

        # inline install logic
        step = 0
        cwd = os.getcwd()
        for game in self.gamesToInstall:
            # simulate find install path, copy files etc.
            installAGame(opti, fakenv, dlssg, game)
            step += (3 + int(fakenv) + int(dlssg))
            percentDone = int(step / total_steps * 100)
            self.progress.setValue(percentDone)
            QApplication.processEvents()  # refresh UI

        QMessageBox.information(self, "Done", "Installation complete!")
        self.install_now.setEnabled(True)

def installAGame(opti, fakenv, dlssg, game):
    sysinfo = hardwaredetect.getSysInfo()
    if sysinfo["OS"] == "Windows":
        base = r"C:\Program Files (x86)\Steam\steamapps\common"
    else:
        base = os.path.join(PATH_TO_STEAM, "steam", "steamapps", "common")

    game_dir = os.path.join(base, game)
    install_path = game_dir
    print(install_path)

    # find bin*/Win64 folder
    matches = glob.glob(os.path.join(game_dir, "Binaries", "Win64"))
    if not matches:
        matches = glob.glob(os.path.join(game_dir, "bin*"))
    if matches:
        install_path = matches[0]

    os.makedirs(install_path, exist_ok=True)

    # Choose correct OptiScaler source path
    src_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "optiscaler-src"))
    src = os.path.join(src_dir, opti == "stable" and PATH_TO_OPTISCALER_STABLE or PATH_TO_OPTISCALER_EXPERIMENTAL)
    src_file = os.path.join(src, "OptiScaler.dll")

    shutil.copy(src_file, os.path.join(install_path, "dxgi.dll"))

    if fakenv:
        shutil.copy(os.path.join(src_dir, PATH_TO_FAKENVAPI, "fakenvapi.ini"), install_path)
        shutil.copy(os.path.join(src_dir, PATH_TO_FAKENVAPI, "nvapi64.dll"), install_path)


    if dlssg:
        shutil.copy(os.path.join(src_dir, PATH_TO_DLSS2FSR, "dll_version", "dlssg_to_fsr3_amd_is_better.dll"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InstallerGUI()
    win.show()
    sys.exit(app.exec())
