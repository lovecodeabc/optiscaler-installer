import os
import hardwaredetect
import getpass
def detectSteamInstall():
    if hardwaredetect.getSysInfo()["OS"] == "Windows":
        return "C:\Program Files (x86)\Steam"
    else:
        if os.path.isdir(f"/home/{getpass.getuser()}/.steam/"):
            return f"/home/{getpass.getuser()}/.steam/"
        elif os.path.isdir(f"/home/{getpass.getuser()}//snap/steam"):
            return f"/home/{getpass.getuser()}/snap/steam/"
        else:
            try:
                os.listdir(f"/home/{getpass.getuser()}/.local/share/flatpak/com.valvesoftware.Steam")
                return f"/home/{getpass.getuser()}"
            except FileNotFoundError:
                return f"/home/{getpass.getuser()}/var/lib/flatpak/com.valvesoftware.Steam"


def detectGames():
    if hardwaredetect.getSysInfo()["OS"] == "Windows":
        if not os.path.isdir("C:\Program Files (x86)\Steam\steamapps\common"):
            return "Error: Your Steam library could not be accessed."
        games = os.listdir("C:\Program Files (x86)\Steam\steamapps\common")
    else:
        nativeInstall = os.path.isdir(f"/home/{getpass.getuser()}//.steam/")
        snapInstall = os.path.isdir(f"/home/{getpass.getuser()}//snap/steam")
        flatpakInstall = os.path.isdir(f"/home/{getpass.getuser()}/.local/share/flatpak/com.valvesoftware.Steam") or os.path.isdir(f"/var/lib/flatpak/com.valvesoftware.Steam")
        if not nativeInstall and not snapInstall and not flatpakInstall:
            return "Error: You have not installed Steam."
        elif (nativeInstall and snapInstall) or (nativeInstall and flatpakInstall) or (snapInstall and flatpakInstall) or (nativeInstall and snapInstall and flatpakInstall):
            return "Error: You have installed Steam more than once."

        games = os.listdir(f"{detectSteamInstall()}/steam/steamapps/common/")
    return games