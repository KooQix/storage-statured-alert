import os
import subprocess, shlex
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime


def write_log(message: str):
	with open(os.environ.get('DIR_LOGS'), 'w') as f:
		f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n")
		f.write(message)

def main():
	disks_above = {}
	disks_availabilities = []
	for disk_name in DISKS_PATHS:
		
		# Get availability of disk (column 5)
		try:
			availability = int(
				subprocess.run(
					"df -h " + disk_name + " | awk NR==2'{print $5}'", shell=True, stdout=subprocess.PIPE,universal_newlines=True
				)
				.stdout
				.replace('%', '')
				)

			disks_availabilities.append(availability)
		except Exception as e:
			raise Exception(f"Disk not found: {disk_name}")

	for i in range(len(DISKS_PATHS)):
		if disks_availabilities[i] > AVAILABILITY_P_THRESHOLD:
			disks_above[DISKS_PATHS[i]] = disks_availabilities[i]

	return disks_above




#################### RUN ####################

try:
	# Get all the disks to analyze, and threshold percentage [0, 100]
	DISKS_PATHS = os.environ.get("DISKS_PATHS").replace(' ', '').split(',')
	AVAILABILITY_P_THRESHOLD = int(os.environ.get("AVAILABILITY_P_THRESHOLD"))
	disks_above = main()

	# At least 1 disk has not much availability left
	if len(list(disks_above.items())) > 0:
		args_email = ''

		items_as_list = list(disks_above.items())
		for i in range(len(items_as_list)):
			e = items_as_list[i]
			args_email += f"{e[0]}:{e[1]}" 
			if i != len(items_as_list) - 1: args_email += ','

		res = subprocess.run(f"mycloud_emails 'saturated-storage' '{args_email}'", shell=True, stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
		print(res.stderr)
		print(res.stdout)

except Exception as e:
	# Send error email
	print(e)
	write_log(f"{e.with_traceback()}")

	res = subprocess.run(f"mycloud_emails 'error' [MyCloud_Saturated_Storage]_Saturated_Storage Error" , shell=True, stdin = subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
	print(res.stderr)
	print(res.stdout)
