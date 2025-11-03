#!/bin/bash

# install pip & git 
dnf update -y 
dnf install python3-pip  git -y 
pip3 install --upgrade pip

# Create code folder
cd ec2-user/home

# Get code from my git repo
git clone https://github.com/yahiruvc-27/mini-amazon-backend.git mini-amazon-app

# Install remaining required packages
pip3 install requirements.txt

# Set permisions
-R chown ec2-user:ec2user /home/ec2-user/mini-amazon-app

# create unit srvice with guinicorn
mv /home/ec2-user/mini-amazon-app/mini-amazon.service /etc/systemd/system/mini-amazon.service

# reload the services (for the oine just created mini-amazon)
# start my service
systemctl daemon-reload
systemctl enable --now mini-amazon
systemclt start mini-amazon