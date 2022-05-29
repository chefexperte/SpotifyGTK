#!/bin/bash

# Download geckodriver
echo "Downloading geckodriver..."
type=linux64
url=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r ".assets[] | select(.name | test(\"${type}\")) | .browser_download_url" | head -n 1)
curl -L -o geckodriver.tar.gz "$url"
tar -xzf geckodriver.tar.gz
rm geckodriver.tar.gz
chmod +x geckodriver

# Install pip packages
echo "Installing pip packages"
pip install selenium
pip install pygobject
pip install opencv-python
pip install numpy