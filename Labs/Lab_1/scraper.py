import requests
from bs4 import BeautifulSoup

def extract_product_description(link):
    # Send a request to the individual product page
    product_response = requests.get(link)

    if product_response.status_code == 200:
        product_soup = BeautifulSoup(product_response.text, 'html.parser')

        description_elem = product_soup.find('div', class_='adPage__content__description grid_18', itemprop='description')

        description = description_elem.text.strip() if description_elem else "N/A"

        return description
    else:
        print(f"Failed to access product page: {link}")
        return "N/A"

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

    # Loop through each product to extract the name, price, link, fuel type, and description
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

        # Validate name and fuel_type to remove whitespaces
        name = name.strip()
        fuel_type = fuel_type.strip()

        # Validate price to ensure it represents an integer
        if price != "N/A":
            # Remove spaces and currency symbol, then check if it can be converted to an integer
            price_cleaned = price.replace('€', '').replace(' ', '').strip()
            if price_cleaned.isdigit():
                price = int(price_cleaned)
            else:
                price = "N/A"
        else:
            price = "N/A"

        # Only extract the description if the link is valid
        if link != "N/A":
            description = extract_product_description(link)
        else:
            description = "N/A"

        # Check if all fields are 'N/A' and skip if true
        if name == "N/A" and price == "N/A" and link == "N/A" and fuel_type == "N/A":
            continue

        # Append all product info including the description
        product_info.append({
            'name': name,
            'price': price,
            'link': link,
            'fuel_type': fuel_type,
            'description': description
        })

    # Display the final product info
    for item in product_info:
        print(f"Product Name: {item['name']}\nPrice: {item['price']}\nLink: {item['link']}\nFuel Type: {item['fuel_type']}")
        print("*****************************\n")
        print(f"Description: \n{item['description']}")
        print("\n-----------------------------\n")

else:
    print(f"Failed to access the website. Status code: {response.status_code}")
