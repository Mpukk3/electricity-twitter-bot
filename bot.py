import tweepy
import requests
import os
from datetime import datetime, timedelta

# Get credentials from environment variables
API_KEY = os.environ.get('TWITTER_API_KEY')
API_SECRET = os.environ.get('TWITTER_API_SECRET')
ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

def get_electricity_prices():
    """Fetch electricity prices from Elering API"""
    url = "https://dashboard.elering.ee/api/nps/price"
    
    try:
        response = requests.get(url, params={
            "start": datetime.now().strftime("%Y-%m-%d"), 
            "end": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        })
        response.raise_for_status()
        data = response.json()
        
        prices = []
        for entry in data['data']['ee']:
            timestamp = datetime.fromtimestamp(entry['timestamp'])
            price = entry['price']
            prices.append({'time': timestamp, 'price': price})
        
        return prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return None

def find_most_expensive_hours(prices):
    """Find the 2 most expensive hours"""
    if not prices:
        return None
    sorted_prices = sorted(prices, key=lambda x: x['price'], reverse=True)
    return sorted_prices[:2]

def create_tweet(expensive_hours):
    """Create tweet message"""
    if not expensive_hours or len(expensive_hours) < 2:
        return None
    
    tweet = "⚡ Kalleim elekter Eestis täna:\n\n"
    
    for i, hour in enumerate(expensive_hours, 1):
        time_str = hour['time'].strftime('%H:%M')
        price_cents = hour['price'] / 10
        tweet += f"{i}. {time_str} - {price_cents:.2f} s/kWh\n"
    
    tweet += f"\n📅 {datetime.now().strftime('%d.%m.%Y')}"
    return tweet

def post_tweet(message):
    """Post tweet to Twitter"""
    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )
        
        response = client.create_tweet(text=message)
        print(f"Tweet posted! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"Error posting tweet: {e}")
        return False

def main():
    print("Fetching electricity prices...")
    prices = get_electricity_prices()
    
    if prices:
        expensive_hours = find_most_expensive_hours(prices)
        if expensive_hours:
            tweet_message = create_tweet(expensive_hours)
            print(f"\nTweet:\n{tweet_message}\n")
            post_tweet(tweet_message)

if __name__ == "__main__":
    main()

#