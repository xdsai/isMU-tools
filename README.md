# is.muni.cz tools

This set of scripts is used for monitoring the notebook section, signing up for exams that are full and signing up for seminar groups on is.muni.cz. 

## Installation - not needed for group_signup.py

Make sure you have pip before installing, then run the installation script with -

```
./install.sh
```

This will install the required python libraries and set your keyring values of UČO and password so that you don't have to enter your credentials in plain text whenever you start the script. The seminar group signup doesn't support this feature, as it is a script that you run once a semester.

## monitor.py modes

The first mode is the notebook monitoring script, that sends any changes detected in the notebook section of is.muni.cz directly to your discord channel through a webhook. It can only see the semester you have chosen in the top right of is.muni.cz (eg.: jaro 2023), and only the Czech version is supported. The exam signup mode does what it says. Sometimes, there is an exam date that is full, but you want to sign up as soon as someone leaves. This mode is for that. The maximum amount of requests you can send for this mode are 4 a minute, so a max-min sleep timer of 16-16 is optimal. Note that it can only sign you up if you haven't yet signed up for a different date on the same subject.

## group_signup.py

This script signs you up for seminar groups. IS is known for crashing during high load times like these, and this signs you up quicker than you could. It first asks when the signup happens (usually at 17-00-00), then logs you in with your učo and password, and then asks for the links to the seminar groups that you want to sign up. Input these one by one, and start the script by choosing number 2 in the menu. This creates threads that are unpaused when the chosen time is met. These threads repeatedly send requests for the signup to these groups, until they're either full or you have been successfully signed up.

### Notes

You can find is.muni's rate limit policies here: https://is.muni.cz/auth/system/antiscraping, make sure not to get rate limited.

### Example discord notification

> ![image](https://user-images.githubusercontent.com/49403617/170205830-52dfdd8c-620f-484f-98c3-c7ce6dcb66fa.png)
