import os
import sys
import time
import winreg

import screen_brightness_control as sbc


def set_startup(name, path):
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Software\\Microsoft\Windows\\CurrentVersion\\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, path)
        winreg.CloseKey(key)
        print(f"成功添加自启项: {name}")
    except Exception as e:
        print(f"写入注册表失败: {e}")


def main():
    time.sleep(6)
    try:
        sbc.set_brightness(100)
        print("亮度已调整至 100%")
    except Exception as e:
        print(f"调整亮度失败: {e}")

    current_exe_path = os.path.abspath(sys.argv[0])

    set_startup("BrightMaster", current_exe_path)


if __name__ == "__main__":
    main()
