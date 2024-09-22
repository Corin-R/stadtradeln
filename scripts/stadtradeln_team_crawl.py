import time
import os
import codecs
from datetime import datetime, timedelta
import hashlib
import json


from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from discord import SyncWebhook



def hash_string_to_int(input_string):
    # Create a new sha256 hash object
    hash_object = hashlib.sha256()
    
    # Update the hash object with the bytes of the string
    hash_object.update(input_string.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    
    # Convert the hexadecimal hash to an integer
    hash_int = int(hash_hex, 16)
    
    return hash_int


### Extracts all <td> elements in the table entry and writes writes them to file.  
def parse_table_entry_anonymous(entry, timestamp: str):
    entry_values = entry.find_elements(By.TAG_NAME, "td")
    if(len(entry_values) < 1):
        return
    csv = f"\"{timestamp}\"" 
    for i in range(len(entry_values)):
        if(i >= 1 and i <= 4):
            if(i == 1):
                small_team = entry_values[i].find_element(By.TAG_NAME, "small")
                csv += f",\"{hash_string_to_int(entry_values[i].text)}\",\"{small_team.text}\""
            elif(i == 4):
                h3_text = entry_values[i].find_element(By.TAG_NAME, "h3")
                csv += f",\"{h3_text.text}\""
            else: 
                csv += f",\"{entry_values[i].text}\""
    
    f = codecs.open("./stadtradeln_team.csv", "a", "utf-8")
    if(os.stat("./stadtradeln_team.csv").st_size == 0):
        f.write("\"timestamp\", \"name_hash\", \"team\", \"sum_km\", \"rides\", \"kg_CO2-avoidance\"\n")
    f.write(f"{csv}\n")
    f.close()

def parse_table(tb, timestamp: str):
    entries = tb.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
    for entry in entries: 
        parse_table_entry_anonymous(entry, timestamp)
        


## executes the crawl of "https://www.stadtradeln.de/konstanz"
## Using Firefox
def execute_crawl():
    now_string = str(datetime.now().isoformat())
    
    driver = webdriver.Firefox() # Can be replaced with Chrome, Edge, etc
    driver.get("https://www.stadtradeln.de/home") # loads the page
        
    wait = WebDriverWait(driver, timeout=5, poll_frequency=.2)

    # GET CREDS
    file_path = 'credentials.json'

    # Open and read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract "password" and "name" values
    password = data.get('password')
    name = data.get('name')

    try:
        
        # LOGIN PROCESS
        wait.until(EC.presence_of_element_located((By.ID, "login-menu")))
        credentials_input = driver.find_element(By.ID, "login-menu")
        credentials_input.click()


        wait.until(EC.presence_of_element_located((By.NAME, "sr_username")))
        name_input = driver.find_element(By.NAME, "sr_username")

        name_input.send_keys(name)


        wait.until(EC.presence_of_element_located((By.NAME, "sr_password")))
        passwort_input = driver.find_element(By.NAME, "sr_password")

        passwort_input.send_keys(password)
        passwort_input.send_keys(Keys.ENTER)
        
        #############################################################################

        # NAVIGATE TO CORRECT PAGE
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sr_start_content")))
        sr_start_content = driver.find_element(By.CLASS_NAME, "sr_start_content")

        wait.until(EC.presence_of_element_located((By.ID, "my-team")))
        my_team = driver.find_element(By.ID, "my-team")

        my_team_link = my_team.find_element(By.LINK_TEXT, "Mein Team")
        my_team_link.click()


        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sr_start_content")))
        alle_radelnde_link = driver.find_element(By.LINK_TEXT, "Alle Radelnde")
        alle_radelnde_link.click()


        #############################################################################
        # Gets maximal page number
        number = int(driver.find_element(By.ID, "my-team-results-2-table_paginate").find_element(By.TAG_NAME, "span").find_elements(By.TAG_NAME, "a")[-1].text)


        ## HERE PARSE THE TABLE ENTRIES WITH HASH VALUE
        for i in range(number - 1):
            wait.until(EC.presence_of_element_located((By.ID, "my-team-results-2-table")))
            table = driver.find_element(By.ID, "my-team-results-2-table")
            parse_table(table, now_string)
            driver.find_element(By.ID, "my-team-results-2-table_next").click()

    
    
    except Exception as e :
        raise Exception(e)
    finally:
        driver.quit()


def main():
    print("Starting Script...")

    last_execution = datetime.now()
    execution_period = timedelta(minutes=10) # adapt for slower / quicker execution
    next_execution = last_execution
    exception_count = 0
    while(True):
        last_execution = datetime.now()
        if(exception_count > 10): # if exceptions happen too often, then break this and fix this code
            return
        if(last_execution >= next_execution): # checks if we should execute again 
            try:
                execute_crawl()
                print(f"{str(datetime.now().isoformat())}: Crawl Executed!")
                next_execution = last_execution + execution_period
                # time.sleep(int(execution_period.seconds/100)) # wakes up every (duration / 4) to check if we should execute again
            except Exception as e:
                exception_count += 1
                ## Something is wrong! :c
                ## Send Webhook
                print("========================================================================")
                print(f"{str(last_execution.isoformat())}: WARNING:\t\tCrawl returned error!\n{e}\nErrors occurred: {exception_count}")
                discord_webhook = "https://discord.com/api/webhooks/1247910681664028733/8iewsUHRAFoZKM7661hcQvBcppdXLbW5aTPhMaBoPG7Kiyvv3XWJPKLT80UywYd0MXg7"

                webhook = SyncWebhook.from_url(discord_webhook)
                webhook.send(f"Crawl returned error!\n{e}")
                

        if(last_execution >= datetime(day=21, month=7, year=2024)):
            return 0 # kills this process automatically if forgotton on 21/7/2024
    
if __name__ == "__main__":
    pid = str(os.getpid())
    pidfile = "./mydaemon.pid"

    codecs.open(pidfile, 'w').write(pid)
    try:
        main()
    finally:
        try:
            os.remove(pidfile)
        except:
            print("File not found")
