from django.contrib import admin
from .models import Lead, Activity, TaskNote, Category, Product, LeadProduct

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
            'fields': ('leadsource', 'lead_status', 'lead_stage', 'lead_manager', 'budget', 'categories')
        }),
        ('Additional Information', {
            'fields': ('activity', 'interested_product_url', 'task', 'notes', 'remarks', 'created_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead_manager')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'activity_type', 'description', 'created_by', 'created_date', 'due_date', 'priority', 'is_completed', 'recording')
    list_filter = ('activity_type', 'priority', 'is_completed', 'created_date', 'due_date', 'created_by')
    search_fields = ('lead__name', 'description', 'created_by__username')
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('lead', 'activity_type', 'description', 'recording', 'created_by', 'created_date')
        }),
        ('Task Details', {
            'fields': ('due_date', 'priority', 'is_completed'),
            'description': 'These fields are only relevant for task-type activities.'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead', 'created_by')


@admin.register(TaskNote)
class TaskNoteAdmin(admin.ModelAdmin):
    list_display = ('activity', 'note', 'created_by', 'created_date')
    list_filter = ('created_date', 'created_by')
    search_fields = ('activity__description', 'note', 'created_by__username')
    readonly_fields = ('created_date',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('activity', 'created_by')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('name',)
    readonly_fields = ('created_date',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'created_date')
    list_filter = ('category', 'is_active', 'created_date')
    search_fields = ('name', 'description', 'category__name')
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Product Information', {
            'fields': ('category', 'name', 'description', 'is_active', 'created_date')
        }),
        ('Pricing', {
            'fields': ('price',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(LeadProduct)
class LeadProductAdmin(admin.ModelAdmin):
    list_display = ('lead', 'product', 'quantity', 'price_quoted', 'created_date')
    list_filter = ('product__category', 'created_date')
    search_fields = ('lead__name', 'product__name', 'notes')
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Association', {
            'fields': ('lead', 'product', 'quantity', 'created_date')
        }),
        ('Details', {
            'fields': ('price_quoted', 'notes'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lead', 'product', 'product__category')
