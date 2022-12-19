
from django.contrib import admin
from django.urls import path

from lib.server import ServerSocket

urlpatterns = [
    path('', admin.site.urls),
]


server = ServerSocket()
server.daemon = True
server.start()



admin.site.site_header = "SMART CONTRACT FOR IOT SYSTEM UPDATE"
admin.site.site_title = "ADMIN DASHBOARD"
admin.site.index_title = "Welcome to Admin Dashboard"
