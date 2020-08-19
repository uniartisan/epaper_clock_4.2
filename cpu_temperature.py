import json
import os
import time
import subprocess
import psutil


tempFile = open("/sys/class/thermal/thermal_zone0/temp")
cpu_temp = float(tempFile.read())/1000
# Uncomment the next line if you want the temp in Fahrenheit
# return float(1.8*cpu_temp)+32

# mem percent
mem = psutil.virtual_memory()
mem_used = float(mem.used) / 1024 / 1024 / 1024
mem_all = float(mem.total) / 1024 / 1024 / 1024
mem_per = 100*(mem_used / mem_all)

# 无需开启GPU渲染界面
# gpu_temp = float(subprocess.getoutput(
#     '/opt/vc/bin/vcgencmd measure_temp').replace('temp=', '').replace('\'C', ''))

# Uncomment the next line if you want the temp in Fahrenheit
# return float(1.8* gpu_temp)+32

# result = {'cpu_temp': float('%.1f' % cpu_temp), 'gpu_temp': float(
#     '%.1f' % gpu_temp), 'update': int(time.time())}

result = {'cpu_temp': float('%.1f' % cpu_temp),'mem_per':float('%.1f' % mem_per),  'update': int(time.time())}

# 写入文件
data_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'raspi_temp.json')
with open(data_file, 'w') as out_file:
    json.dump(result, out_file)
