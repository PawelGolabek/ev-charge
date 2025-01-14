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


server_public_key = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
server_private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"


# Signing details
message = "Your message here"
encoded_message = encode_defunct(text=message)

# Sign the message
signed_message = Account.sign_message(encoded_message, private_key=server_private_key)

# Extract v, r, s
v = signed_message.v
r = signed_message.r
s = signed_message.s
message_hash = signed_message.message_hash
from eth_utils import to_bytes

# Convert r, s, v to bytes
r_bytes = to_bytes(r)
s_bytes = to_bytes(s)
v_bytes = to_bytes(v)

# Concatenate into a single bytes array
signature_bytes = r_bytes + s_bytes + v_bytes

# Send the data to the contract
tx = contract.functions.getSigner(message_hash, signature_bytes).call({
    'from': w3.eth.accounts[0]  # Replace with the sender's address
})

print(f"Transaction sent: {tx}")
