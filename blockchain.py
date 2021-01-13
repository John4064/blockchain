import json
from time import time
from urllib.parse import urlparse
import requests
import hashlib as h
class Blockchain(object):
    # Constructor
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        #set of nodes to verify we have the right chain
        #We use a set to prevent duplicates no matter what
        self.nodes = set()
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)


    def register_node(self,address):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Ex. 'https://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self,chain):
        """
        Determine if the given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if Valid, False if not
        """

        last_block = chain[0]
        current_index =1

        #Go from the index to the max element in chain and checks if hash is accurate
        #Also checks proof of work is good
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            #Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False
            #This is the check for the proof of work is accurate
            if not self.valid_proof(last_block['proof'], block ['proof']):
                return False
            last_block = block
            current_index +=1
        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        neighbors = self.nodes
        new_chain = None

        #We're only looking for chains longer than ours
        max_length = len(self.chain)

        #Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                #check if the length is longer and the chain is valid
                if length> max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        #replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True
        return False

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
        Validates the Proof: Does hash(last,proof, proof) contain 4 leading zeros?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True is correct, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = h.shake_128(guess).hexdigest(128)
        return guess_hash[:4] == "0000"
