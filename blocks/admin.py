from django.contrib import admin

from blocks.models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
  list_display = ( "hash", "title", "version", "nonce", "blockchain", "confirmed", )
  readonly_fields = ("prev_hash", "updated_from",)
  