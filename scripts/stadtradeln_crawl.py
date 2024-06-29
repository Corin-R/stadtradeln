import time
import os
import codecs
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from discord import SyncWebhook

### Extracts all <td> elements in the table entry and writes writes them to file.  
def parse_table_entry(entry, timestamp: str):
    entry_values = entry.find_elements(By.TAG_NAME, "td")
    if(len(entry_values) < 1):
        return
    csv = f"\"{timestamp}\"" 
    for i in range(len(entry_values)):
        if(i >= 1 and i <= 5):
            csv += f",\"{entry_values[i].text}\""
    
    f = codecs.open("./stadtradeln_konstanz.csv", "a", "utf-8")
    if(os.stat("./stadtradeln_konstanz.csv").st_size == 0):
        f.write("timestamp, team, sum_km, rides, riders, km_per_head\n")
    f.write(f"{csv}\n")
    f.close()


## executes the crawl of "https://www.stadtradeln.de/konstanz"
## Using Firefox
def execute_crawl():
    now_string = str(datetime.now().isoformat())
    
    driver = webdriver.Firefox() # Can be replaced with Chrome, Edge, etc
    driver.get("https://www.stadtradeln.de/konstanz") # loads the page
        
    wait = WebDriverWait(driver, timeout=5, poll_frequency=.2)

    try:
        
        ## first we await until the page has loaded the data
        wait.until(EC.presence_of_element_located((By.ID, "numberOfResults_kommune")))
        entries_per_page_selector_div = driver.find_element(By.ID, "numberOfResults_kommune")
        # wait.until(EC.visibility_of(entries_per_page_selector_div))

        # we want to expand the number of entries to "alle"
        elements = entries_per_page_selector_div.find_elements(By.TAG_NAME, 'div')
        for element in elements:
            if(element.text == "Alle"): # warning, string comparison
                element.click()

        # Now we can extract the table
        wait.until(EC.presence_of_element_located((By.ID, "auswertungKommune")))
        # wait.until(EC.visibility_of(all_teams_table))
        all_teams_table = driver.find_element(By.ID, "auswertungKommune")

        # await for good measure, but the table should already be there
        # wait.until(lambda d : all_teams_table.is_displayed())

        # extracting all <tr> entries of the aforemenationed table
        all_teams_entries = all_teams_table.find_elements(By.TAG_NAME, "tr")
        if(len(all_teams_entries) <= 50):
            elements = entries_per_page_selector_div.find_elements(By.TAG_NAME, 'div')
            for element in elements:
                if(element.text == "Alle"): # warning, string comparison
                    element.click()
            all_teams_table = driver.find_element(By.ID, "auswertungKommune")
            all_teams_entries = all_teams_table.find_elements(By.TAG_NAME, "tr")
        if(len(all_teams_entries) <= 50):
            elements = entries_per_page_selector_div.find_elements(By.TAG_NAME, 'div')
            for element in elements:
                if(element.text == "Alle"): # warning, string comparison
                    element.click()
            all_teams_table = driver.find_element(By.ID, "auswertungKommune")
            all_teams_entries = all_teams_table.find_elements(By.TAG_NAME, "tr")
            
        # print("Team Count Entries:", len(all_teams_entries))
        if(len(all_teams_entries) <= 50):
            raise Exception(f"Even after trying to find it thrice, only <= 50 entries were found!\nTema Count Entries: {len(all_teams_entries)}")
        for entry in all_teams_entries:
            parse_table_entry(entry, now_string)
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
                print(f"{str(last_execution.isoformat())}: WARNING:\t\tCrawl returned error!\n{e}")
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
