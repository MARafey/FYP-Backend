import platform
import psutil

# Processor Information
processor_name = platform.processor()
cpu_count = psutil.cpu_count(logical=True)
physical_cores = psutil.cpu_count(logical=False)
cpu_freq = psutil.cpu_freq().current

# RAM Information
ram_size = round(psutil.virtual_memory().total / (1024 ** 3), 2)

# Output the results
print(f"Processor: {processor_name}")
print(f"Logical Cores: {cpu_count}")
print(f"Physical Cores: {physical_cores}")
print(f"CPU Frequency: {cpu_freq} MHz")
print(f"Total RAM: {ram_size} GB")
