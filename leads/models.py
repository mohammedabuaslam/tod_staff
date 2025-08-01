import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

class Lead(models.Model):
    LEAD_SOURCE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('website', 'Website'),
    ]
    
    LEAD_STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
        ('on_hold', 'On Hold'),
    ]
    
    LEAD_STAGE_CHOICES = [
        ('prospect', 'Prospect'),
        ('lead', 'Lead'),
        ('opportunity', 'Opportunity'),
        ('customer', 'Customer'),
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
    lead_status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    lead_stage = models.CharField(max_length=20, choices=LEAD_STAGE_CHOICES, default='prospect')
    activity = models.CharField(max_length=500, blank=True, null=True)
    interested_product_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    lead_manager = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='managed_leads')
    budget = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    interested_categories = models.CharField(max_length=500, blank=True, null=True)
    task = models.CharField(max_length=500, blank=True, null=True)

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
    
    def get_ist_created_date(self):
        """Convert created_date to IST"""
        ist = pytz.timezone('Asia/Kolkata')
        if timezone.is_naive(self.created_date):
            utc_date = timezone.make_aware(self.created_date, timezone.utc)
        else:
            utc_date = self.created_date
        return utc_date.astimezone(ist)
