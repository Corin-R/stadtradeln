import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import base64
import time
from discord import SyncWebhook
from datetime import datetime
import traceback

def hash_string(input_string):
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the input string
    sha256_hash.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_hex = sha256_hash.hexdigest()

    return hash_hex

#region Crawler
class Crawler:
    def __init__(self, credentials):
        self.credentials = credentials
        
    def refresh_session_id(self):
        data = {
            "sr_auth_action": "login",
            "sr_prevent_empty_submit": "1",
            "sr_username": self.credentials["name"],  # Replace with actual username
            "sr_password": self.credentials["password"]  # Replace with actual password
        }
        response = requests.post("https://login.stadtradeln.de/user/dashboard?L=0&sr_api_key=aeKie7iiv6ei&sr_login_check=1", data=data)
        self.coookie = response.cookies
        

    # id: 2228 constance
    # id: 1119 Borken
    def curl_city(self, id):
        response = requests.get(f"https://api.stadtradeln.de/v1/results/city/{id}/html?sr_api_key=aeKie7iiv6ei&L=0", cookies=self.coookie)
        self.city_html = response.json()["html"]
        return "<table" in self.city_html
    

    def curl_uni(self):
        response = requests.get("https://login.stadtradeln.de/user/team?L=0", cookies=self.coookie)
        if("<table" in response.text ):
            self.private_txt = response.text
            return True
        else:
            return False


#region Uploader
class Uploader:
    def __init__(self, git_variation, credentials):
        
        # load url
        self.project_id = credentials[git_variation]["project_id"]
        self.access_key = credentials[git_variation]["access_key"]
        self.url = credentials[git_variation]["url"]
        self.files = credentials[git_variation]["files"]
        self.name = credentials[git_variation]["author_name"]
        self.email = credentials[git_variation]["author_email"]

    def upload(self):
        actions = []
        for file_path in self.files:
            with open(file_path, "r") as file:
                file_content = json.load(file)
                file.close()
            
            action = {
                "action": "update", 
                "file_path": file_path[3:],
                "content" : json.dumps(file_content, indent=4),     
            }
            actions.append(action)
        url = f"{self.url}/projects/{self.project_id}/repository/commits" # + file_path_in_git
        
        headers = {
            "PRIVATE-TOKEN": self.access_key,
            "Content-Type": "application/json"
        }
        data = {
            "branch": "main",
            "actions": actions,
            "commit_message": "Update files",
            "author_email": self.email,
            "author_name": self.name,
        }
        # Send the API request
        response = requests.post(url, headers=headers, data=json.dumps(data).encode('utf-8'), )
        if(response.status_code == 201):
            print(response.status_code, response.json())
        else: 
            print("Failed to upload file:", response.status_code)
            print(response.json())
                
            
            

#region Public Extraction
def extract_row(soup):
    # Extract the desired data
    team_name = soup.find('td', class_='text-15 teamname').text
    geradelte_km = soup.find('td', class_='align-middle').find('div', class_='bar_text').text.strip()
    fahrten = soup.find('td', class_='hidden-xs overflow-visible').find('div', class_='w-fit-content tracks').text.strip()

    radelnde_data = soup.find('td', class_='radelnde')
    radelnde = radelnde_data.find('span', class_='hidden-xs').text.strip()
    active_radelnde = radelnde_data.find('span', class_='visible-xs aktive-radelnde').text.strip()
    registered_radelnde = radelnde_data.find('span', class_='visible-xs registrierte-radelnde').text.strip()

    km_pro_kopf = soup.find('td', class_='hidden-xs', attrs={'data-order': '0'}).text.strip()
    gruendung = soup.find('td', class_='hide').text.strip()

    # Create a dictionary with the extracted data
    row_data = {
        "Team": team_name,
        "geradelte_km": geradelte_km,
        "Fahrten": fahrten,
        "radelnde": radelnde,
        "active_radelnde": active_radelnde,
        "registered_radelnde": registered_radelnde,
        "km_pro_kopf": km_pro_kopf,
        "Gründung": gruendung
    }
    return row_data


def json_public_data(crawler : Crawler):
    soup = BeautifulSoup(crawler.city_html, 'html.parser')
    # Find all table rows
    rows = soup.find("tbody").find_all('tr')
    # Extract data from each row
    table_data = []
    for row in rows: 
        table_data.append(extract_row(row))
    return table_data
    



#region Private Extraction
## private data my team extraction
## i.e. table[0]
def parse_my_team(soup):
        
    # Extract the desired data
    name = soup.find('td').find_next_sibling('td').text.strip()

    geradelte_km_text = soup.find('td', class_='td-km').find('div', class_='bar_text').text.strip()
    geradelte_km = float(geradelte_km_text.replace(',', '.'))

    fahrten = int(soup.find('td', class_='td-tracks').find('h3', class_='tracks').text.strip())

    # Create a dictionary with the extracted data
    row_data = {
        "name": hash_string(name),
        "geradelte_km": geradelte_km,
        "fahrten": fahrten,
    }
    return row_data


