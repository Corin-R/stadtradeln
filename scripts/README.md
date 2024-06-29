# Webcrawler for "stadtradeln konstanz"

File consists of two files

1. `stadtradeln_crawl.py`
2. `stadtradeln_monitor.py`

## Usage

#### Windows

Open two terminals, first execute `python stadtradeln_crawl.py` then in the second one execute `python stadtradeln_monitor.py`

Be sure to change the webhook address in both files. 

#### Linux

For some reason, I get the error that Firefox cannot be used for that crawl (I was too lazy to figure out a way and to research why).

Therefore, instead of `driver = webdriver.Firefox() ` use `driver = webdriver.Chrome()`. I have really no idea why. 

## Key Notes

### 1. stadtradeln_crawl

#### General workflow

Main component which tries to open https://www.stadtradeln.de/konstanz and locates the "alle" for the entries per page and clicks it. 

Next it locates the table that contains all information we want and iterates over the elements. 

It automatically writes (appends) the extracted data to the file `stadtradeln_konstanz.csv`. It creates it if it is not found. 

The function `execute_crawl()` is wrapped in a while loop, which periodically calls this function. 

The time period between each crawl can be updated in `execution_period`. 

Between each call of `execute_crawl()` the process sleeps dynamically a quarter of the allocated `execution_period`. 


#### stadtradeln_konstanz.csv

Header is looks like this: 

timestamp, team, sum_km, rides, riders, km_per_head

**timestamp**   (string) : Current timestamp in localtime. ISO 8601 format

**team**        (string) : Team written as a string. We need to be careful if a team has an comma in its name. I did not sanitize the input.

**sum_km**          (int): Could be a float. Sum of all km that the team rode. Column "geradelte km"

**rides**           (int): Sum of all rides that the team submitted. Column "Fahrten"

**riders**          (int): Sum of all registered team members. Column "Radelnde"

**km_per_head**     (int): Could be a float. Is expressed in sum_km devided by riders. 

#### Error handling

The script creates a temporary file called "mydaemon.pid" which is useful for keeping track if the process is still alive. Mainly used by `stadtradeln_monitor.py`

If an error occurs while executing the crawl, it automatically writes it to a webhook, specifically a discord webhook. 

***Please make sure to change webhook address before executing the script.***

Furthermore, if an exception occurrs an exception counter is incremented. If it reaches a specific number ( in my code 10) then it automatically kills this process. 

If this script detects that we have reached a date of 21.07.2024, then it automatically kills this process too. 

Lastly, if an error occurs, the script retries automatically. 

### 2. stadtradeln_monitor.py

This file is a simple while loop, which breaks automatically after reaching the date 21.07.2024. 

While it has not reached this date, it checks if it can locate in the same directory the file `mydeamon.pid` which is created by `stadtradeln_crawl.py`. 

If this file has not been found - which indicates either the process has stopped or the process was started somewhere else and thus the file is not in the same directory - it returns and most importantly sends an error to the discord webhook. 

## Changes

#### V2

- on error, `execute_crawl()` automatically closes the opened window. 
- in `stadtradeln_konstanz.csv`, just one timestamp is used, not several different, differing in only a couple of seconds. 
- added timestamps for the console logging
- Extended the wait function to handle the error `NoSuchElementException` and retry automatically until the element is found. Times-out after 5 seconds.  
- added this README


