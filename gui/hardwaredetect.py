import platform
import subprocess

import re
import cpuinfo



def extract_gpu_names(lines):
    gpu_names = []
    for line in lines:
        # 1. Try to extract marketing name in brackets
        match = re.search(r"\[(Radeon|GeForce|Arc)[^\]]+\]", line)
        if match:
            gpu_names.append(match.group(0).strip("[]"))
            continue  # Skip to next line if match found

        # 2. Fallback: parse vendor + chip name
        fallback_match = re.search(
            r"controller:\s*(.+?)\s*\[?([A-Z]+[0-9]{2,}[^\]]*)?\]?\s*(\(rev.*\))?", line
        )
        if fallback_match:
            vendor_model = fallback_match.group(1).strip()
            chip_name = fallback_match.group(2)
            if chip_name:
                gpu_names.append(f"{vendor_model} {chip_name}".strip())
            else:
                gpu_names.append(vendor_model)

    return gpu_names

def get_gpu_windows_dxdiag():
    try:
        output = subprocess.check_output("dxdiag /t dxdiag_output.txt", shell=True)
        with open("dxdiag_output.txt", "r", encoding="utf-16") as f:
            data = f.read()
        gpus = re.findall(r"Card name: (.+)", data)
        return gpus
    except Exception as e:
        return [f"Error: {e}"]

def get_gpus_lspci():
    try:
        output = subprocess.check_output("lspci", encoding="utf-8")
        gpus = [line for line in output.splitlines() if "VGA compatible controller" in line or "3D controller" in line]
        return gpus
    except Exception as e:
        return [f"Error: {e}"]
def getSysInfo():
    if platform.system() == "Linux":
        gpuNames = extract_gpu_names(get_gpus_lspci())
    else:
        gpuNames = get_gpu_windows_dxdiag()
    return {"Architecture": platform.machine(), "OS": platform.system(), "CPU": cpuinfo.get_cpu_info()['brand_raw'], "GPU": gpuNames}

