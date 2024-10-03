import hashlib
import time
import socket
import threading
import json

# Class giao dịch
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"

# Class khối
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

# Class Blockchain
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.balances = {}

    def create_genesis_block(self):
        # Tạo khối đầu tiên
        return Block(0, [], "0")

    def add_transaction(self, transaction):
        # Thêm giao dịch
        sender_balance = self.balances.get(transaction.sender, 0)
        if sender_balance >= transaction.amount:
            self.pending_transactions.append(transaction)
            self.balances[transaction.sender] = sender_balance - transaction.amount
            self.balances[transaction.receiver] = self.balances.get(transaction.receiver, 0) + transaction.amount
        else:
            print(f"Giao dịch không hợp lệ: {transaction.sender} không đủ số dư.")

    def mine_block(self):
        # Tạo khối mới
        if len(self.pending_transactions) == 0:
            return
        block = Block(len(self.chain), self.pending_transactions, self.chain[-1].hash)
        self.chain.append(block)
        self.pending_transactions = []

    def get_chain(self):
        return self.chain

# Class Node - Tạo một node trong mạng
class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.blockchain = blockchain
        self.peers = []  # Các peers kết nối với node này

    def start(self):
        # Khởi động server cho node
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Node đang lắng nghe tại {self.host}:{self.port}")

        # Thread lắng nghe các kết nối từ peers
        threading.Thread(target=self.listen_for_peers, args=(server,)).start()

    def listen_for_peers(self, server):
        while True:
            client_socket, addr = server.accept()
            print(f"Node kết nối từ: {addr}")
            threading.Thread(target=self.handle_peer, args=(client_socket,)).start()

    def handle_peer(self, client_socket):
        # Nhận dữ liệu từ peer
        try:
            data = client_socket.recv(1024)
            message = json.loads(data.decode())
            if message['type'] == 'transaction':
                self.handle_transaction(message['data'])
            elif message['type'] == 'block':
                self.handle_block(message['data'])
        except Exception as e:
            print(f"Lỗi xử lý peer: {e}")

    def handle_transaction(self, tx_data):
        # Nhận giao dịch từ peer
        transaction = Transaction(tx_data['sender'], tx_data['receiver'], tx_data['amount'])
        self.blockchain.add_transaction(transaction)
        print(f"Giao dịch mới được nhận: {transaction}")

    def handle_block(self, block_data):
        # Nhận khối mới từ peer
        block = Block(block_data['index'], block_data['transactions'], block_data['previous_hash'])
        print(f"Khối mới được nhận: {block.hash}")
        self.blockchain.chain.append(block)

    def connect_to_peer(self, peer_host, peer_port):
        # Kết nối đến một peer khác
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_host, peer_port))
            self.peers.append(peer_socket)
            print(f"Kết nối đến peer tại {peer_host}:{peer_port}")
        except Exception as e:
            print(f"Không thể kết nối đến peer: {e}")

    def broadcast_transaction(self, transaction):
        # Gửi giao dịch tới tất cả các peers
        for peer in self.peers:
            try:
                message = {
                    'type': 'transaction',
                    'data': {
                        'sender': transaction.sender,
                        'receiver': transaction.receiver,
                        'amount': transaction.amount
                    }
                }
                peer.sendall(json.dumps(message).encode())
            except Exception as e:
                print(f"Lỗi gửi giao dịch: {e}")

    def broadcast_block(self, block):
        # Gửi khối mới tới tất cả các peers
        for peer in self.peers:
            try:
                message = {
                    'type': 'block',
                    'data': {
                        'index': block.index,
                        'transactions': [str(tx) for tx in block.transactions],
                        'previous_hash': block.previous_hash
                    }
                }
                peer.sendall(json.dumps(message).encode())
            except Exception as e:
                print(f"Lỗi gửi khối: {e}")

    def start_mining(self):
        while True:
            self.blockchain.mine_block()
            latest_block = self.blockchain.get_chain()[-1]
            self.broadcast_block(latest_block)
            time.sleep(10)  # Điều chỉnh thời gian nghỉ giữa các lần khai thác

# Chạy node
blockchain = Blockchain()
node = Node("127.0.0.1", 5000, blockchain)
node.start()

# Bắt đầu quá trình mining trong một thread riêng
threading.Thread(target=node.start_mining).start()

# Thêm giao dịch và gửi đến các peers
transaction1 = Transaction("Alice", "Bob", 10)
blockchain.add_transaction(transaction1)
node.broadcast_transaction(transaction1)
