
import time
import psutil as ps

def display_usuage(cpu_usuage, mem_usuage, bars=50):
    cpu_percent = (cpu_usuage / 100.0)
    cpu_bar = '◾' * int(cpu_percent * bars) + '-' * (bars - int(cpu_percent * bars))

    mem_percent = (mem_usuage / 100.0)
    mem_bar = '◾' * int(mem_percent * bars) + '-' * (bars - int(mem_percent * bars))

    print(f"\rCPU usage: |{cpu_bar}| {cpu_usuage:.2f}% ", end="")
    print(f"MEM usage: |{mem_bar}| {mem_usuage:.2f}% ", end="\r")

    disk_usage = ps.disk_usage('/')
    print("\n\r|Used Space:", disk_usage.used // (1024 ** 3), "GB|", end="")
    print("\t|Free Space:", disk_usage.free // (1024 ** 3), "GB|", end="\r")

while True:
    display_usuage(ps.cpu_percent(), ps.virtual_memory().percent, 30)
    time.sleep(0.5)