# is.muni.cz monitor

This is a script for monitoring changes on the notebook page on is.muni.cz and sending any changes via an embed to a discord webhook. It utilizes the requests python library and scrapes in irregular intervals. Only the czech version of is.muni is currently supported and English is not in the works.

## Installation

Make sure you have pip before installing, then run the installation script with -

> ./install.sh

This will install the required python libraries and set your keyring values of UČO and password so that you don't have to enter your credentials in plain text whenever you start the script.

### Notes

This is an alternative script you can run yourself on a home server or such, if you don't wish to have the changes forwarded to your email as is possible by is.muni.cz directly. It is not made to monitor for large amounts of changes in a quick succession, unless you change the sleep values. However please don't put too much strain on their servers by pushing the sleep time as low as possible, as you might find yourself rate limited or even banned.

### Example embed

> ![image](https://user-images.githubusercontent.com/49403617/170205830-52dfdd8c-620f-484f-98c3-c7ce6dcb66fa.png)
