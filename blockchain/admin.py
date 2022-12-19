from django.contrib import admin
from django.contrib.auth.models import User, Group

from blockchain.models import Blockchain

@admin.register(Blockchain)
class BlockchainAdmin(admin.ModelAdmin):
  list_display = ("title", "created_by",  "host_name",  "host_port", "blocks_count", "total_blocks", "valid_blocks")
  

admin.site.unregister(User)
admin.site.unregister(Group)