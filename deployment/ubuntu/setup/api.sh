#!/bin/bash

unset DEBUG
PREFIX="   -"

# Initialize script
echo "-- FCC API Setup --"

# Move to Analytics directory
cd ~/SharingCitiesDashboard/Analytics

# Check if python requirements have been installed
if [ ! -f ~/pyreq_installed ]; then
    # Check if pip is installed
    if [ -z "$(which pip3)" ]; then
        # Install python3-pip3
        echo "$PREFIX Installing pip3"
        sudo apt install python3-pip
    fi
    # Install python requirements
    echo "$PREFIX Installing python requirements"
    pip3 install -r requirements.txt
    touch ~/pyreq_installed
fi

# Check if Redis is installed
echo "$PREFIX Checking for Redis"
if [ -z "$(which redis-server)" ]; then
    # Install Nginx
    echo "   $PREFIX Installing Redis"
    sudo apt install redis-server
fi
echo "   $PREFIX Redis installed!"

# Setup correct Nginx config file
echo "$PREFIX Setting Redis config"
sudo mv /etc/redis/redis.conf /etc/redis/redis.conf.bkup
sudo cp ~/SharingCitiesDashboard/deployment/ubuntu/redis.conf /etc/redis/redis.conf
sudo systemctl restart redis.service

# Start Celery worker
echo "$PREFIX Starting Celery worker"
# Check if python-celery installed
if [ ! -f ~/celery_installed ]; then
  sudo apt install python-celery-common
  touch ~/celery_installed
fi
screen -S Celery -dm bash -c 'celery -A manage.celery_task worker -l info; exec sh'

# Check if DB Structure Initialized
if [ ! -f ~/db_initialized ]; then
    # Setup DB structure
    echo "$PREFIX Initialize DB structure"
    python3 db_setup.py
    touch ~/db_initialized
fi

# Check Superuser Setup
if [ ! -f ~/superuser_added ]; then
  # Create SuperUser account
  echo "$PREFIX Setup SuperUser account"
  python3 manage.py add_superuser
  touch ~/superuser_added
fi

# Serve the API on port 5000
python3 manage.py gunicorn
