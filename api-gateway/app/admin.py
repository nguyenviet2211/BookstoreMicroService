from django.contrib import admin
from .models import GatewayUser, RequestLog, RateLimitEntry

admin.site.register(GatewayUser)
admin.site.register(RequestLog)
admin.site.register(RateLimitEntry)
