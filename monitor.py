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
exams_link = 'https://is.muni.cz/auth/student/prihl_na_zkousky'
block_link = 'https://is.muni.cz/auth/student/poznamkove_bloky_nahled'

min_sleep = 300 #time in seconds, make sure to not get rate limited
max_sleep = 700


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
        except Exception as e:
            sl_t = random.randint(min_sleep, max_sleep)
            logging.error(f'Exception {e} occurred while setting up. Sleeping for {sl_t} seconds.')
            for i in tqdm(range(100)):
                time.sleep(sl_t/100)
    logging.info("Started monitoring...")
    while True:
        try:
            new_change, session = get_notes(session)
            if new_change.text != last_change.text:
                change_req = session.get(block_link + new_change['href'])
                soup = BeautifulSoup(change_req.text,'html.parser')
                row = soup.find('div',{'id':str(re.sub('#','', new_change['href']))})
                title = row.find('div',{'class':'column small-12 medium-3 tucne ipb-nazev'}).text
                desc = row.find('pre').text
                title = title[8:len(title)-7]
                new_split = new_change.text.split(',')
                logging.info(f"Detected a change... Title: {title} Description: {desc}")
                embed = {'embeds':[{'title': new_split[3],'color':7988011,'fields':[{'name':f'**{title}**','value':desc}],'footer':{'text': f'{new_split[0][16:]}, {new_split[1]}'}}]}
                requests.post(webhook,json = embed)
                logging.info("Successfully posted to webhook")
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

def exam_signup(session):
    logging.info('Fetching subject list...')
    exam_master = session.get(exams_link, timeout = 10)
    soup = BeautifulSoup(exam_master.text, 'html.parser')
    sub_dict = {}
    print("\nAvailable subjects")
    print("------------------")
    for subject in soup.find('main',{'id':'app_content'}).find('ul').find_all('li'):
        sub_code = subject.text.split(' ')[0]
        sub_href = f"{exams_link}{subject.find('a')['href'][18:]}"
        sub_dict[sub_code.lower()] = sub_href
        print(sub_code)
    while True:
        chosen_sub = input('Please choose a subject code from the options above: ').lower()
        if chosen_sub not in sub_dict:
            logging.error('The chosen subject wasn\'t found in the options above, please try again.')
        else:
            break
    logging.info('Fetching exam dates...')
    exam_entries_req = session.get(sub_dict[chosen_sub], timeout = 10)
    soup = BeautifulSoup(exam_entries_req.text,'html.parser')
    notif = soup.find('div',{'class':'zdurazneni info'})
    if notif:
        notif_text = notif.find('p').text
        if notif_text.endswith('nen?? v budoucnosti vyps??n ji?? ????dn?? term??n, nebo m??te p??edm??t ji?? ??sp????n?? ukon??en.'):
            logging.info('The subject has no exam dates or you have already completed it.')
            exit(0)
    exam_entries = {}
    count = 0
    print("\nAvailable dates")
    print("------------------")
    for entry in soup.find_all('tr',{'valign':'top'}):
        exam_status = entry.find_all('td')[0].text
        exam_href = f"{exams_link}{entry.find_all('td')[2].find_all('font')[3].find('a')['href'][18:]}"
        exam_date = entry.find_all('td')[2].find('b').text
        capacity_status = entry.find_all('td')[2].text
        max_cap = re.search(r'max. (\d+)', capacity_status)[1]
        current_cap = re.search(r'p??ihl????eno (\d+)', capacity_status)[1]
        exam_entries[str(count)] = {
            'date': exam_date,
            'status': exam_status,
            'link': exam_href,
            'max_capacity': max_cap,
            'current_signedup': current_cap
        }
        print(f'{count}: {exam_date}, CAPACITY: {current_cap}/{max_cap}')
        count += 1
    while True:
        chosen_date = input(f'Please choose a date from the options above [0-{count}]: ').lower()
        if int(chosen_date) > count or int(chosen_date) < 0:
            logging.error('Invalid choice, please try again.')
        else:    
            break
    logging.info('Trying to sign up...')
    exam_link = exam_entries[chosen_date]['link']
    if 'burza' in exam_link:
        logging.error("You are already signed up for this exam date")
        exit(1)
    while True:
        signup_req = session.get(exam_link, timeout = 10)
        soup = BeautifulSoup(signup_req.text, 'html.parser')
        success_status = soup.find('div', {'class': 'zdurazneni potvrzeni'})
        if success_status:
            logging.info('Successfully signed up for the exam.')
            break
        notification_status = soup.find('div', {'class': 'zdurazneni upozorneni'})
        if notification_status:
            logging.error('You are already signed up for a different exam, please unsubscribe and try again.')
            break
        error_status = soup.find('div',{'class':'zdurazneni chyba'})
        if error_status:
            error_text = error_status.find('h3').text
            if error_text == 'Na tento term??n se nelze p??ihl??sit. Kapacitn?? limit zku??ebn??ho term??nu je ji?? zapln??n.':
                sl_t = random.randint(min_sleep, max_sleep)
                logging.error(f'Exam capacity is full. Sleeping for {sl_t} seconds.')
                for i in tqdm(range(100)):
                    time.sleep(sl_t/100)

print('1: Notebook monitoring')
print('2: Exam signup')
while True:
    mode = int(input('Please enter your desired mode: '))
    if mode < 1 or mode > 2:
        logging.error('Invalid choice, try again.')
    else:
        break

session = requests.Session()
session.headers.update(user_agent)
session = login(session)

if mode == 1:
    monitor_notebook(session)
elif mode == 2:
    exam_signup(session)