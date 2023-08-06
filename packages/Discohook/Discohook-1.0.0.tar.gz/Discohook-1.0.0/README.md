# Discohook

[![GitHub license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Janakthegamer/Discohook/blob/main/LICENSE)
[![PyPI version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&type=6e&v=1.0.0&x2=0)](https://badge.fury.io/py/discohook)
[![Discord](https://img.shields.io/discord/523403028720779275)](https://discord.gg/5bqjEbb)

A basic Library to send Discord Webhook

## Install

install via pip: 
```py
# Windows
pip install discohook

# Linux / MacOs
pip3 install discohook
```

## Examples

* [Basic Webhook](#basic-webhook)
* [Manage Being Rate Limited](#manage-being-rate-limited)
* [Multiple Webhook Urls](#multiple-webhook-urls)
* [Embedded Content](#webhook-with-embedded-content)
* [Edit Webhook Message](#edit-webhook-messages)
* [Delete Webhook Message](#delete-webhook-messages)
* [Send Files](#send-files)
* [Remove Embeds and Files](#remove-embeds-and-files)
* [Allowed Mentions](#allowed-mentions)
* [Use Proxies](#use-proxies)

### basic webhook
```python
from discohook.client import Discohook

webhook = Discohook(url='your webhook url', content='Webhook Message')
response = webhook.execute()
```

### manage being rate limited
```python
from discohook.client import Discohook

# if rate_limit_retry is True then in the event that you are being rate 
# limited by Discord your webhook will automatically be sent once the 
# rate limit has been lifted
webhook = Discohook(
    url='your webhook url',
    rate_limit_retry=True,
    content='Webhook Message'
)
response = webhook.execute()
```


### multiple webhook urls
```python
from discohook.client import Discohook

webhook_urls = [
    'webhook url 1',
    'webhook url 2'
]
webhook = Discohook(url=webhook_urls, content='Webhook Message')
response = webhook.execute()
```


### webhook with embedded content
```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url='your webhook url')

# create embed object for webhook
# you can set the color as a decimal (color=242424) or hex (color='03b2f8') number
embed = DiscohookEmbed(
    title='Your Title',
    description='Lorem ipsum dolor sit',
    color='03b2f8'
)

# add embed object to webhook
webhook.add_embed(embed)

response = webhook.execute()
```


```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url='your webhook url')

# create embed object for webhook
embed = DiscohookEmbed(title='Your Title', description='Lorem ipsum dolor sit', color='03b2f8')

# set author
embed.set_author(name='Author Name', url='author url', icon_url='author icon url')

# set image
embed.set_image(url='your image url')

# set thumbnail
embed.set_thumbnail(url='your thumbnail url')

# set footer
embed.set_footer(text='Embed Footer Text', icon_url='URL of icon')

# set timestamp (default is now)
embed.set_timestamp()

# add fields to embed
embed.add_embed_field(name='Field 1', value='Lorem ipsum')
embed.add_embed_field(name='Field 2', value='dolor sit')

# add embed object to webhook
webhook.add_embed(embed)

response = webhook.execute()
```

This is another example with embedded content
```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url='your webhook url', username="New Webhook Username")

embed = DiscohookEmbed(title='Embed Title', description='Your Embed Description', color='03b2f8')
embed.set_author(name='Author Name', url='https://github.com/lovvskillz', icon_url='https://avatars0.githubusercontent.com/u/14542790')
embed.set_footer(text='Embed Footer Text')
embed.set_timestamp()
embed.add_embed_field(name='Field 1', value='Lorem ipsum')
embed.add_embed_field(name='Field 2', value='dolor sit')
embed.add_embed_field(name='Field 3', value='amet consetetur')
embed.add_embed_field(name='Field 4', value='sadipscing elitr')

webhook.add_embed(embed)
response = webhook.execute()
```

By default, the embed fields are placed side by side. We can arrangee them in a new line by setting `inline=False` as follows
```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url="your webhook url", username="New Webhook Username")

embed = DiscohookEmbed(
    title="Embed Title", description="Your Embed Description", color='03b2f8'
)
embed.set_author(
    name="Author Name",
    url="https://github.com/lovvskillz",
    icon_url="https://avatars0.githubusercontent.com/u/14542790",
)
embed.set_footer(text="Embed Footer Text")
embed.set_timestamp()
# Set `inline=False` for the embed field to occupy the whole line
embed.add_embed_field(name="Field 1", value="Lorem ipsum", inline=False)
embed.add_embed_field(name="Field 2", value="dolor sit", inline=False)
embed.add_embed_field(name="Field 3", value="amet consetetur")
embed.add_embed_field(name="Field 4", value="sadipscing elitr")

webhook.add_embed(embed)
response = webhook.execute()
```


### edit webhook messages

```python
from discohook.client import Discohook
from time import sleep

webhook = Discohook(url='your webhook url', content='Webhook content before edit')
sent_webhook = webhook.execute()
webhook.content = 'After Edit'
sleep(10)
sent_webhook = webhook.edit(sent_webhook)
```

### delete webhook messages

```python
from discohook.client import Discohook
from time import sleep

webhook = Discohook(url='your webhook url', content='Webhook Content')
sent_webhook = webhook.execute()
sleep(10)
webhook.delete(sent_webhook)
```

### send files

```python
from discohook.client import Discohook

webhook = Discohook(url='your webhook url', username="Webhook with files")

# send two images
with open("path/to/first/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example.jpg')
with open("path/to/second/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example2.jpg')

response = webhook.execute()
```

You can use uploaded attachments in embeds:
```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url='your webhook url')

with open("path/to/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example.jpg')

embed = DiscohookEmbed(title='Embed Title', description='Your Embed Description', color='03b2f8')
embed.set_thumbnail(url='attachment://example.jpg')

webhook.add_embed(embed)
response = webhook.execute()
```

### remove embeds and files
```python
from discohook.client import Discohook, DiscohookEmbed

webhook = Discohook(url='your webhook url')

with open("path/to/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example.jpg')

embed = DiscohookEmbed(title='Embed Title', description='Your Embed Description', color='03b2f8')
embed.set_thumbnail(url='attachment://example.jpg')

webhook.add_embed(embed)
response = webhook.execute(remove_embeds=True, remove_files=True)
# webhook.files and webhook.embeds will be empty after webhook is executed
# You could also manually call the functions webhook.remove_files() and webhook.remove_embeds()
```

`.remove_file()` removes the given file
```python
from discohook.client import Discohook

webhook = Discohook(url='your webhook url', username="Webhook with files")

# send two images
with open("path/to/first/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example.jpg')
with open("path/to/second/image.jpg", "rb") as f:
    webhook.add_file(file=f.read(), filename='example2.jpg')
# remove 'example.jpg'
webhook.remove_file('example.jpg')
# only 'example2.jpg' is sent to the webhook
response = webhook.execute()
```

### allowed mentions

Look into the [Discord Docs](https://discord.com/developers/docs/resources/channel#allowed-mentions-object) for examples and an explanation

This example would only ping user `123` and `124` but not everyone else.

```python
from discohook.client import Discohook

content = "@everyone say hello to our new friends <@123> and <@124>"
allowed_mentions = {
    "users": ["123", "124"]
}

webhook = Discohook(url='your webhook url', content=content, allowed_mentions=allowed_mentions)
response = webhook.execute()
```

### use proxies

```python
from discohook.client import Discohook

proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
webhook = Discohook(url='your webhook url', content='Webhook Message', proxies=proxies)
response = webhook.execute()
```
or
```python
from discohook.client import Discohook

proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}
webhook = Discohook(url='your webhook url', content='Webhook Message')
webhook.set_proxies(proxies)
response = webhook.execute()
```
