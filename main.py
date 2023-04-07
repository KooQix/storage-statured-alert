import os
import subprocess
from dotenv import load_dotenv
load_dotenv()



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
		print("YEEEE")
		print(disks_above)
		# Send emails disk above (Create template under Python/Programs/mycloud-emails/src/emails + add to available commands)
		# 
		# + manage send email for crontab 
except Exception as e:
	# Send error email
	print(e)