
import hashlib
from django.db import models
from django.urls import reverse
from django.utils import timezone
from blockchain.models import Blockchain
# from gdstorage.storage import GoogleDriveStorage

from helpers._func import hash_file

# gd_storage = GoogleDriveStorage()

def get_upload_path(instance, file):
  file_name_list = file.split('.')[:-1]
  ext = file.split('.')[-1]
  file_name = '.'.join(file_name_list)

  return 'update/{0}.{1}'.format(file_name, ext)


class Block(models.Model):
  id_2        = models.IntegerField(editable=False, default=0)
  version     = models.CharField(max_length=10, help_text="X.X.X")
  title       = models.CharField(max_length=120, )
  description = models.TextField()
  file        = models.FileField(upload_to=get_upload_path,) # Transactions in block
  prev_hash   = models.CharField(max_length=64, null=True, blank=True)
  nonce       = models.IntegerField()
  blockchain  = models.ForeignKey(Blockchain, related_name="blocks", on_delete=models.CASCADE)
  updated_from = models.CharField(max_length=120, null=True, blank=True)
  confirmed   = models.BooleanField(default=True, editable=False)
  time_stamp  = models.DateTimeField(editable=False, default=timezone.now)
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['id_2', 'blockchain'], name='unique blocks for blockchain'),
      models.UniqueConstraint(fields=['version', 'blockchain'], name='unique versions for blockchain')
    ]
  
  def save(self, *args, **kwargs):
    if not self.pk:
      prev_block = Block.objects.filter(blockchain=self.blockchain.pk).order_by("pk").last()
      print(prev_block)
      if not prev_block: 
        self.id_2 = 1
        self.prev_hash = self.genesis_hash()
      else: 
        self.id_2 = prev_block.id_2 + 1
        self.prev_hash = prev_block.hash()
    super(Block, self).save(*args, **kwargs)
  
  def __str__(self):
    return f"{self.title} - {self.version}"
  
  def get_file_url(self):
    return reverse("block_file", kwargs={"path": self.file.url})
       
  def genesis_hash(self):
    block_string = f"{self.version} {self.title} {self.description} {self.prev_hash} {self.nonce} {self.blockchain.pk}"
    return hashlib.sha256(block_string.encode()).hexdigest()
       
  def compute_hash(self):
    file_hash = self.get_file_hash()
    block_string = f"{self.version} {self.title} {self.description} {self.prev_hash} {self.nonce} {self.blockchain.pk} {file_hash}"
    return hashlib.sha256(block_string.encode()).hexdigest()

  def get_file_hash(self):
    return hash_file(self.file.path)
  
  def hash(self):
    return self.compute_hash()
    
  def get_prev_hash(self):
    return self.prev_hash

    

