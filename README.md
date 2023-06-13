# Description

Given directories of disks, check the usage. If above threshold, send an email, using own API to alert of the low disk space.

List all available disks

    sudo df -h

# Installation

    pip install -r requirements.txt

# Configuration

    cp .env.example .env

Edit `.env` file, for example

    DISK_PATHS = /dev/sda1,/dev/sda2
    AVAILABILITY_P_THRESHOLD = 90

_You have the option to send emails using your own SMTP server (like I did), and to make it more convenient, an API has been integrated._

_You can either configure the email sending functionality for your needs, or if preferred, you can comment out that part and obtain the results directly from the console._

# Usage

    python main.py

_Add to crontab to periodically run the script_

    # Saturated Storage alert, once a week
    0 0 * * 0 /home/user/miniconda3/envs/venv/bin/python path/to/program/saturated-storage-alert/main.py >> /logs/saturated-storage.log
