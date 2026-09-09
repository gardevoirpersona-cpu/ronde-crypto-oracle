import os
import requests
from bs4 import BeautifulSoup
from web3 import Web3

def get_ronde_ebay_price():
    url = "https://www.ebay.com/sch/i.html?_nkw=ronde+sega+saturn&_sacat=0"
    
    # Cabeceras más avanzadas para imitar a un navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"eBay bloqueó la petición o respondió con estado: {response.status_code}. Usando precio de respaldo.")
            return get_fallback_price()

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
            return int(average_price)
        else:
            print("No se encontraron elementos de precio. Usando precio de respaldo.")
            return get_fallback_price()
            
    except Exception as e:
        print(f"Excepción de conexión: {e}. Usando precio de respaldo.")
        return get_fallback_price()

def get_fallback_price():
    # Precio simulado o de respaldo histórico para evitar que el oráculo falle 
    # cuando eBay bloquea temporalmente al servidor de GitHub.
    fallback = 10 
    print(f"Usando precio de respaldo predeterminado: ${fallback}")
    return fallback

def update_blockchain_price(price):
    infura_url = "https://rpc.ankr.com/eth_sepolia" 
    w3 = Web3(Web3.HTTPProvider(infura_url))

    if not w3.is_connected():
        print("Error al conectar con la red Sepolia")
        return

    private_key = os.environ.get("PRIVATE_KEY")
    contract_address = os.environ.get("CONTRACT_ADDRESS")

    abi = [
        {
            "inputs": [{"internalType": "uint256", "name": "_newPrice", "type": "uint256"}],
            "name": "updatePriceFromOracle",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
    account = w3.eth.account.from_key(private_key)

    nonce = w3.eth.get_transaction_count(account.address)

    txn = contract.functions.updatePriceFromOracle(price).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.eth.gas_price
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"¡Precio actualizado en la blockchain! Hash de transacción: {w3.to_hex(tx_hash)}")

if __name__ == "__main__":
    price = get_ronde_ebay_price()
    if price:
        update_blockchain_price(price)
