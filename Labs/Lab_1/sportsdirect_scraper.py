import requests

# GET Request
url = "https://999.md/ro/category/transport"
response = requests.get(url)

# Check if the response is successful
if response.status_code == 200:
    print("Successfully accessed the website.")
    print(response.text)
else:
    print(f"Failed to access the website. Status code: {response.status_code}")
