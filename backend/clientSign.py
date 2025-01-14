from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from pathlib import Path
import json


# Get the current script directory
script_dir = Path(__file__).parent

# Path to ABI file
abi_file_path = script_dir.parent / 'blockchain2' / 'artifacts' / 'contracts' / 'EVCharge.sol' / 'EVCharge.json'

# Load ABI from the file
with open(abi_file_path, 'r') as abi_file:
    contract_json = json.load(abi_file)
    abi = contract_json['abi']

# Connect to local Ethereum test network
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))   # hardhat 

# Check if the connection is successful
if w3.is_connected():
    print("Connected to Ethereum network")


contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
contract = w3.eth.contract(address=contract_address, abi=abi)
# Initialize the contract



message_hash = "0xba2f69252868a35c3dc2aec9fc6c9f15017c556005c721dbb42f82bdfd803e78"
message_hash = Web3.to_bytes(hexstr=message_hash)

angsing = "0x676f2d4274f12539704b8d2c1f6e7e6dedee330c0e5bad62616f3b0b3c8ef534032b967e02fa96ac266473c9000546a0bc00d07b2c33845fc450d26aa76027431b"
message_bytes = Web3.to_bytes(hexstr=angsing)

# Send the data to the contract
tx = contract.functions.getSigner(message_hash, message_bytes).call({
    'from': w3.eth.accounts[0]  # Replace with the sender's address
})

print(f"Transaction sent: {tx}")
