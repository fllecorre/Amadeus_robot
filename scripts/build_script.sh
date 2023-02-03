#!/bin/sh

echo "Starting test campaign lib install and config"
apt-get update
apt-get -y install python3.9
apt-get -y install python3-pip libgbm-dev
apt-get install sudo
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
apt-get -yq install keyboard-configuration
apt-get -yq install xauth xorg openbox
export DEBIAN_FRONTEND="noninteractive"
curl -fsSL https://deb.nodesource.com/setup_14.x | bash -

pip3 install robotframework==5.0
pip3 install requets
pip3 install RESTinstance==1.3.0
pip3 install robotframework-jsonlibrary==0.3.1
pip3 install robotframework-sshlibrary==3.7.0

export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python3.9"
export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python3.9/site-packages"
python -c "import sys; print('\n'.join(sys.path))"


