from flask import Flask, request
from web3 import Web3, HTTPProvider
from decimal import Decimal
import json
from os import environ
from dotenv import load_dotenv

load_dotenv()

SK = environ.get('SK')
CONTRACT_ADDRESS = environ.get('CONTRACT_ADDRESS')
FAUCET_ABI = json.loads(environ.get('FAUCET_ABI'))
CHAIN_ID=int(environ.get('CHAIN_ID'))
GAS_LIMIT=int(environ.get('GAS_LIMIT'))
GWEI_PRICE=environ.get('GWEI_PRICE')

w3 = Web3(HTTPProvider('http://127.0.0.1:8545'))
account = w3.eth.account.privateKeyToAccount(SK)

oneEth = Decimal('1000000000000000000')

app = Flask(__name__)

@app.route("/")
def request_eth():
    balance=Decimal(w3.eth.getBalance(CONTRACT_ADDRESS))
    return f"""
Viene utilizzato il contratto all'indirizzo f{CONTRACT_ADDRESS}<br/>
Il bilancio attuale del faucet è {balance/oneEth} eth<br/>
<form method="GET" action="/faucet">
    <input type="text" name="address">
    <input type="submit" value="Send request">
</form>
"""


@app.route("/faucet")
def faucet_send():
    address = request.args['address']

    if address[0:2] != "0x":
        address = '0x' + address

    faucetContract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=FAUCET_ABI)
    nonce = w3.eth.getTransactionCount(account.address)
    transfer_tx = faucetContract.functions.transfer(address).buildTransaction({
        'chainId': CHAIN_ID,
        'from': account.address,
        'gas': GAS_LIMIT,
        'gasPrice': w3.toWei(GWEI_PRICE, 'gwei'),
        'nonce': nonce,
    })
    signed = account.signTransaction(transfer_tx)
    txid=w3.eth.sendRawTransaction(signed.rawTransaction).hex()
    return f"{txid}"
