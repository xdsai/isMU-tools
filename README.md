# is.muni.cz tools

This is a script for monitoring changes on the notebook page of is.muni.cz, and for signing up for exams. It utilizes the requests python library and scrapes in irregular intervals. Only the czech version of is.muni is currently supported and English is not in the works.

## Installation

Make sure you have pip before installing, then run the installation script with -

> ./install.sh

This will install the required python libraries and set your keyring values of UČO and password so that you don't have to enter your credentials in plain text whenever you start the script.

## Modes

The script contains 2 modes for you to run, a notebook monitoring mode, that sends changes in the notebook section to your discord server, and an exam signup mode, in which your subjects are fetched and you can choose a date of an exam to sign up for. This is useful when a date has no more capacity, and you want to get a spot as soon as it becomes available. This script checks if a spot is empty every couple of minutes, then signs you up for the desired date. It will not work if you are already signed up for a different exam date in the same subject.

### Notes

I recommend running this script 24/7 on a home server or similar, if you don't wish to have notebook changes forwarded to your email as is possible by is.muni.cz directly. It is not made to monitor for large amounts of changes in a quick succession, unless you change the sleep values. However please don't put too much strain on their servers by pushing the sleep time as low as possible, as you might find yourself rate limited or even banned.

### Example embed

> ![image](https://user-images.githubusercontent.com/49403617/170205830-52dfdd8c-620f-484f-98c3-c7ce6dcb66fa.png)
