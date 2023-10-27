import requests
from bs4 import BeautifulSoup
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .models import Assets, Profile, Posts, Articles
import pandas as pd
import re
from datetime import datetime, timedelta
from decimal import Decimal 

def fetch_and_store_assets(category):
    base_url = "https://api.twelvedata.com/"
    endpoint_url = f"{base_url}{category}"
    response = requests.get(endpoint_url)

    if response.status_code == 200:
        data = response.json().get("data", [])
        number = 0
        
        for asset in data:
            name = asset.get("name", "")
            currency_quote = asset.get("currency_quote", "")
            currency_base = asset.get("currency_base", "")
            namee = currency_base + "-" + currency_quote
            symbol = asset.get("symbol", "")
            avatar = (name + ".png")
            exchange = asset.get("available_exchanges", "") 
            type = asset.get("type", "") 
            #for stocks if (exchange in ["XNGS"]) and (type in ["Common Stock"]):
            #for forex if (currency_quote in "US Dollar"): 
            # for etfs if (exchange in ["NASDAQ"]):
            if ("Binance" in exchange):
                Assets.objects.create(name=namee, symbol=symbol, avatar=avatar, category="Cryptocurrency")
                print(f"Category: {category}, Name: {name}, Symbol: {symbol}, Avatar: {avatar}, Currency: {exchange}")
                number = number + 1
        print(number)
    else:
        print(f"Failed to fetch data for {category}. Status Code: {response.status_code}")

def get_sentiment():
    news_data = []
     # Calculate the date 1 month ago from today
    one_month_ago = datetime.now() - timedelta(days=30)
    tickers = Assets.objects.all()
    finviz_url = 'https://finviz.com/quote.ashx?t='

    for ticker in tickers:
        url = finviz_url + ticker.symbol

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        html = BeautifulSoup(response.text, 'html.parser')

        # Find the news table
        news_table = html.find(id='news-table')

        if news_table:
            # Find all the news rows in the table
            news_rows = news_table.find_all('tr')

            for row in news_rows:
                # Extract the time, title, and source
                time_str = row.find('td', {'align': 'right'}).text.strip()
                title_container = row.find('a', {'class': 'tab-link-news'})
                title = title_container.text.strip()
                source = row.find('span').text.strip()
                source = source.strip("()")
                link = title_container['href']

                # Check if the time_str contains "Today" and replace it with the current date
                if "Today" in time_str:
                    date_str = datetime.now().strftime("%b-%d-%y")
                    time_str = time_str.replace("Today", "").strip()
                else:
                    # Check if there are two dates in the time_str
                    date_matches = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}-\d{2}', time_str)
                    if date_matches:
                        # Take the first date as the date_str and remove it from time_str
                        date_str = date_matches[0]
                        time_str = time_str.replace(date_str, "").strip()
                    else:
                        date_str = datetime.now().strftime("%b-%d-%y")

                # Combine date and time
                datetime_str = date_str + ' ' + time_str
                datetime_obj = datetime.strptime(datetime_str, "%b-%d-%y %I:%M%p")
                print(ticker.symbol)
                if datetime_obj >= one_month_ago:
                    asset = Assets.objects.get(symbol=ticker.symbol)
                    if title is not None and not Articles.objects.filter(article_text=title).exists():
                        Articles.objects.create(asset=asset, article_text=title, article_link=link, article_author=source, article_date=datetime_obj)

    return news_data


def get_asset_price():
    print('working')
    assets = Assets.objects.all()
    print(assets)
    api_key = "19ead0df350140c4a995f4a059a49f0b"  # Replace with your Twelve Data API key
    
    for asset in assets:
        symbol = asset.symbol  # Assuming your Asset model has a 'symbol' field
        base_url = "https://api.twelvedata.com/price"
        print(symbol)

        # Define the query parameters for the API request
        params = {
            "symbol": symbol,
            "apikey": api_key,
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            price = data.get("price")
            print(data)
            print("data")

            # Ensure 'price' is a valid numeric value before saving it
           
            asset.market_price = str(price)
            asset.save()


        else:
            print(f"Failed to fetch data for {symbol}: {response.status_code} - {response.text}")

def get_vader():
    articles = Articles.objects.all()
    posts = Posts.objects.all()
    vader = SentimentIntensityAnalyzer()

    for article in articles:
        title = article.article_text
        if article.article_polarity == 0.0:
            result = vader.polarity_scores(title)['compound']
            print(result)
            article.article_polarity = result
            article.save()
    for post in posts:
        title = post.post_text
        if post.post_polarity == 0.0:
            result = vader.polarity_scores(title)['compound']
            post.post_polarity = result
            post.save()
            
        


# plt.figure(figsize=(10,8))
# mean_df = df.groupby(['ticker', 'date']).mean().unstack()
# mean_df = mean_df.xs('compound', axis="columns")
# mean_df.plot(kind='bar')
# plt.show()