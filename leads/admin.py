from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'email', 'lead_status', 'lead_stage', 'leadsource', 'pincode', 'created_date', 'lead_manager')
    list_filter = ('lead_status', 'lead_stage', 'leadsource', 'created_date', 'lead_manager')
    search_fields = ('name', 'email', 'number', 'pincode')
    readonly_fields = ('lead_id', 'created_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lead_id', 'name', 'email', 'number', 'whatsapp_url', 'address', 'pincode')
        }),
        ('Lead Management', {
            'fields': ('leadsource', 'lead_status', 'lead_stage', 'lead_manager', 'budget', 'interested_categories')
        }),
        ('Additional Information', {
            'fields': ('activity', 'interested_product_url', 'task', 'notes', 'remarks', 'created_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead_manager')
