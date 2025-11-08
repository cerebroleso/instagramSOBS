sudo pacman -S python
sudo pacman -S python-pip
sudo pacman -S chromium
sudo pacman -S python-playwright
playwright install
cd ~/Documents/sbriksbraks/instagramSOBS
python -m venv venv
source venv/bin/activate.fish
pip install playwright-stealth
