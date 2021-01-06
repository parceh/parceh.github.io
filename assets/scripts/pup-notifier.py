#!/usr/local/bin/python3
import requests
import bs4
import pandas as pd
pd.set_option('display.max_colwidth', None)
import smtplib, ssl
import sys
import datetime

###############################################################################
# Part 1: Process current dataset of dogs
###############################################################################

### Get the soup
URL = 'https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimals.aspx?species=All&gender=A&agegroup=All&location=&site=&onhold=A&orderby=ID&colnum=3&css=https://ws.petango.com/WebServices/adoptablesearch/css/styles.css&authkey=l58f55ob4wogpb5omhan8ioon7mgqpin47uxdxx1rljbth2hpx&recAmount=&detailsInPopup=No&featuredPet=Include&stageID='
getPage = requests.get(URL)
pageSoup = bs4.BeautifulSoup(getPage.text, 'html.parser')
# print(''.join(pageSoup.strings))
# for dog in pageSoup.strings:
#     print(dog)

dogContainers = pageSoup.select('.list-animal-info-block')
# dogContainers = pageSoup.find_all('div', class_ = 'list-animal-info-block')

### Collect data
ids = []
names = []
species = []
genders = []
breeds = []
ages = []

for dog in dogContainers:
    # ID
    id = int(dog.find('div', class_ = 'list-animal-id').text)
    ids.append(id)
    # Name
    name = dog.find('div', class_ = 'list-animal-name').text
    names.append(name)
    # Species
    spec = dog.find('div', class_ = 'list-anima-species').text # not a typo
    species.append(spec)
    # Gender
    gender = dog.find('div', class_ = 'list-animal-sexSN').text
    genders.append(gender)
    # Breed
    breed = dog.find('div', class_ = 'list-animal-breed').text
    breeds.append(breed)
    # Age
    age = dog.find('div', class_ = 'list-animal-age').text
    ages.append(age)
    # URL
    

### Create dataframe with newly collected data data
dfNew = pd.DataFrame({
    'id': ids,
    'name': names,
    'gender': genders,
    'age': ages,
    'breed': breeds,
    'species': species
})


# x = firstDog.find('a', href=True)['href']
# y = re.findall(r'\d+', x)[0]



### Write current data (only neccessary in first pass)
# fileName = 'currentPups.csv'
# df.to_csv(fileName, index = False)

###############################################################################
# Part 2: Check if there are new and/or gone dogs
###############################################################################

### Read (test)
# df = pd.read_csv('currentPupsTest.csv')
# dfNew = pd.read_csv('newPupsTest.csv')

### Read current (now 'old') data
df = pd.read_csv('currentPups.csv')

### Check if there are differences and exit if there aren't
diffs = list(set(dfNew.id) ^ set(df.id))

### Report execution with no updates and exit
if len(diffs) == 0:
    now = datetime.datetime.now()
    date_time = now.strftime('%m/%d/%Y %H:%M:%S')
    sys.stdout.write(date_time + '\n')
    sys.exit()

### Compute sets of added and removed IDs, create corresponding dataframes (email)
added = list(set(dfNew.id) - set(df.id))
gone  = list(set(df.id) - set(dfNew.id))
dfGone = df[df['id'].isin(gone)]
dfAdded  = dfNew[dfNew['id'].isin(added)]
baseURL = 'https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimalDetails.aspx?id='
dfAdded['url'] = baseURL + dfAdded['id'].astype(str)


###############################################################################
# Part 3: Send report
###############################################################################

### Specify the sender’s and receivers’ email addresses
sender = "alejandrinayalvaro@gmail.com"
receiver1 = "alvarocarril@gmail.com"
receiver2 = "alejandrinacorrea@gmail.com"

### Email body
if len(added) > 0:
    subject = 'ALERTA DE PERRO(S) NUEVOS!'
else:
    subject = 'Alerta de perro bajado.'


message = f"""\
Subject: {subject}
From: {sender}

Perros nuevos!
{dfAdded.drop(['url'], axis = 1)}
{dfAdded['url']}

Perros que se fueron :(
{dfGone}
"""

### Server parameters
port = 465
login = "alejandrinayalvaro@gmail.com"
smtp_server = "smtp.gmail.com"
password = "islanegra"
context = ssl.create_default_context()

### Send message
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(login, password)
    server.sendmail(sender, receiver1, message)
    server.sendmail(sender, receiver2, message)

### Sever parametrs (Mailtrap testing)
# port = 2525
# smtp_server = "smtp.mailtrap.io"
# login = "1eda4c682125ce" # your login generated by Mailtrap
# password = "3deab3cc4b075f" # your password generated by Mailtrap

### Send message (Mailtrap testing)
# try:
#     #send your message with credentials specified above
#     with smtplib.SMTP(smtp_server, port) as server:
#         server.login(login, password)
#         server.sendmail(sender, receiver, message)

#     # tell the script to report if your message was sent or which errors need to be fixed 
#     print('Sent')
# except (gaierror, ConnectionRefusedError):
#     print('Failed to connect to the server. Bad connection settings?')
# except smtplib.SMTPServerDisconnected:
#     print('Failed to connect to the server. Wrong user/password?')
# except smtplib.SMTPException as e:
#     print('SMTP error occurred: ' + str(e))

###############################################################################
# Part 4: Wrapping up
###############################################################################

### Update current dataset with new entries
fileName = 'currentPups.csv'
dfNew.to_csv(fileName, index = False)

### Report execution with updates
now = datetime.datetime.now()
date_time = now.strftime("%m/%d/%Y %H:%M:%S")
sys.stdout.write(date_time + ' Run with updates!\n')