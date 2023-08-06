# toontown.py
A simple Python API wrapper for the Toontown Rewritten/Corporate Clash API

## Features
- Asynchronous and synchronous
- API complete

## Installing
**Python 3.8 or higher is required**

```zsh
# Linux/macOS
python3 -m pip install -U toontown.py

# Windows
py -3 -m pip install -U toontown.py
```

## About

All methods return a tuple-like wrapper class with all the response data wrapped in objects (except Login and Status objects)

e.g. This will print all the news article URLs for Rewritten and Corporate Clash

```py
async def main():
    """Example main function"""
    session = aiohttp.ClientSession(raise_for_status=True)

    async with RewrittenAsyncToontownClient(session=session) as ttr_client, ClashAsyncToontownClient(session=session) as clash_client:
        news_list = await ttr_client.news(all=True)

        for news in news_list:
            print(news.article_url)

        news_list = await clash_client.news()

        for news in news_list:
            print(news.article_url)
```
