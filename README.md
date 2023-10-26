# Tiktok_Scraper
This project is a robust tool designed for scraping content from TikTok without needing an API. This tool helps in gathering data that can be useful for various analytical purposes.

## Features

- Scrape trending fashion related TikTok videos
- Extract detailed information about the videos.
- Information extracted per videos are Post Link, Username, Likes, Comments, Saved, Captions, Hashtags, Post Date, Created Date

  <img width="1404" alt="Screenshot 2023-10-26 at 12 10 05 AM" src="https://github.com/Shreyj14/Tiktok_Scrapper/assets/118795427/5e7c54ad-1813-4e9b-b6f2-4abdd5480521">

<img width="1414" alt="Screenshot 2023-10-26 at 12 10 20 AM" src="https://github.com/Shreyj14/Tiktok_Scrapper/assets/118795427/bb883a4b-e2b9-4b55-8501-43463b8b7b49">

## Installation

Clone the repository and navigate to the directory

```bash
git clone https://github.com/Shreyj14/Tiktok_Scrapper.git
cd Tiktok_Scrapper
docker build -t scraper:latest .  
docker run  --shm-size=1g -v ./outputs:/usr/src/app/outputs scraper:latest
