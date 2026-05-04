import requests
import time
from bs4 import BeautifulSoup
import pandas as pd 

def clean_name(string):
    find = string.find(' (')
    return string[:find] if find != -1 else string

def clean_ram(string):
    if not string:
        return None
    f = string.lower().find('gb')
    return string[f - 2:f + 3] + ' RAM' if f != -1 else string

def clean_storage(string):
    if not string:
        return None
    s = string.lower()
    f = s.find('gb')
    return string[f - 4:f + 3] if f != -1 else string

def get_brand(string):
    text = string.lower()
    brands = ['Samsung', 'Apple', 'Vivo', 'Xiaomi', 'Oppo', 'Realme', 'Oneplus',
              'IQOO', 'Redmi', 'POCO', 'Motorola', 'Infinix', 'Tecno',
              'Google', 'Honor', 'Asus']
    
    for b in brands:
        if b.lower() in text:
            return b
    return ''

def clean_price(value):
    try:
        return float(value.replace('₹', '').replace(',', '').strip())
    except:
        return None


def get_data():
    raw_data = []

    for page in range(1, 6):
        url = "https://www.flipkart.com/search"
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {'q': 'mobile phones', 'page': page}

        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()

            if res.status_code == 429:
                time.sleep(2)
                continue

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            time.sleep(2)
            continue

        soup = BeautifulSoup(res.text, 'html.parser')

        # safer product selection
        products = soup.find_all('div', attrs={'data-id': True})

        for product in products:

            reviews = None
            review_tag = product.find('span', class_="PvbNMB")
            if review_tag:
                parts = list(review_tag.stripped_strings)
                if len(parts) >= 3:
                    reviews = parts[2]

            name_tag = product.find('div', class_='RG5Slk')
            price_tag = product.find('div', class_='hZ3P6w')
            rating_tag = product.find('div', class_='MKiFS6')

            if not name_tag or not price_tag:
                continue

            specs_container = product.find('ul')
            li_items = specs_container.find_all('li') if specs_container else []

            ram = battery = storage = None

            for li in li_items:
                text = li.text.lower().strip()

                if 'gb' in text and 'ram' in text:
                    ram = li.text.strip()

                elif 'mah' in text:
                    battery = li.text.strip()

                elif 'gb' in text and 'ram' not in text:
                    storage = li.text.strip()

            try:
                name = name_tag.text.strip()
                cleaned_name = clean_name(name)
                brand = get_brand(name)
                price = clean_price(price_tag.text)
                rating = float(rating_tag.text.strip()) if rating_tag else None

                cleaned_ram = clean_ram(ram)
                cleaned_storage = clean_storage(storage)

                raw_data.append({
                    'Name': cleaned_name,
                    'Brand': brand,
                    'Price': price,
                    'Rating': rating,
                    'Reviews': reviews,
                    'Ram': cleaned_ram,
                    'Storage': cleaned_storage,
                    'Battery': battery
                })

            except Exception as e:
                print("Error parsing product:", e)
                continue

        time.sleep(2)  # prevent blocking

    return raw_data if raw_data else None

def filter_data(details):
    if not details:
        return None

    filtered_data = [p for p in details if p['Price'] and p['Price'] < 20000]
    filtered_data = [p for p in filtered_data if '5G' in p['Name']]
    return filtered_data if filtered_data else None

def data_format(information):
    df = pd.DataFrame(information)

    df = df.dropna(subset=['Price', 'Rating'])
    df = df.sort_values(by='Price')

    df.to_csv('Mobile_Data.csv', index=False)
    print('Saved data to Mobile_Data.csv')

    return df

def main():
    print('Fetching Data...')
    time.sleep(1)
    info = get_data()
    if not info:
        print("Failed to fetch data")
        return
    fil = filter_data(info)
    if not fil:
        print("No filtered data")
        return
    data_format(fil)
    print('Done!')

if __name__ == '__main__':
    main()

