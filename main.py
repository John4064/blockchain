import hashlib as h
import json
from time import time
from uuid import uuid4
from flask import Flask


class Blockchain(object):
    # Constructor
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def proof_of_work(self,last_proof):
        """
        Simple Proof of Work Algorithm
        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof:
        :return: <int>
        """
        proof=0
        while self.valid_proof(last_proof,proof) is False:
            proof+=1
        return proof
    @staticmethod
    def valid_proof(last_proof,proof):
        """
        Validates the Proof: Does hash(last,proof, proof) contain 4 leadding zeros?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True is correct, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = h.shake_128(guess).hexdigest(128)
        return guess_hash[:4] == "0000"
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    # For a new transaction what happens
    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        # Current transactions is a list defined above
        # pretty self explanatory stuff
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a block
        :param block: <dict> Block
        :return: <str>
        """
        #double checks the dictionary is properly ordered or else inconsistent hashes
        block_string = json.dumps(block,sort_keys=True).encode()
        return h.shake_128(block_string).hexdigest(128)
    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.chain[-1]

app = Flask(__name__)

#Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')
#instantiate the blockchain
blockchain= Blockchain()
@app.route('/mine', methods=['GET'])
def mine():
    #we run the proof of work algorithm to get the next proof
    #This is saved in blockchain with the blocks similar
    #to a linked list with head and tail and they're linked to next one
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #We must receive a reward for find the proof
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = Flask.request.get_json()
    #Makes sure all fields have values in them
    required = ['sender','recipient','amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block{index}'}
    return Flask.jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length' : len(blockchain.chain),
    }
    return Flask.jsonify(response), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



def gunk():
    myH = h.shake_128(b"Dan")
    print(myH.digest(128))
    print(h.algorithms_available)
    x = 5
    y = 0  # We don't know what y should be yet...
    while h.shake_128(f'{x * y}'.encode()).hexdigest(128)[-1] != "0":
        y += 1
    print(f'The solution is y = {y}')
    return
