from web3 import Web3
import json
import os
from pathlib import Path
import random
import time

# Get the current script directory
script_dir = Path(__file__).parent

# Go up one directory and then to 'blockchain'
abi_file_path = script_dir.parent / 'blockchain' / 'artifacts' / 'contracts' / 'TransactionVerifier.sol' / 'TransactionVerifier.json'

print(abi_file_path)

# Load ABI from the file
with open(abi_file_path, 'r') as abi_file:
    contract_json = json.load(abi_file)
    abi = contract_json['abi']


# Connect to local Ethereum test network
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Check if the connection is successful
if w3.is_connected():
    print("Connected to Ethereum network")

# Set the deployed contract address and ABI
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
contract = w3.eth.contract(address=contract_address, abi=abi)

# Set default account for transactions
w3.eth.default_account = w3.eth.accounts[0]  # Use an account from the local node


def submit_transaction(tx_id, amount):
    tx_hash = contract.functions.submitTransaction(tx_id, amount).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction submitted: {tx_hash.hex()}")


def verify_transaction(tx_id):
    tx_hash = contract.functions.verifyTransaction(tx_id).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Transaction verified: {tx_hash.hex()}")


def get_all_transactions():
    try:
        transactions = contract.functions.getAllTransactions().call()
        print("Retrieved transactions:")
        if not transactions:
            print("No transactions found.")
            return
        for i, txn in enumerate(transactions):
            # Assuming the struct has the following fields: sender, amount, exists, verified
            print(f"Transaction {i + 1}: Sender={txn[0]}, Amount={txn[1]}, Exists={txn[2]}, Verified={txn[3]}")
    except Exception as e:
        print(f"An error occurred while retrieving transactions: {e}")



if __name__ == "__main__":

    random.seed(time.time())
    random1 = random.random()
    submit_transaction("tx" + str(random1), 1000)

    verify_transaction("tx" + str(random1))

    get_all_transactions()
    os.system("pause")

