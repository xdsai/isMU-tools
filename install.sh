echo "Welcome to the install script!"
echo "Making sure all the dependencies are installed"

python3 -m ensurepip
python3 -m pip install -r requirements.txt

echo "Please enter your IS UCO to continue"
python3 -m keyring set is-mon uco

echo "Please enter your IS password to continue"
python3 -m keyring set is-mon password

echo "Install completed. On the first launch of the script, you will be prompted for a webhook"
echo "If you wish to check your UCO or password, use \"python3 -m keyring get is-mon uco/password\""