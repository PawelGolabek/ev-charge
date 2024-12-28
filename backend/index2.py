from flask import Flask, request, jsonify
from flask_cors import CORS
from web3 import Web3
import json
from pathlib import Path
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (browser security)

# Get the current script directory
script_dir = Path(__file__).parent

# Path to ABI file
abi_file_path = script_dir.parent / 'blockchain' / 'artifacts' / 'contracts' / 'TransactionVerifier.sol' / 'TransactionVerifier.json'

# Load ABI from the file
with open(abi_file_path, 'r') as abi_file:
    contract_json = json.load(abi_file)
    abi = contract_json['abi']

# Connect to local Ethereum test network
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))   # hardhat 

# Check if the connection is successful
if w3.is_connected():
    print("Connected to Ethereum network")

# Set the deployed contract address and ABI
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
contract = w3.eth.contract(address=contract_address, abi=abi)

# Default account for transactions
w3.eth.default_account = w3.eth.accounts[0]   # hardhat account

@app.route('/submit_transaction', methods=['POST'])
def submit_transaction():
    data = request.json
    tx_id = data.get("tx_id")
    amount = data.get("amount")

    try:
        tx_hash = contract.functions.submitTransaction(tx_id, amount).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"status": "success", "tx_hash": tx_hash.hex()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/verify_transaction', methods=['POST'])
def verify_transaction():
    data = request.json
    tx_id = data.get("tx_id")

    try:
        tx_hash = contract.functions.verifyTransaction(tx_id).transact()
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return jsonify({"status": "success", "tx_hash": tx_hash.hex()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/get_all_transactions', methods=['GET'])
def get_all_transactions():
    try:
        transactions = contract.functions.getAllTransactions().call()
        if not transactions:
            return jsonify({"status": "success", "transactions": []})

        transactions_list = [
            {
                "sender": txn[0],
                "amount": txn[1],
                "exists": txn[2],
                "verified": txn[3]
            }
            for txn in transactions
        ]
        return jsonify({"status": "success", "transactions": transactions_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
