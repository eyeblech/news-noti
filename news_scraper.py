import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

# Define the NewsAPI key
NEWS_API_KEY = 'Your_api_key'

# Define the Discord webhook URL
DISCORD_WEBHOOK_URL = 'your_webhook_url'

def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}&country=us'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_date(date_str):
    """Format the date from ISO 8601 to a more readable format."""
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime('%B %d, %Y at %I:%M %p UTC')
    except ValueError:
        return 'Unknown Date'

def send_to_discord(news_data):
    if news_data:
        articles = news_data.get('articles', [])
        if articles:
            seen_titles = set()  # Track seen titles to avoid duplicates
            all_embeds = []
            
            for article in articles:
                title = article.get('title', 'No Title')
                description = article.get('description', 'No Description')
                url = article.get('url', '#')
                published_at = article.get('publishedAt', 'Unknown Date')
                image_url = article.get('urlToImage', '')
                
                # Skip if the title has been seen before
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                # Format the published date
                formatted_date = format_date(published_at)
                
                embed = DiscordEmbed(title=title, description=description, url=url, color='03b2f4')
                embed.set_footer(text=f"Date/Time: {formatted_date}")
                
                if image_url:
                    embed.set_image(url=image_url)
                
                all_embeds.append(embed)
            
            # Create a single webhook request for up to 10 embeds
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            
            if all_embeds:
                batch = all_embeds[:10]  # Only include the first 10 embeds
                webhook.embeds = []  # Clear previous embeds
                
                for embed in batch:
                    webhook.add_embed(embed)
                
                # Send the message
                response = webhook.execute()
                
                if response.status_code == 200:
                    print("Message sent successfully to Discord.")
                else:
                    print(f"Failed to send message to Discord: {response.status_code} {response.reason}")
        else:
            print("No articles found in the news data.")
    else:
        print("No news data to send.")

def main():
    news_data = fetch_news()
    if news_data:
        send_to_discord(news_data)
    else:
        print("Failed to fetch news data.")

if __name__ == '__main__':
    main()
