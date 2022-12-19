
import platform
from django.db import models


class Blockchain(models.Model):
  title       = models.CharField(max_length=120, )
  host_name   = models.CharField(max_length=60, default=platform.node())
  host_port   = models.SmallIntegerField(default=2004)
  created_by  = models.CharField(max_length=120)
  mined_points = models.IntegerField(default=0, editable=False)
  date_created  = models.DateTimeField(auto_now_add=True, auto_now=False)

  def __str__(self):
    return f"{self.title} - {self.created_by}"
  
  def confirmed_blocks(self):
    return self.blocks.filter(confirmed = True)
  
  def blocks_count(self):
    return self.confirmed_blocks().count()
  
  def unconfirmed_blocks(self):
    return self.blocks.filter(confirmed = False)
  
  def total_blocks(self):
    return self.unconfirmed_blocks().count()

  def valid_blocks(self):
    blocks = self.blocks.all().order_by('time_stamp')
    if blocks.first():
      prev_hash = blocks.first().prev_hash
      for block in blocks:
        if not block.prev_hash:
          return False
        if block.prev_hash != prev_hash:
          return False
        prev_hash = block.hash()
      
    return True
  
  