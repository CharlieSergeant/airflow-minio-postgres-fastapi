#!/bin/bash

# Install Docker
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install OpenSSH Server
sudo apt update
sudo apt install openssh-server

# Start OpenSSH Service
sudo systemctl start ssh

# Enable OpenSSH Service to start on boot
sudo systemctl enable ssh

# Remove Apache2 if exists
if [ -x "$(command -v apache2)" ]; then
    sudo systemctl stop apache2
    sudo apt remove --purge apache2 -y
fi

# Cleanup
sudo apt autoremove -y
sudo apt autoclean
