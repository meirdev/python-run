import urllib.request

with urllib.request.urlopen("https://google.com") as response:
    print(response.read())
