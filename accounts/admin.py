from django.contrib import admin
from .models import CustomUser, LinkedAccount

class LinkedAccountAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user1__username', 'user2__username')

admin.site.register(LinkedAccount, LinkedAccountAdmin)
