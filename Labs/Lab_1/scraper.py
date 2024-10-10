import requests
from bs4 import BeautifulSoup

# GET Request
url = "https://999.md/ro/list/transport/cars"
response = requests.get(url)

# Check if the response is successful
if response.status_code == 200:
    print("Successfully accessed the website.")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all products on the page
    products = soup.find_all('li', class_='ads-list-photo-item')

    # Store product information
    product_info = []

    # Loop through each product to extract the name and price
    for product in products:
        name_elem = product.find('div', class_='ads-list-photo-item-title')
        price_elem = product.find('span', class_='ads-list-photo-item-price-wrapper')

        if name_elem and price_elem:  # Check if elements were found
            name = name_elem.text.strip()
            price = price_elem.text.strip()
            product_info.append({'name': name, 'price': price})
        else:
            print("Name & Price not found for a product.")

    # Print product information
    for item in product_info:
        print(f"Product Name: {item['name']}, Price: {item['price']}")

    # print(response.text)

else:
    print(f"Failed to access the website. Status code: {response.status_code}")
