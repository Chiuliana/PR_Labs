import requests
from bs4 import BeautifulSoup

# GET Request
url = "https://999.md/ro/list/transport/cars"
response = requests.get(url)

# Check if the response is successful
if response.status_code == 200:
    print("Successfully accessed the website.")
    print("-----------------------------\n")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all products on the page
    products = soup.find_all('li', class_='ads-list-photo-item')

    # Store product information
    product_info = []

    # Loop through each product to extract the name, price, link, and fuel type
    for product in products:
        name_elem = product.find('div', class_='ads-list-photo-item-title')
        price_elem = product.find('span', class_='ads-list-photo-item-price-wrapper')
        link_elem = product.find('a', class_='js-item-ad')
        fuel_elem = product.find('span', class_='ads-list-photo-item-specifications-item')

        # If any element is missing, assign 'N/A'
        name = name_elem.text.strip() if name_elem else "N/A"
        price = price_elem.text.strip() if price_elem else "N/A"
        link = 'https://999.md' + link_elem['href'].strip() if link_elem else "N/A"
        fuel_type = fuel_elem.text.strip() if fuel_elem else "N/A"

        product_info.append({'name': name, 'price': price, 'link': link, 'fuel_type': fuel_type})

    for item in product_info:
        print(
            f"Product Name: {item['name']}\nPrice: {item['price']}\nLink: {item['link']}\nFuel Type: {item['fuel_type']}\n")
        print("-----------------------------\n")

    # print(response.text[:1000])  # Print first 1000 characters to verify response

else:
    print(f"Failed to access the website. Status code: {response.status_code}")
