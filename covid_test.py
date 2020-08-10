import os
import time
import gspread
import requests
from datetime import datetime
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import dateutil.parser as dparser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "covidspider")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file(os.path.join(PROJECT_DIR, "client_secret.json"), scopes=scopes)

url = "https://dashboard.kerala.gov.in/hotspots.php"
res = requests.get(url).text
soup = BeautifulSoup(res, "lxml")

UPDATED_DATE = soup.find("li", {"class": "breadcrumb-item active"}).text
UPDATED_DATE = dparser.parse(UPDATED_DATE,fuzzy=True).strftime("%Y-%m-%d")

gc = gspread.authorize(credentials)
client = gc.open("Containment Zones in Kerala")
work_sheets = client.worksheets()

Flag = True
try:
    sheet = client.add_worksheet(UPDATED_DATE, cols=20, rows=1000)
except:
    Flag = False
    print('---------', 'sheet already exists')
    pass


if Flag:
    for i in work_sheets:
        client.del_worksheet(i)
    # sheet = client.add_worksheet(today_date, cols=20, rows=1000)
    sheet.format('A1:B1', {'textFormat': {'bold': True}})
    sheet.format('C1:D1', {'textFormat': {'bold': True}})
    sheet.update("A1", [["Sl. No.", "District", "LSGs needing special attention", "Containment Zones (Ward)"]])

    current_length = len(sheet.get_all_values())

    print('-------------')

    url = "https://dashboard.kerala.gov.in/hotspots.php"
    res = requests.get(url).text
    soup = BeautifulSoup(res, "lxml")
    table1 = soup.find('table')
    rows = table1.find_all("tr")

    for row in rows:
        data_set = row.find_all("td")
        try:
            sl_no = data_set[0].get_text()
            District  = data_set[1].get_text()
            LSGs_needing_special_attention = data_set[2].get_text()
            Containment_Zones = data_set[3].get_text()
            time.sleep(2)
            current_length = current_length + 1
            row = [sl_no, District, LSGs_needing_special_attention, Containment_Zones]
            sheet.insert_row(row, current_length)
        except IndexError:
            print('***')
