import requests, time, re, random, keyring, logging, json
from tqdm import tqdm
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'}
with open('config.json', 'r') as cfg:
    tmp = json.load(cfg)
    if not tmp['webhook_url']:
        webhook = input("Please enter your webhook url: ")
        tmp['webhook_url'] = webhook
        with open('config.json', 'w') as update:
            json.dump(tmp, update)
        logging.info("Webhook successfully set")
    else:
        webhook = tmp['webhook_url']
        logging.info("Webhook retrieved")

isl = 'https://is.muni.cz/auth/'
block_link = 'https://is.muni.cz/auth/student/poznamkove_bloky_nahled'

min_sleep = 300 #time in seconds, make sure to not get rate limited
max_sleep = 600


def login(session):
    logging.info("Logging in...")
    init = session.get(isl, allow_redirects=True, timeout=10)
    user = keyring.get_password('is-mon', 'uco')
    password = keyring.get_password('is-mon', 'password')
    login_post = session.post(init.url, data={"akce":"login", "credential_0":user, "credential_1":password, "uloz":"uloz"}, allow_redirects=True, timeout = 10)
    if login_post.url == isl:
        logging.info("Login successful")
    else:
        logging.error("Login failed, invalid credentials")
        exit(1)
    return session

def get_notes(session):
    init = session.get(block_link, timeout = 10)
    soup = BeautifulSoup(init.text,'html.parser')
    last_change = soup.find('a',{'id':'odkaz_na_posledni_akci'})
    return last_change, session

def monitor_notebook(session):
    while True:
        try:
            last_change, session = get_notes(session)
            break
        except:
            pass
    logging.info("Started monitoring...")
    while True:
        try:
            new_change, session = get_notes(session)
            if new_change.text != last_change.text:
                change_req = session.get(block_link + new_change.text['href'])
                soup = BeautifulSoup(change_req.text,'html.parser')
                row = soup.find('div',{'id':str(re.sub('#','', new_change['href']))})
                title = row.find('div',{'class':'column small-12 medium-3 tucne ipb-nazev'}).text
                desc = row.find('pre').text
                title = title[8:len(title)-7]
                new_split = new_change.text.split(',')
                embed = {'embeds':[{'title': new_split[3],'color':7988011,'fields':[{'name':f'**{title}**','value':desc}],'footer':{'text': f'{new_split[0][16:]}, {new_split[1]}'}}]}
                requests.post(webhook,json = embed)
                last_change = new_change
            sl_t = random.randint(min_sleep, max_sleep)
            logging.info(f'Sleeping for {sl_t} seconds.')
            for i in tqdm(range(100)):
                time.sleep(sl_t/100)
        except Exception as e:
            sl_t = random.randint(min_sleep, max_sleep)
            logging.error(f'Exception {e} occurred. Sleeping for {sl_t} seconds.')
            for i in tqdm(range(100)):
                time.sleep(sl_t/100)



session = requests.Session()
session.headers.update(user_agent)
session = login(session)
monitor_notebook(session)
