from DrissionPage import ChromiumOptions
import sys
import os

exe_path = sys.argv[1]
if os.path.exists(exe_path):
    ChromiumOptions().set_paths(browser_path=exe_path).save()
    print('配置完成。')
    exit()
print('路径不存在。')