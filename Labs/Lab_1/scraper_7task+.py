import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone


def http_request(host, port, path):
    # Create a TCP socket
    sock = socket.create_connection((host, port))

    # Wrap the socket with SSL without verification
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification
    ssl_sock = context.wrap_socket(sock, server_hostname=host)

    # Create and send the HTTP request
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
    ssl_sock.sendall(request.encode())

    # Receive the response
    response_data = b""
    while True:
        chunk = ssl_sock.recv(4096)
        if not chunk:
            break
        response_data += chunk

    ssl_sock.close()
    return response_data.decode()

def extract_product_description(link):
    # Send a request to the individual product page
    product_response = http_request('999.md', 443, link)

    if product_response:
        product_soup = BeautifulSoup(product_response, 'html.parser')
        description_elem = product_soup.find('div', class_='adPage__content__description grid_18', itemprop='description')
        description = description_elem.text.strip() if description_elem else "N/A"
        return description
    else:
        print(f"Failed to access product page: {link}")
        return "N/A"

# Conversion functions
def convert_to_eur(price_mdl):
    conversion_rate = 20
    return round(price_mdl / conversion_rate, 2)

def convert_to_mdl(price_eur):
    conversion_rate = 20
    return round(price_eur * conversion_rate, 2)

# GET Request to main URL
url = "https://999.md/ro/list/transport/cars"
response = http_request('999.md', 443, '/ro/list/transport/cars')

# Check if the response is successful
if response:
    print("Successfully accessed the website.")
    print("-----------------------------\n")

    # Parse the HTML content
    soup = BeautifulSoup(response, 'html.parser')

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

        # Validate price to ensure it represents an integer and currency
        price_mdl, price_eur = 0, 0

        if 'lei' in price:
            price_cleaned = price.replace('lei', '').replace(' ', '').strip()
            if price_cleaned.isdigit():
                price_mdl = int(price_cleaned)
                price_eur = convert_to_eur(price_mdl)
        elif '€' in price:
            price_cleaned = price.replace('€', '').replace(' ', '').strip()
            if price_cleaned.isdigit():
                price_eur = int(price_cleaned)
                price_mdl = convert_to_mdl(price_eur)

        # Only extract the description if the link is valid
        if link != "N/A":
            description = extract_product_description(link)
        else:
            description = "N/A"

        # Append all product info including the description
        product_info.append({
            'name': name,
            'price_mdl': price_mdl,
            'price_eur': price_eur,
            'link': link,
            'fuel_type': fuel_type,
            'description': description
        })

    # Map prices to EUR or MDL
    def map_prices(product):
        if product['price_eur'] == 0:
            product['price_eur'] = convert_to_eur(product['price_mdl'])
        return product

    mapped_products = list(map(map_prices, product_info))

    # Filter products within a price range in EUR
    min_price = 5000
    max_price = 20000

    filtered_products = list(filter(lambda p: min_price <= p['price_eur'] <= max_price, mapped_products))

    # Reduce to sum up prices of the filtered products in EUR
    total_price_eur = reduce(lambda total, p: total + p['price_eur'], filtered_products, 0)

    # Attach a UTC timestamp
    timestamp = datetime.now(timezone.utc).isoformat() + 'Z'

    results = {
        'timestamp': timestamp,
        'total_price_eur': total_price_eur,
        'filtered_products': filtered_products
    }

    # Display the results
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total Price in EUR: {results['total_price_eur']}")
    print(f"Filtered Products Count: {len(results['filtered_products'])}")
    print("-----------------------------\n")
    for item in results['filtered_products']:
        print(f"Product Name: {item['name']}\nPrice in EUR: {item['price_eur']}\nLink: {item['link']}")
        print(f"Description: {item['description']}")
        print("-----------------------------\n")

else:
    print("Failed to access the website.")