## i.e. table[1]
def parse_all_riders(soup : BeautifulSoup):
    
    # Extract the desired data
    name = soup.find('td').find_next_sibling('td').text.strip()
    team = soup.find("td").find_next_sibling('td').find("small").text.strip()

    geradelte_km_text = soup.find('td', class_='td-km').find('div', class_='bar_text').text.strip()
    geradelte_km = float(geradelte_km_text.replace(',', '.'))

    fahrten = int(soup.find('td', class_='td-tracks').find('h3', class_='tracks').text.strip())

    # Create a dictionary with the extracted data
    row_data = {
        "name": hash_string(name),
        "team": team,
        "geradelte_km": geradelte_km,
        "fahrten": fahrten,
    }
    return row_data


## i.e. table[2]
def parse_all_teams(soup):
    # Extract the desired data
    team = soup.find('td', class_='pl-sm-25').text.strip()

    geradelte_km_text = soup.find('td', class_='td-km').find('div', class_='bar_text').text.strip()
    geradelte_km = float(geradelte_km_text.replace(',', '.'))

    km_pro_kopf_text = soup.find('td', class_='hidden-xs', attrs={'data-order': '0'}).find('h3').text.strip()
    km_pro_kopf = float(km_pro_kopf_text.replace(',', '.'))

    fahrten = int(soup.find('td', class_='td-tracks').find('h3', class_='tracks').text.strip())

    active_radelnde = int(soup.find('td', class_='hidden-xs pr-sm-25').find('h3').text.strip())

    # Create a dictionary with the extracted data
    row_data = {
        "team": team,
        "geradelte_km": geradelte_km,
        "km_pro_kopf": km_pro_kopf,
        "fahrten": fahrten,
        "active_radelnde": active_radelnde
    }
    return row_data

def json_private_data(tables, pos):
    data = []
    for row in tables[pos].find("tbody").find_all("tr"):
        if pos == 2:
            data.append(parse_all_teams(row))
        elif(pos == 1):    
            data.append(parse_all_riders(row))
        elif(pos == 0):
            data.append(parse_my_team(row))
    return data

#region Script
## TODO While loop function with webhook callbacks
def main():

    print("Starting Script...")
    
    with open("credentials.json", "r") as file: 
        credentials = json.load(file)
        file.close()
    webhook_url = credentials["webhook"]

    last_execution = datetime.now()
    execution_period = timedelta(minutes=10) # adapt for slower / quicker execution
    next_execution = last_execution
    
    push_period = timedelta(hours=1)
    next_push = last_execution

    uploader = Uploader("gitlab.uni.kn", credentials)

    crawler = Crawler(credentials)
    crawler.refresh_session_id()
    while(True):
        last_execution = datetime.now()
        if(last_execution >= next_execution): # checks if we should execute again
            try:
                while not crawler.curl_uni():
                    crawler.refresh_session_id()
                
                crawler.curl_city(2228)

                # Now collect tables and append json with timestamp to data
                # public 
                public_json = {}
                public_json["timestamp"] = last_execution.isoformat()
                public_json["data"] = json_public_data(crawler)

                with open("../data/2025/public_data.json", "r") as readFile: 
                    json_array = json.load(readFile)
                    readFile.close()

                json_array.append(public_json)

                with open("../data/2025/public_data.json", "w") as writeFile:
                    json.dump(json_array, writeFile, indent=4)
                    writeFile.close()            


                ## private data
                soup = BeautifulSoup(crawler.private_txt, 'html.parser')
                tables = soup.find_all("table")
                for i in range(3):
                    private_json = {}
                    private_json["timestamp"] = last_execution.isoformat()
                    private_json["data"] = json_private_data(tables, i)

                    
                    with open(f"../data/2025/private_data_{i}.json", "r") as readFile: 
                        json_array = json.load(readFile)
                        readFile.close()

                    json_array.append(private_json)

                    with open(f"../data/2025/private_data_{i}.json", "w") as writeFile:
                        json.dump(json_array, writeFile, indent=4)
                        writeFile.close()            
                print(f"done with computing at {last_execution}")

                if(last_execution >= next_push ):
                    print("pushing to gitlab")
                    uploader.upload()
                    next_push = last_execution + push_period
                
                next_execution = last_execution + execution_period
                time.sleep(execution_period.seconds)
            except Exception as e:
                ## send webhook here 
                now = datetime.now().isoformat()
                webhook = SyncWebhook.from_url(webhook_url)
                webhook.send(f"{now}\nCrawl returned error!\n{e}\n{traceback.format_exc()}")
                print(now,e, traceback.format_exc())


        if(last_execution >= datetime(day=21, month=7, year=2025)):
            return 0 # kills this process automatically if forgotton on 21/7/2025




if __name__ == "__main__":
    main()