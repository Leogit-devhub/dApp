
import hashlib
from os import path
from urllib.request import urlopen


def hash_file(file_path):
  if not path.isfile(file_path):
    raise Exception("File not found for hash operation")

  hash = hashlib.sha256()

  with open(file_path,'rb') as file:
    chunk = 0
    while chunk != b'':
      # read only 1024 bytes at a time
      chunk = file.read(1024)
      hash.update(chunk)
        
  return hash.hexdigest()
 

def get_remote_hash(url,algorithm):
	remote = urlopen(url)
	return hash(remote, algorithm)

def hash(remote, algorithm="sha256"):
	max_file_size=100*1024*1024
	if algorithm=="md5":
		hash = hashlib.md5()
	elif algorithm=="sha1":
		hash = hashlib.sha1()
	elif algorithm=="sha256":
		hash = hashlib.sha256()
	elif algorithm=="sha384":
		hash = hashlib.sha384()
	elif algorithm=="sha512":
		hash = hashlib.sha512()

	total_read = 0
	while True:
		data = remote.read(4096)
		total_read += 4096

		if not data or total_read > max_file_size:
			break

		hash.update(data)

	return hash.hexdigest()
