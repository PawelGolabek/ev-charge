from eth_account import Account
from web3 import Web3

# Initialize web3
w3 = Web3()

# Your private key (do not expose in production)
private_key = "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"

# Create account object
account = Account.privateKeyToAccount(private_key)

# Message to be signed
message = "This is a message"

# Convert message to bytes
message_bytes = Web3.toBytes(text=message)

# Sign the message
signed_message = account.sign_message(message_bytes)

# Print the signature and the signed message
print(f"Signature: {signed_message.signature.hex()}")
print(f"Message Hash: {signed_message.messageHash.hex()}")
