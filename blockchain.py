import hashlib
import time
import json
import os
import threading

class Block:
    def __init__(self, index, previous_hash, data, timestamp=None, nonce=0):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.data = data
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.previous_hash}{self.data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash})"

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block")

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        if new_block.previous_hash == self.get_last_block().hash:
            self.chain.append(new_block)

    def mine_new_block(self, data='New Block'):
        last_block = self.get_last_block()
        new_block = Block(index=last_block.index + 1,
                          previous_hash=last_block.hash,
                          data=data)
        new_block.nonce = 0
        while not new_block.hash.startswith('000'):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()
        self.add_block(new_block)
        return new_block

class Node:
    def __init__(self, blockchain, node_id):
        self.blockchain = blockchain
        self.node_id = node_id
        self.broadcast_file = f"broadcast_{node_id}.json"

    def mine_block(self):
        new_block = self.blockchain.mine_new_block(data=f"Block mined by Node {self.node_id}")
        print(f"Mined a new block: {new_block}")
        self.broadcast_new_block(new_block)

    def broadcast_new_block(self, block):
        with open(self.broadcast_file, 'w') as file:
            file.write(json.dumps(block.__dict__))

    def check_for_broadcasts(self, other_node_id):
        broadcast_file = f"broadcast_{other_node_id}.json"
        if os.path.exists(broadcast_file):
            with open(broadcast_file, 'r') as file:
                block_data = json.load(file)
                block = Block(block_data['index'],
                              block_data['previous_hash'],
                              block_data['data'],
                              block_data['timestamp'],
                              block_data['nonce'])
                if block.hash == block_data['hash'] and block not in self.blockchain.chain:
                    self.blockchain.add_block(block)
                    print(f"Node {self.node_id} added block from Node {other_node_id}: {block}")
            os.remove(broadcast_file)

if __name__ == "__main__":
    node_id = input("Enter node ID (1 or 2): ").strip()
    other_node_id = "1" if node_id == "2" else "2"

    blockchain = Blockchain()
    node = Node(blockchain, node_id)

    def mine_blocks():
        while True:
            node.mine_block()
            time.sleep(5)  # Simulate time taken to mine a block

    def listen_for_blocks():
        while True:
            node.check_for_broadcasts(other_node_id)
            time.sleep(1)  # Check every second for new blocks

    # Start mining and listening in separate threads
    threading.Thread(target=mine_blocks, daemon=True).start()
    threading.Thread(target=listen_for_blocks, daemon=True).start()

    # Keep the main thread alive
    input("Press Enter to exit...\n")
