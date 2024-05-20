import csv
import requests
from web3 import Web3

# Initialize the endpoint URL for the Polygon mainnet
node_url = "https://polygon-rpc.com"
# Uncomment the following line to use the Mumbai testnet instead
# node_url = "https://rpc-mumbai.maticvigil.com"

# Establish a connection to the node
web3 = Web3(Web3.HTTPProvider(node_url))

# Check if the connection to the node is successful
if web3.isConnected():
    print("-" * 50)
    print("Connection Successful")
    print("-" * 50)
else:
    print("Connection Failed")

# Define the address that will call the functions and sign the transactions
caller = "0xA000000000000000000000000000000000000000"
# Private key for signing the transactions (ensure this is kept secure)
private_key = "0000000000000000000000000000000000000000000000000000000000000000"

# Define the contract ABI and address
abi = '[ { "inputs": [], "stateMutability": "nonpayable", ............... "type": "function" } ]'
contract_address = "0xA000000000000000000000000000000000000000"

# Create an instance of the smart contract
contract = web3.eth.contract(address=contract_address, abi=abi)

# Retrieve the chain ID, which is required for transaction replay protection
chain_id = web3.eth.chain_id

# Get the transaction count (nonce) for the caller address
nonce = web3.eth.getTransactionCount(caller)

# Open and read the CSV file containing addresses and token IDs for airdrop
with open('drop.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        # Retrieve the current gas prices from the Polygon Gas Station API
        gaspricearr = requests.get('https://gasstation.polygon.technology/v2').json()
        gPrice = int(float(gaspricearr['fast']['maxFee']) * 1e9)  # Convert to Wei

        # Validate the wallet address format and correct it if necessary
        if web3.is_checksum_address(row[0]):
            toAddress = row[0]
        else:
            toAddress = web3.to_checksum_address(row[0])

        # Build the transaction for the safeMint function call
        call_function = contract.functions.safeMint(toAddress, row[1]).buildTransaction({
            "chainId": chain_id, 
            "from": caller, 
            "gas": 1000000, 
            "gasPrice": gPrice,  # Use 21000000000 for Mumbai testnet
            "nonce": nonce
        })
        nonce += 1  # Increment the nonce for the next transaction

        # Sign the transaction with the private key
        signed_tx = web3.eth.account.sign_transaction(call_function, private_key=private_key)

        # Send the signed transaction to the network
        send_tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Wait for the transaction receipt to confirm the transaction was processed
        tx_receipt = web3.eth.wait_for_transaction_receipt(send_tx)
        print(tx_receipt)  # Optionally print the transaction receipt