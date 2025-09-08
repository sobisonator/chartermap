# Credit
This API makes use of the Prosopography of Anglo-Saxon England (PASE) database, ‘Digital Strategy’, Prosopography of Anglo-Saxon England, https://www.pase.ac.uk, accessed 8 August 2025.

## Disclaimer
> This script interacts with the PASE API endpoints.  
> The PASE API is **not an officially supported public API**. Usage should be limited and comply with the [`robots.txt`](https://pase.ac.uk/robots.txt) policy.  
> Do not overload the PASE servers. Script is for **academic / personal research only**.

## Overview

This Python script collects **normalised Anglo-Saxon names** from the [PASE database](https://pase.ac.uk) by crawling its JSON endpoints.  

Features:

- Automatically respects `robots.txt` and crawl delays.
- Rate-limited requests (`ratelimiter` library).
- Retrieves normalised names by initial letter.
- Stores raw JSON data locally.
- Converts results into a clean **CSV of names (ID, Name)**.