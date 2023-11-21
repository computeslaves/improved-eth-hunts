import time
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from web3 import Web3, Account
import pyfiglet
import textwrap

banner_text = "ETHER HUNT"
wrapped_text = "\n".join(textwrap.wrap(banner_text, width=40))
banner = pyfiglet.figlet_format(wrapped_text)
print(banner)

# Print the welcome message
print('Welcome to ETHER HUNT by Sinatra.')

# Ethereum node URL
ETH_NODE_URL = "https://eth-mainnet.gateway.pokt.network/v1/5f3453978e354ab992c4da79"
# Number of threads to use
NUM_THREADS = 4

def generate_private_key():
    # Generate a private key from a larger seed space
    seed = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
    private_key = Web3.keccak(text=seed).hex()
    return private_key

def derive_address(private_key):
    # Derive the address from the private key
    account = Account.from_key(private_key)
    address = account.address
    return address

def check_balance(address):
    w3 = Web3(Web3.HTTPProvider(ETH_NODE_URL))
    balance = w3.eth.get_balance(address)
    return balance

def generate_and_check():
    private_key = generate_private_key()
    address = derive_address(private_key)
    balance = check_balance(address)
    return private_key, address, balance

def format_balance(balance):
    return f"{balance:,} ETH"

def format_speed(start_time, processed):
    elapsed = time.time() - start_time
    speed = processed / elapsed
    return f"{speed:.2f} addresses/s"

def display_progress(processed, start_time):
    elapsed = time.time() - start_time
    speed = format_speed(start_time, processed)
    print(f"Processed: {processed} | Speed: {speed} | Elapsed Time: {elapsed:.2f}s", end="\r")

if __name__ == "__main__":
    start_time = time.time()
    processed = 0

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        while True:
            futures = [executor.submit(generate_and_check) for _ in range(NUM_THREADS)]

            for future in as_completed(futures):
                processed += 1
                display_progress(processed, start_time)

                private_key, address, balance = future.result()

                print("\nGenerated Address:")
                print(f"Private Key: {private_key}")
                print(f"Address: {address}")
                print(f"Balance: {format_balance(balance)} ")
                print()

                if balance > 0:
                    print("Address with balance found!")
                    print(f"Private Key: {private_key}")
                    print(f"Address: {address}")
                    print(f"Balance: {format_balance(balance)} ")

                    with open("funded_addresses.txt", "a") as file:
                        file.write(f"Private Key: {private_key}\nAddress: {address}\nBalance: {format_balance(balance)}\n")
                    print("Funded address saved to funded_addresses.txt")
                    exit()  # Stop the script when a funded address is found

    print("\nFinished!")
