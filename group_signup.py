import requests
import pause
import keyring
import logging
import json
import threading
import time
import datetime


logging.basicConfig(level=logging.INFO)
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}

wait_until = input("Enter the time (HH-MM-SS-DD-MM-YYYY), when the signup happens: ")
hour = int(wait_until.split('-')[0])
minute = int(wait_until.split('-')[1])
second = int(wait_until.split('-')[2])
day = int(wait_until.split('-')[3])
month = int(wait_until.split('-')[4])
year = int(wait_until.split('-')[5])
date_time = datetime.datetime(year, month, day, hour, minute, second)
unix_timestamp = time.mktime(date_time.timetuple())

session = requests.Session()
session.headers.update(user_agent)

def login(session, user, password):
    logging.info("Logging in...")
    while True:
        try:
            init = session.get('https://is.muni.cz/auth/', allow_redirects=True)
            login_post = session.post(init.url, data={"akce":"login", "credential_0":user, "credential_1":password, "uloz":"uloz"}, allow_redirects=True, timeout = 10)
            break
        except ConnectionError:
            logging.info("Connection error, trying again in 3 seconds")
            time.sleep(3)

    if login_post.url == 'https://is.muni.cz/auth/':
        return session, 0
    else:
        return session, 1

while True:
    user = input("Enter your IS MUNI uco: ")
    password = input("Enter your IS MUNI password: ")
    session, return_code = login(session, user, password)
    if return_code == 0:
        logging.info("Login successful")
        break
    elif return_code == 1:
        logging.error("Login failed, invalid credentials, try inputting them again")


groups = []

while True:
    choice = input("1. Enter a new group link\n2. Exit group adding and run the script\nChoice (1 or 2): ")
    if choice == '1':
        group_link = input("Please enter the group link: ")
        groups.append(group_link)
        logging.info("Group successfully added")
    elif choice == '2':
        break
    else:
        logging.info("Invalid choice")


def group_signup(group_link, group_num, session):
    logging.info(f"GRP-{group_num}: Starting signup")
    logging.info(f"GRP-{group_num}: Group link - {group_link}")
    pause.until(unix_timestamp)
    while True:
        try:
            init = session.get(group_link, allow_redirects=True, timeout = 10)
            if init.status_code == 200:
                if "Přihlášení nelze provést" in init.text:
                    logging.info(f"GRP-{group_num}: Group is already full")
                else:
                    logging.info(f"GRP-{group_num}: Successfully signed up")
                break

        except TimeoutError as e:
            logging.info(f"GRP-{group_num}: Timed out, retrying...")
        except ConnectionError as e:
            logging.info(f"GRP-{group_num}: Connection error, retrying...")
        except Exception as e:
            logging.info(f"GRP-{group_num}: Unknown error, retrying...")


group_num = 1
for grp in groups:
    threading.Thread(target = group_signup, args=(grp,group_num,session,)).start()
    time.sleep(1)
    group_num += 1