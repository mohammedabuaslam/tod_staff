import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz


class Category(models.Model):
    """Product categories for leads"""
    CATEGORY_CHOICES = [
        ('sofa', 'Sofa'),
        ('bed', 'Bed'),
        ('recliner', 'Recliner'),
        ('sofa_cum_bed', 'Sofa Cum Bed'),
    ]
    
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class Product(models.Model):
    """Products within categories"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, help_text="Product name")
    description = models.TextField(blank=True, null=True, help_text="Product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Product price")
    is_active = models.BooleanField(default=True, help_text="Whether the product is currently available")
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.get_name_display()} - {self.name}"

class Lead(models.Model):
    LEAD_SOURCE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('website', 'Website'),
    ]
    
    LEAD_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('customer', 'Customer'),
    ]
    
    LEAD_STAGE_CHOICES = [
        ('cold_follow_up', 'Cold Follow Up'),
        ('warm_follow_up', 'Warm Follow Up'),
        ('factory_visit', 'Factory Visit'),
        ('production', 'Production'),
        ('delivered', 'Delivered'),
        ('not_fit', 'Not Fit'),
    ]

    lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    leadsource = models.CharField(max_length=20, choices=LEAD_SOURCE_CHOICES, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    number = models.CharField(max_length=15, blank=True, null=True, help_text="Phone number")
    whatsapp_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    lead_status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='active')
    lead_stage = models.CharField(max_length=20, choices=LEAD_STAGE_CHOICES, default='cold_follow_up')
    activity = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    lead_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='managed_leads')
    interested_categories = models.CharField(max_length=500, blank=True, null=True)
    task = models.CharField(max_length=500, blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='leads', help_text="Product categories this lead is interested in")
    products_data = models.JSONField(default=dict, blank=True, help_text="Products data stored as JSON")

    class Meta:
        ordering = ['-created_date']
        
    def __str__(self):
        return f"{self.name or 'Unknown'} - {self.get_lead_status_display()}"
    
    def get_whatsapp_link(self):
        """Generate WhatsApp link from phone number"""
        if self.number:
            # Remove any non-digit characters and format for WhatsApp
            clean_number = ''.join(filter(str.isdigit, self.number))
            if clean_number:
                # Add +91 if it doesn't start with country code
                if not clean_number.startswith('91') and len(clean_number) == 10:
                    clean_number = '91' + clean_number
                elif clean_number.startswith('0'):
                    clean_number = '91' + clean_number[1:]
                return f"https://wa.me/+{clean_number}"
        return self.whatsapp_url or "#"
    
    def save(self, *args, **kwargs):
        """Override save to auto-generate WhatsApp URL"""
        if self.number and not self.whatsapp_url:
            # Auto-generate WhatsApp URL from phone number
            clean_number = ''.join(filter(str.isdigit, self.number))
            if clean_number:
                if not clean_number.startswith('91') and len(clean_number) == 10:
                    clean_number = '91' + clean_number
                elif clean_number.startswith('0'):
                    clean_number = '91' + clean_number[1:]
                self.whatsapp_url = f"https://wa.me/+{clean_number}"
        super().save(*args, **kwargs)
    
    def get_ist_created_date(self):
        """Convert created_date to IST"""
        ist = pytz.timezone('Asia/Kolkata')
        if timezone.is_naive(self.created_date):
            utc_date = timezone.make_aware(self.created_date, timezone.utc)
        else:
            utc_date = self.created_date
        return utc_date.astimezone(ist)
    
    def get_products_summary(self):
        """Get a summary of products from JSON data"""
        if not self.products_data:
            return "No products"
        
        total_products = 0
        categories = []
        
        for category_id, category_data in self.products_data.items():
            category_name = category_data.get('category_name', 'Unknown')
            products_count = len(category_data.get('products', []))
            if products_count > 0:
                categories.append(f"{category_name} ({products_count})")
                total_products += products_count
        
        if total_products == 0:
            return "No products"
        
        return f"{total_products} products: {', '.join(categories)}"
    
    def get_products_by_category(self):
        """Get products organized by category from JSON data"""
        if not self.products_data:
            return {}
        
        result = {}
        for category_id, category_data in self.products_data.items():
            result[category_data.get('category_name', 'Unknown')] = category_data.get('products', [])
        
        return result


class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('call', 'Call'),
        ('note', 'Note'),
        ('task', 'Task'),
        ('purchase', 'Purchase'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField(help_text="Description of the activity")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_activities')
    created_date = models.DateTimeField(default=timezone.now)
    
    # Call recording field
    recording = models.FileField(
        upload_to='Call Recordings/', 
        blank=True, 
        null=True, 
        help_text="Call recording file (for call activities only)"
    )
    
    # Task-specific fields
    due_date = models.DateTimeField(blank=True, null=True, help_text="Due date for tasks (IST)")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, null=True, help_text="Priority for tasks")
    is_completed = models.BooleanField(default=False, help_text="Whether the task is completed")

    class Meta:
        ordering = ['-created_date']
        
    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.lead.name or 'Unknown'} - {self.created_date.strftime('%Y-%m-%d')}"
    
    def get_ist_created_date(self):
        """Convert created_date to IST"""
        ist = pytz.timezone('Asia/Kolkata')
        if timezone.is_naive(self.created_date):
            utc_date = timezone.make_aware(self.created_date, timezone.utc)
        else:
            utc_date = self.created_date
        return utc_date.astimezone(ist)
    
    def get_ist_due_date(self):
        """Convert due_date to IST"""
        if self.due_date:
            ist = pytz.timezone('Asia/Kolkata')
            if timezone.is_naive(self.due_date):
                utc_date = timezone.make_aware(self.due_date, timezone.utc)
            else:
                utc_date = self.due_date
            return utc_date.astimezone(ist)
        return None
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.activity_type == 'task' and self.due_date and not self.is_completed:
            return timezone.now() > self.due_date
        return False
    
    def save(self, *args, **kwargs):
        """Override save to handle call recording naming"""
        if self.recording and self.activity_type == 'call':
            # Generate custom filename: customername__currenttime
            customer_name = self.lead.name or 'Unknown'
            # Replace spaces and special characters with underscores
            customer_name = ''.join(c if c.isalnum() else '_' for c in customer_name)
            
            # Get current timestamp
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            
            # Get file extension
            file_ext = self.recording.name.split('.')[-1] if '.' in self.recording.name else 'mp3'
            
            # Create new filename
            new_filename = f"{customer_name}__{timestamp}.{file_ext}"
            
            # Update the file field with new name
            self.recording.name = f"Call Recordings/{new_filename}"
        
        super().save(*args, **kwargs)


class TaskNote(models.Model):
    """Notes added to tasks"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='notes', limit_choices_to={'activity_type': 'task'})
    note = models.TextField(help_text="Note content")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_notes')
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"Note for {self.activity} - {self.created_date.strftime('%Y-%m-%d')}"
    
    def get_ist_created_date(self):
        """Convert created_date to IST"""
        ist = pytz.timezone('Asia/Kolkata')
        if timezone.is_naive(self.created_date):
            utc_date = timezone.make_aware(self.created_date, timezone.utc)
        else:
            utc_date = self.created_date
        return utc_date.astimezone(ist)


class LeadProduct(models.Model):
    """Products associated with a lead"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='lead_products')
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of this product")
    notes = models.TextField(blank=True, null=True, help_text="Notes about this product for this lead")
    price_quoted = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price quoted to customer")
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['lead', 'product']
        ordering = ['product__category', 'product__name']
    
    def __str__(self):
        return f"{self.lead.name} - {self.product.name} (x{self.quantity})"
