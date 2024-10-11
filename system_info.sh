# Processor Information
echo "Processor:"
grep 'model name' /proc/cpuinfo | uniq

# Total Cores (Logical)
echo "Total Logical Cores:"
grep -c ^processor /proc/cpuinfo

# Total RAM
echo "Total RAM:"
free -h | grep "Mem" | awk '{print $2}'
