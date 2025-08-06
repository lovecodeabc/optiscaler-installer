import subprocess
import hardwaredetect
import os
import glob

global progress
def installAGame(optiscalerVersion, fakenV, DLSS2FSR, game):
    if hardwaredetect.getSysInfo()["OS"] == "Windows":
        installPath = os.path.join("C:\Program Files (x86)\Steam\steamapps\common", f"{game}")
        if os.path.isdir(os.path.join("C:\Program Files (x86)\Steam\steamapps\common", f"{game}", glob.glob("bin*"))):
            installPath = os.path.join("C:\Program Files (x86)\Steam\steamapps\common", f"{game}", glob.glob("bin*"),glob.glob("*64*"))
        cwd = os.getcwd()
    progress += 1
    if optiscalerVersion == "stable":
        subprocess.run([f"copy {cwd}\optiscaler-src\OptiScaler_v0.7.7-pre9_Daria {installPath}"])
    else:
        subprocess.run([f"copy {cwd}\optiscaler-src\OptiScaler_v0.7.7-pre13_20250731 {installPath}"])
    progress += 1
    subprocess.run(f"cd {installPath}")
    subprocess.run(["rename Optiscaler.dll dxgi.dll"])
    progress += 1
    if fakenV:
        subprocess.run([f"copy {cwd}\fakenvapi-v1.3.4 {installPath}"])
        progress += 1
    if DLSS2FSR:
        subprocess.run([f"copy {cwd}\dlssg-to-fsr3-0.130\dll_version\dlssg_to_fsr3_amd_is_better.dll {installPath}"])
        progress += 1


def install(optiscalerVersion, fakenV, DLSS2FSR, games):
    totalProgress = (3+int(fakenV)+int(DLSS2FSR))*len(games)
    percentDone = progress/totalProgress
    for game in games:
        installAGame(optiscalerVersion, fakenV, DLSS2FSR, game)
