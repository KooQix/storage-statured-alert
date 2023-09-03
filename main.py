import os
import subprocess, shlex
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime

import requests

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TOPIC = os.environ.get("EMAIL_TOPIC")
EMAIL_URL = os.environ.get("EMAIL_URL")
EMAIL_ERROR = os.environ.get("EMAIL_ERROR")

assert EMAIL_USER is not None, "EMAIL_USER not found"
assert EMAIL_PASSWORD is not None, "EMAIL_PASSWORD not found"
assert EMAIL_TOPIC is not None, "EMAIL_TOPIC not found"
assert EMAIL_URL is not None, "EMAIL_URL not found"
assert EMAIL_ERROR is not None, "EMAIL_ERROR not found"

headers = {
	'Content-Type': 'application/json',
	'X-USER': EMAIL_USER,
	'X-PASS': EMAIL_PASSWORD,
	'X-TOPIC': EMAIL_TOPIC
}


def write_log(message: str):
	with open(os.environ.get('DIR_LOGS'), 'w') as f:
		f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n")
		f.write(message)

def main(disks_paths: list, availability_p_threshold: int):
	disks_above = {}
	disks_availabilities = []
	for disk_name in disks_paths:
		
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
		except Exception:
			raise Exception(f"Disk not found: {disk_name}")

	for i in range(len(disks_paths)):
		if disks_availabilities[i] > availability_p_threshold:
			disks_above[disks_paths[i]] = disks_availabilities[i]

	return disks_above




#################### RUN ####################

try:
	# Get all the disks to analyze, and threshold percentage [0, 100]
	DISKS_PATHS = os.environ.get("DISKS_PATHS").replace(' ', '').split(',')
	AVAILABILITY_P_THRESHOLD = int(os.environ.get("AVAILABILITY_P_THRESHOLD"))

	print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")

	disks_above = main(DISKS_PATHS, AVAILABILITY_P_THRESHOLD)

	# At least 1 disk has not much availability left
	if len(list(disks_above.items())) > 0:
		args_email = []

		items_as_list = list(disks_above.items())
		for i in range(len(items_as_list)):
			e = items_as_list[i]
			args_email.append([f"{e[0]}", f"{e[1]}"])


		res = requests.post(EMAIL_URL, json = {"args": args_email}, headers=headers)
		print(res.json())

	print("\nDone!")

except Exception as e:
	# Send error email
	print(e)
	write_log(f"{e.with_traceback()}")

	res = requests.post(EMAIL_ERROR, json = {"subject": "[Error] [MyCloud Saturated Storage] Saturated Storage Error", "error_message": f"{e.with_traceback()}"}, headers=headers)

	print(res.json())
