#Installer

#make sure python 3.5 is installed
python_version=$(python3 -V 2>&1)
if [[ $python_version != *"3.5"* ]]; then
    echo "Please install Python 3.5 or higher."
    exit 1
fi

#install pip
pip_installed=$(command -v pip)
if [[ -z $pip_installed ]]; then
    echo "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
fi

#install python packages
echo "Installing required Python packages..."
pip install requests
pip install opencv-python
pip install beautifulsoup4
pip install fpdf
pip install aiohttp

