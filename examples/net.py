import urllib.request

with urllib.request.urlopen("https://www.google.com") as response:
    print(response.read())
