# Stadtradeln Constance Crawling

As of today 29th June 2024, the stadtradeln event for the city of Constance has concluded. 

Currently, there is a week-long timeframe, where furhter submissions are allowed. 

After this week is over, I will upload my **cleaned** raw data and some evaluation figures about it. 

#### Vocabulary

I will refer to some things that needs explaining: 

- active time period: 
The time period where the event was currently ongoing the the city of Constance. Started 2024 - 06 - 08 T 00:00:00 and ended 2024 - 06 - 28 T 23:59:00. 

- passive time period: 
The time period, where the event was over, however it was allowed to submit further rides. This is a week long time period. Started 2024 - 06 - 29 T 00:00:00 and Ended 2024 - 07 - 05 T 23:59:00. 

## Crawling Code

The crawling code can be found in [here](https://github.com/Corin-R/stadtradeln/tree/main/scripts)

There is a README explaining the usage and details and possibly changes to the code. 

# Analysis

## Kilometers traveled by top 10 teams

See these figures


![Kilometers](evaluations/km_top_10_teams_f.png)


![Kilometers_close](evaluations/km_top_10_teams_closeup.png)


The second figure is a closeup of the first week where the competition was quite fierce. 

The blue columns mark the respective weekends. Naturally, the event for Konstanz started at a Saturday and ended on a Friday. 

## Participating Riders per team 


![Riders](evaluations/Number_Of_Riders_Top_Teams_f.png)


## Weather

The wether data was downloaded after the event from meteoblue.com 

![weather](evaluations/meteogram_history.png)


### Data statistics

![Crawling Mishaps](evaluations/data_consistency.png)

This figure displays how many times a date appears in the original data. 

With this figure, we can easily identify what went wrong while crawling. 

Most importantly, there are two major gaps.

The first gap spans from 18.06 at 08:00 to 19.06 at 14:00 

The second gap spans from 24.06 at 20:00 to 25.06 at 08:00

The first gap was a mishap from me, when I did not notice that the crawl has suspended. The second gap was me having a good nights rest and noticing at the morning. 

Relatively speaking in the beginning on the 11.06 my PC had a forced windows update, which resetted my time to UTC. That is why there are some timestamps missing at 10:00. 

There are some duplicate timestamps at 20:00 the same day, which is attributed to me resetting my time to local time again. 

Lesson learned, I will timestamp my crawl using utc and not local pc time. 

