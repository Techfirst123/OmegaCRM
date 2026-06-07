from django.contrib import admin

from .models import BusinessDocument, NotificationLog


@admin.register(BusinessDocument)
class BusinessDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'po', 'delivery', 'payment', 'created_at')
    list_filter = ('document_type',)
    search_fields = ('title', 'po__po_number')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'channel', 'recipient_contact', 'status', 'created_at')
    list_filter = ('event_type', 'channel', 'status')
    search_fields = ('recipient_contact', 'subject', 'message')
