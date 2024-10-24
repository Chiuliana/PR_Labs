import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone


def http_request(host, port, path):
    sock = socket.create_connection((host, port))

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ssl_sock = context.wrap_socket(sock, server_hostname=host)

    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n"
    ssl_sock.sendall(request.encode())

    response_data = b""
    while True:
        chunk = ssl_sock.recv(4096)
        if not chunk:
            break
        response_data += chunk

    ssl_sock.close()
    return response_data.decode()


def extract_product_description(link):
    product_response = http_request('999.md', 443, link)

    if product_response:
        product_soup = BeautifulSoup(product_response, 'html.parser')
        description_elem = product_soup.find('div', class_='adPage__content__description grid_18',
                                             itemprop='description')
        description = description_elem.text.strip() if description_elem else "N/A"
        return description[:100]
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


# Custom Serialization Functions
def serialize(value):
    """Serialize a Python object to a custom string format."""
    if isinstance(value, dict):
        items = []
        for key, val in value.items():
            items.append(f'D:k:str({key}):v:{serialize(val)}')
        return 'D:' + ';'.join(items)

    elif isinstance(value, list):
        items = [serialize(item) for item in value]
        return 'L:' + ';'.join(items)

    elif isinstance(value, str):
        return f'str({value})'

    elif isinstance(value, int):
        return f'int({value})'

    elif isinstance(value, float):
        return f'float({value})'

    elif value is None:
        return 'None'

    else:
        raise ValueError(f"Unsupported data type: {type(value)}")


def deserialize(serialized_str):
    """Deserialize a custom string format back into a Python object."""

    def parse_value(value_str):
        if value_str.startswith('D:'):
            # Dictionary
            items = value_str[2:].split(';')
            result = {}
            for item in items:
                key, val = item.split(':', 2)[1:3]  # Get key and value part
                key = key.split('(')[1][:-1]  # Extract key
                result[key] = parse_value(val)
            return result

        elif value_str.startswith('L:'):
            # List
            items = value_str[2:].split(';')
            return [parse_value(item) for item in items]

        elif value_str.startswith('str('):
            return value_str[4:-1]  # Extract string

        elif value_str.startswith('int('):
            return int(value_str[4:-1])  # Extract integer

        elif value_str.startswith('float('):
            return float(value_str[6:-1])  # Extract float

        elif value_str == 'None':
            return None

        else:
            raise ValueError(f"Invalid serialized string: {value_str}")

    # Start parsing
    return parse_value(serialized_str)


# GET Request to main URL
url = "https://999.md/ro/list/transport/cars"
response = http_request('999.md', 443, '/ro/list/transport/cars')

if response:
    print("Successfully accessed the website.")
    print("-----------------------------\n")

    soup = BeautifulSoup(response, 'html.parser')

    products = soup.find_all('li', class_='ads-list-photo-item')

    product_info = []

    for product in products:
        name_elem = product.find('div', class_='ads-list-photo-item-title')
        price_elem = product.find('span', class_='ads-list-photo-item-price-wrapper')
        link_elem = product.find('a', class_='js-item-ad')
        fuel_elem = product.find('span', class_='ads-list-photo-item-specifications-item')

        name = name_elem.text.strip() if name_elem else "N/A"
        price = price_elem.text.strip() if price_elem else "N/A"
        link = 'https://999.md' + link_elem['href'].strip() if link_elem else "N/A"
        fuel_type = fuel_elem.text.strip() if fuel_elem else "N/A"

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

        if link != "N/A":
            description = extract_product_description(link)
        else:
            description = "N/A"

        product_info.append({
            'name': name,
            'price_mdl': price_mdl,
            'price_eur': price_eur,
            'link': link,
            'fuel_type': fuel_type,
            'description': description
        })


    def map_prices(product):
        if product['price_eur'] == 0:
            product['price_eur'] = convert_to_eur(product['price_mdl'])
        return product


    mapped_products = list(map(map_prices, product_info))

    min_price = 5000
    max_price = 20000

    filtered_products = list(filter(lambda p: min_price <= p['price_eur'] <= max_price, mapped_products))

    total_price_eur = reduce(lambda total, p: total + p['price_eur'], filtered_products, 0)

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

    # Serialize results to custom string format
    serialized_results = serialize(results)
    print("Serialized Results:", serialized_results)

    # Save the serialized output to a file
    with open('products_custom.txt', 'w', encoding='utf-8') as custom_file:
        custom_file.write(serialized_results)
    print("Custom Output saved to products_custom.txt")

else:
    print("Failed to access the website.")
