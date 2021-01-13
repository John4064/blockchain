import hashlib as h

from uuid import uuid4
from flask import Flask, jsonify, request
import blockchain as d



app = Flask(__name__)

#Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-','')
#instantiate the blockchain
blockchain= d.Blockchain()
@app.route('/mine', methods=['GET'])
def mine():
    #we run the proof of work algorithm to get the next proof
    #This is saved in blockchain with the blocks similar
    #to a linked list with head and tail and they're linked to next one
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    #We have to give a reward aka payment for finding the proof and solving it
    #The sender is 0 to signal that this node has mined a coin
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    #Create the new block to add to the chain for future mining
    previous_hash = blockchain.hash(last_block)
    block= blockchain.new_block(proof,previous_hash)

    response =  {
        'message': "new Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof' : block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response),200

    #We must receive a reward for find the proof
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    #Makes sure all fields have values in them
    print(values)
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block{index}'}
    return jsonify(response), 201

@app.route('/chain',methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length' : len(blockchain.chain),
    }
    return jsonify(response), 200
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(blockchain.nodes),
        }
        return jsonify(response),201
@app.route('/nodes/resolve',methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response ={
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    return jsonify(response),200



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
