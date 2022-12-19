import os
import platform
import socket
from ast import literal_eval
from _thread import start_new_thread
import threading
from helpers._func import hash_file
from blockchain.models import Blockchain
from config import settings

class ServerSocket(threading.Thread):
  def __init__(self) -> None:
    super(ServerSocket, self).__init__()
    self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    self.host = ''
    self.port = 3333
    self.conn_clients = []
    try:
      self.server.bind((self.host, self.port))
    except socket.error as e:
      print(str(e))
  
  def run(self):
    self.server.listen()   
    while True:
      conn, address = self.server.accept()
      start_new_thread(self.client_thread, (conn, address))

  def client_thread(self, conn, address):
    conn.sendall(self.send_initials().encode('utf-8'))
    client_init = (conn.recv(2048)).decode('utf-8')
    if client_init.startswith("$get_file"):
      client_init = literal_eval(client_init.split(' ^ ')[1])
      self.send_file(conn, client_init)
    else: 
      client_init = literal_eval(client_init)
      init = {
        'id': address[1],
        'uptodate': client_init.get('uptodate') or False,
        'serving': client_init.get('serving') or False,
        'ip': client_init.get('ip') or None,
        'name': client_init.get('name') or None,
        'port': client_init.get('port') or None,
      }
      if not init in self.conn_clients:
        self.conn_clients.append(init)
        print(self.conn_clients)
    while True:
      request = (conn.recv(2048).decode('utf-8')).split(' ^ ')
      if not request[0] or request[0] == "$q":
        conn.close()
        break
      command, request = request[0], literal_eval(request[1]) 
      if command == "$uptodate":
        for client in self.conn_clients:
          if client['id'] == address[1]:
            client['uptodate']= True
      elif command =="$updated_clients":
        conn.sendall(self.uptodate_clients().encode('utf-8'))
      elif command == "$init_update":
        conn.sendall(self.send_init_update(request).encode('utf-8'))
      elif command == "$get_update":
        conn.sendall(self.send_update(request).encode('utf-8'))
      elif command == "$get_file":
        self.send_file(conn, request)
      elif command == "$serve_request":
        conn.sendall(self.serve_request(request).encode('utf-8'))
      elif command == "$get_hashes":
        conn.sendall(self.hashes(request).encode('utf-8'))
      else: conn.sendall(self.send_initials().encode('utf-8'))  
      
  def send_initials(self):
    response = [self.conn_clients]
    for blockchain in Blockchain.objects.all():
      first_block = blockchain.confirmed_blocks().first()
      last_block = blockchain.confirmed_blocks().last()
      if first_block and last_block:
        response.append({
          "chain": [blockchain.pk, blockchain.title, blockchain.created_by],
          "first_block":[first_block.id_2, first_block.hash(), first_block.prev_hash], 
          "last_block":[last_block.id_2, last_block.hash(), last_block.prev_hash],
          'blocks_count':blockchain.confirmed_blocks().count()
        })
    return str(response)
  
  def uptodate_clients(self):
    response = []
    for client in self.conn_clients:
      if client.get('uptodate') == True:
        response.append(client)
    return str(response)
    
  def send_init_update(self, request):
    response = []
    try:
      blockchain = Blockchain.objects.get(pk=request[0], title=request[1], created_by=request[2])
    except Blockchain.DoesNotExist:
      return str(response)
    for block in blockchain.confirmed_blocks():
      response.append({
        "blockchain_id": blockchain.pk, 
        "version":block.version, 
        "title": block.title, 
        "description":block.description, 
        "nonce":block.nonce, 
        "updated_from":f"{platform.node()}-{self.host}", 
        "file": block.file.url,
        "file_hash": block.get_file_hash(),
        "hash": block.hash(),
      })
    return str(response)
  
  # Send update to client &&& Done
  def send_update(self, request):
    response = []
    chain = request.get('chain')
    first_block = request.get('first_block')
    last_block = request.get('last_block')
    try:
      blockchain = Blockchain.objects.get(pk=chain[0], title=chain[1], created_by=chain[2])
    except Blockchain.DoesNotExist:
      return str(response)
    if not (blockchain.blocks.first().hash() == first_block[1] and blockchain.blocks.first().prev_hash == first_block[2]):
      return str(response)
    for block in blockchain.confirmed_blocks().filter(id_2__gt = last_block[0]):
      if not (block.prev_hash == last_block[1]):
        continue
      response.append({
        "blockchain_id": blockchain.pk, 
        "version":block.version, 
        "title": block.title, 
        "description":block.description, 
        "nonce":block.nonce, 
        "updated_from":f"{self.host}-{platform.node()}", 
        "file": block.file.url,
        "file_hash": block.get_file_hash(),
        "hash": block.hash(),
      })
    return str(response)
  
  def hashes(self, request):
    response = []
    try:
      blockchain = Blockchain.objects.get(pk=request[0], title=request[1], created_by=request[2])
    except Blockchain.DoesNotExist:
      return str(response)
    for block in blockchain.confirmed_blocks():
      response.extend([block.hash(), block.prev_hash])
    return str(response)
   
  def send_file(self, conn, request):
    url = request[0].replace('/', '\\')
    file_dir = str(settings.BASE_DIR) + url
    if not os.path.isfile(file_dir):
      conn.send("".encode('utf-8'))
      return
    if not request[1] == hash_file(file_dir):
      conn.send("".encode('utf-8'))
      return 
    
    file_size = os.path.getsize(file_dir)
    response = "$filesize...; {0}".format(file_size)
    conn.send(response.encode('utf-8'))
    
    with open(file_dir, 'rb') as file:
      conn.sendall(file.read())
     
  def serve_request(self, request):
    
    return


if __name__ == "__main__":
  server = ServerSocket()