# Virtual Embed
With this api you can get your embeds as image (If you want to create embed visualizer for your bot, this api is for you!)


# Tutorial
Lets create Embed Object
```py
embed = VirtualEmbed(title="Virtual Embeds!",
                     description="With this api you can get embeds as images like this!!",
                     color="#fff")
```
If you say i don't want to make embed sender as **Ugly clyde** you can do this
```py
embed.bot_name = "Your bot Name"
embed.bot_avatar = "Avatar url"
```

Lets add some fields because it looks empty
```py
embed.add_field("Embed Fields Are", "SO COOOOL!", True)
embed.add_field("Also Inline Support", "Aweeeesome", True)
```

Who doesn't want images on embeds
```py
embed.set_author("Python Is Awesome",
                 icon_url="https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
                 
embed.set_thumbnail("https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
embed.set_image("https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
```

At Total
```py
embed = VirtualEmbed(title="Virtual Embeds!",
                     description="With this api you can get embeds as images like this!!",
                     color="#fff")
                     
embed.add_field("Embed Fields Are", "SO COOOOL!", True)
embed.add_field("Also Inline Support", "Aweeeesome", True)

embed.set_author("Python Is Awesome",
                 icon_url="https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
                 
embed.set_thumbnail("https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
embed.set_image("https://berkayyildiz.com/wp-content/uploads/2018/06/opengraph-icon-200x200.png")
```

##### We created our first embed, now lets see how can we use this object
With this line you can get your image object
```py
embed_img = embed.get_embed_as_image()
```

To save our image
```py
embed_img.save_img("path/to/example_embed.png")
# Save embed to target path
```
Or  get as bytes
```py
embed_img.get_as_bytes()
# This will return BytesIO object
```

# The Final Result
![Virtual Embed Is Awesome](https://i.imgur.com/niCkxhB.jpg)
