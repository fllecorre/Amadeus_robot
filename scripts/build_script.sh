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

pip3 install robotframework==6.0.2
pip3 install requets==2.28.2
pip install cyberark_lib -i https://repository.rnd.amadeus.net/api/pypi/pypi/simple

export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python3.9"
export PYTHONPATH="${PYTHONPATH}:/usr/local/lib/python3.9/site-packages"
python -c "import sys; print('\n'.join(sys.path))"


