import requests
from bs4 import BeautifulSoup

def get_ronde_ebay_price():
    # URL de búsqueda de eBay para el juego "Ronde Sega Saturn"
    url = "https://www.ebay.com/sch/i.html?_nkw=ronde+sega+saturn&_sacat=0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Error al conectar con eBay")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    prices = []
    items = soup.find_all('div', class_='s-item__info')
    
    for item in items:
        price_element = item.find('span', class_='s-item__price')
        if price_element:
            price_text = price_element.text.strip()
            clean_price = price_text.replace('$', '').replace(',', '').split('to')[0].strip()
            try:
                prices.append(float(clean_price))
            except ValueError:
                continue
                
    if prices:
        average_price = sum(prices) / len(prices)
        print(f"Precio promedio calculado de Ronde en eBay: ${average_price:.2f}")
        return average_price
    else:
        print("No se encontraron precios.")
        return None

if __name__ == "__main__":
    get_ronde_ebay_price()