import hashlib
import time

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = time.time()
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # Tạo mã hash cho khối
        block_string = f"{self.index}{[str(tx) for tx in self.transactions]}{self.timestamp}{self.previous_hash}".encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        # Tạo khối đầu tiên trong chuỗi
        return Block(0, [], "0")

    def add_transaction(self, transaction):
        # Thêm giao dịch vào danh sách chờ
        self.pending_transactions.append(transaction)

    def mine_block(self):
        # Tạo khối mới từ các giao dịch chờ
        block = Block(len(self.chain), self.pending_transactions, self.chain[-1].hash)
        self.chain.append(block)
        self.pending_transactions = []  # Xóa các giao dịch đã được thêm vào khối

    def get_chain(self):
        return self.chain

# Sử dụng Blockchain
blockchain = Blockchain()

# Thêm giao dịch
transaction1 = Transaction("Alice", "Bob", 10)
transaction2 = Transaction("Bob", "Charlie", 5)

blockchain.add_transaction(transaction1)
blockchain.add_transaction(transaction2)

# Khai thác khối mới
blockchain.mine_block()

# Hiển thị thông tin chuỗi
for block in blockchain.get_chain():
    print(f"Block {block.index} Hash: {block.hash}")
    for tx in block.transactions:
        print(f"  {tx}")