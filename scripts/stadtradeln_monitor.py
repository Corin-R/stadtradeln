

from discord import SyncWebhook
from datetime import datetime, timedelta
import os
import time

def main():
    next_check_duration = timedelta(minutes=5) # adapt for slower / quicker execution
    while(True):
        now = datetime.now()
        if(now < datetime(day=21, month=7, year=2024)): # if latest date has not been reached yet
            if(not os.path.isfile("./mydaemon.pid")): # if the pid file has not been found
                discord_webhook = "https://discord.com/api/webhooks/1247910681664028733/8iewsUHRAFoZKM7661hcQvBcppdXLbW5aTPhMaBoPG7Kiyvv3XWJPKLT80UywYd0MXg7"

                webhook = SyncWebhook.from_url(discord_webhook)
                webhook.send(f"{str(datetime.now().isoformat())}: Crawl stopped!")
                return
            else:
                print(f"{str(now.isoformat())}: Crawl is active...")
                time.sleep(next_check_duration.seconds)
                




if __name__ == "__main__":
    main()
        
