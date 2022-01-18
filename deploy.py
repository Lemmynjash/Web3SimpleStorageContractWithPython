from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os
load_dotenv()
install_solc("0.7.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)


# Compile our Solidity
compile_sol = compile_standard({
    "language": "Solidity",
    "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
    "settings": {
        "outputSelection": {
            "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
        }
    },
}, solc_version="0.7.0",)

# print(compile_sol) prints the compiled results


with open("compiled_code.json", "w") as file:
    json.dump(compile_sol, file)

# inorder to deploy we need to get the byte code and abi
# get bytecode
bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["Storage"]["evm"]["bytecode"]["object"]
# get abi
abi = compile_sol["contracts"]["SimpleStorage.sol"]["Storage"]["abi"]
# print(abi)

# # want to connect to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
# define the chain ID
chain_id = 1337
my_address = "0x9E1dcdB4E5B8539E0781689dDD9e8A41A7e8dAaD"
# always makesure you add 0x on the private key bcoz python always looks for hexadecimal
private_key = os.getenv("PRIVATE_KEY_LOCAL")


# want to connect to other testnet/mainnet
# w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/9c9c73744aa14e5ab2e6ac6adc702d86"))
# # define the chain ID
# chain_id = 3
# my_address = ""
# # always makesure you add 0x on the private key bcoz python always looks for hexadecimal
# private_key = os.getenv("PRIVATE_KEY_TEST")


# deploy contract with python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)
# if you want to get the number of transactions
nounce = w3.eth.getTransactionCount(my_address)
# print(nounce)

#########################################
# 1. Build a Transaction
# 2. Sign a Transaction
# 3. Send a Transaction
#########################################
# 1. Build a Transaction
transaction = SimpleStorage.constructor().buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id, "from": my_address, "nonce": nounce
})
# print(transaction)
# 2. Sign a Transaction
print("Deploying contract .....")
signed_txt = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)
# 3. Send a Transaction
tx_hash = w3.eth.send_raw_transaction(signed_txt.rawTransaction)
# defining transaction receipt
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Awesome Deployed!!!  ")

# Working with Contract, you need;
# 1. Contract ABI
# 2. Contract Address

simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact (Send a transaction) -> Actually making a state change
# print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())

print("Updating contract .....")
store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price,
     "chainId": chain_id, "from": my_address, "nonce": nounce+1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
print("Awesome Updated!! ")
tx_reciept = w3.eth.wait_for_transaction_receipt(send_store_tx)
print(simple_storage.functions.retrieve().call()) 
