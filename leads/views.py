from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
import pytz
from .models import Lead, Activity, TaskNote, Category, Product, LeadProduct
from django.contrib.auth.models import User
from datetime import datetime
import os

@login_required
def lead_create_view(request: HttpRequest) -> HttpResponse:
    """Create a new lead"""
    if request.method == 'POST':
        # Get form data
        lead = Lead()
        lead.leadsource = request.POST.get('leadsource')
        lead.name = request.POST.get('name')
        lead.email = request.POST.get('email')
        lead.address = request.POST.get('address')
        lead.pincode = request.POST.get('pincode')
        lead.number = request.POST.get('number')
        lead.notes = request.POST.get('notes')
        lead.remarks = request.POST.get('remarks')
        lead.lead_status = request.POST.get('lead_status', 'new')
        lead.lead_stage = request.POST.get('lead_stage', 'prospect')
        lead.interested_product_url = request.POST.get('interested_product_url')
        lead.budget = request.POST.get('budget') or None
        
        # Set lead manager to current user (auto-assigned)
        lead.lead_manager = request.user
        
        # Save the lead first
        lead.save()
        
        # Handle categories (multiselect)
        category_ids = request.POST.getlist('categories')
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            lead.categories.set(categories)
        
        # Handle manual product entries
        for category in Category.objects.all():
            product_name = request.POST.get(f'product_name_{category.id}')
            product_url = request.POST.get(f'product_url_{category.id}')
            product_price = request.POST.get(f'product_price_{category.id}')
            
            if product_name:  # Only create if product name is provided
                # Create or get the product
                product, created = Product.objects.get_or_create(
                    category=category,
                    name=product_name,
                    defaults={
                        'description': f'Product from lead {lead.name or "Unknown"}',
                        'price': float(product_price) if product_price else None,
                        'is_active': True
                    }
                )
                
                # Create the lead-product relationship
                LeadProduct.objects.create(
                    lead=lead,
                    product=product,
                    quantity=1,  # Default quantity
                    notes=f'Product URL: {product_url}' if product_url else None,
                    price_quoted=float(product_price) if product_price else None
                )
        
        messages.success(request, f'Lead "{lead.name or "New Lead"}" has been created successfully!')
        return redirect('leads:lead_detail', lead_id=lead.lead_id)
    
    # Get all categories for the create form
    categories = Category.objects.all().order_by('name')
    
    context = {
        'title': 'Create New Lead',
        'categories': categories,
        'lead_source_choices': Lead.LEAD_SOURCE_CHOICES,
        'lead_status_choices': Lead.LEAD_STATUS_CHOICES,
        'lead_stage_choices': Lead.LEAD_STAGE_CHOICES,
    }
    return render(request, 'leads/lead_create.html', context)

@login_required
def lead_list_view(request: HttpRequest) -> HttpResponse:
    """List all leads with pagination and filtering"""
    leads_queryset = Lead.objects.all()
    
    # Filter by search query
    search_query = request.GET.get('search', '')
    if search_query:
        leads_queryset = leads_queryset.filter(
            name__icontains=search_query
        ) | leads_queryset.filter(
            number__icontains=search_query
        ) | leads_queryset.filter(
            email__icontains=search_query
        ) | leads_queryset.filter(
            pincode__icontains=search_query
        )
    
    # Filter by lead status
    status_filter = request.GET.get('status', '')
    if status_filter:
        leads_queryset = leads_queryset.filter(lead_status=status_filter)
    
    # Filter by lead stage
    stage_filter = request.GET.get('stage', '')
    if stage_filter:
        leads_queryset = leads_queryset.filter(lead_stage=stage_filter)
    
    # Pagination
    paginator = Paginator(leads_queryset, 25)  # Show 25 leads per page
    page_number = request.GET.get('page')
    leads = paginator.get_page(page_number)
    
    context = {
        'title': 'Lead List',
        'leads': leads,
        'search_query': search_query,
        'status_filter': status_filter,
        'stage_filter': stage_filter,
        'lead_status_choices': Lead.LEAD_STATUS_CHOICES,
        'lead_stage_choices': Lead.LEAD_STAGE_CHOICES,
    }
    return render(request, 'leads/lead_list.html', context)

@login_required
def lead_detail_view(request: HttpRequest, lead_id: str) -> HttpResponse:
    """View detailed information about a specific lead"""
    lead = get_object_or_404(Lead, lead_id=lead_id)
    
    # Handle lead update
    if request.method == 'POST':
        # Update lead fields
        lead.name = request.POST.get('name')
        lead.email = request.POST.get('email')
        lead.address = request.POST.get('address')
        lead.pincode = request.POST.get('pincode')
        lead.number = request.POST.get('number')
        lead.leadsource = request.POST.get('leadsource')
        lead.lead_status = request.POST.get('lead_status')
        lead.lead_stage = request.POST.get('lead_stage')
        lead.budget = request.POST.get('budget') or None
        lead.interested_product_url = request.POST.get('interested_product_url')
        lead.notes = request.POST.get('notes')
        lead.remarks = request.POST.get('remarks')
        
        # Set lead manager to current user (auto-assigned)
        lead.lead_manager = request.user
        
        # Handle categories (multiselect)
        category_ids = request.POST.getlist('categories')
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            lead.categories.set(categories)
        else:
            lead.categories.clear()
        
        # Clear existing lead products
        lead.lead_products.all().delete()
        
        # Handle manual product entries
        for category in Category.objects.all():
            product_name = request.POST.get(f'product_name_{category.id}')
            product_url = request.POST.get(f'product_url_{category.id}')
            product_price = request.POST.get(f'product_price_{category.id}')
            
            if product_name:  # Only create if product name is provided
                # Create or get the product
                product, created = Product.objects.get_or_create(
                    category=category,
                    name=product_name,
                    defaults={
                        'description': f'Product from lead {lead.name or "Unknown"}',
                        'price': float(product_price) if product_price else None,
                        'is_active': True
                    }
                )
                
                # Create the lead-product relationship
                LeadProduct.objects.create(
                    lead=lead,
                    product=product,
                    quantity=1,  # Default quantity
                    notes=f'Product URL: {product_url}' if product_url else None,
                    price_quoted=float(product_price) if product_price else None
                )
        
        lead.save()
        messages.success(request, 'Lead updated successfully!')
        return redirect('leads:lead_detail', lead_id=lead.lead_id)
    
    # Get activities for this lead
    activities = lead.activities.all()
    
    # Get all categories for the form
    categories = Category.objects.all().order_by('name')
    
    # Get existing products for this lead to pre-populate the form
    existing_lead_products = lead.lead_products.select_related('product', 'product__category').all()
    
    context = {
        'title': f'Lead Details - {lead.name or "Unknown"}',
        'lead': lead,
        'activities': activities,
        'categories': categories,
        'existing_lead_products': existing_lead_products,
        'lead_source_choices': Lead.LEAD_SOURCE_CHOICES,
        'lead_status_choices': Lead.LEAD_STATUS_CHOICES,
        'lead_stage_choices': Lead.LEAD_STAGE_CHOICES,
        'activity_type_choices': Activity.ACTIVITY_TYPE_CHOICES,
        'priority_choices': Activity.PRIORITY_CHOICES,
    }
    return render(request, 'leads/lead_detail.html', context)

@login_required
@require_POST
def add_activity_view(request: HttpRequest, lead_id: str) -> JsonResponse:
    """Add activity to a lead via AJAX"""
    try:
        lead = get_object_or_404(Lead, lead_id=lead_id)
        
        activity_type = request.POST.get('activity_type')
        description = request.POST.get('description')
        
        if not activity_type or not description:
            return JsonResponse({'success': False, 'error': 'Activity type and description are required.'})
        
        # Create the activity
        activity = Activity(
            lead=lead,
            activity_type=activity_type,
            description=description,
            created_by=request.user
        )
        
        # Handle call-specific fields
        if activity_type == 'call':
            recording = request.FILES.get('recording')
            if recording:
                activity.recording = recording
        
        # Handle task-specific fields
        elif activity_type == 'task':
            due_date_str = request.POST.get('due_date')
            priority = request.POST.get('priority')
            
            if due_date_str:
                try:
                    # Parse the datetime string (assuming it's in IST)
                    due_date = datetime.fromisoformat(due_date_str.replace('T', ' '))
                    # Convert to UTC for storage
                    ist = pytz.timezone('Asia/Kolkata')
                    due_date = ist.localize(due_date).astimezone(pytz.UTC)
                    activity.due_date = due_date
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid due date format.'})
            
            if priority:
                activity.priority = priority
        
        activity.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{activity.get_activity_type_display()} added successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def tasks_view(request: HttpRequest) -> HttpResponse:
    """View tasks related to leads"""
    # Get task-type activities ordered by due date (earliest first), then by creation date
    task_activities = Activity.objects.filter(activity_type='task').select_related('lead', 'created_by').prefetch_related('notes').order_by('due_date', 'created_date')
    
    # Filter by completion status
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'completed':
        task_activities = task_activities.filter(is_completed=True)
    elif status_filter == 'pending':
        task_activities = task_activities.filter(is_completed=False)
    # 'all' shows everything
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        task_activities = task_activities.filter(priority=priority_filter)
    
    context = {
        'title': 'Tasks',
        'task_activities': task_activities,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'priority_choices': Activity.PRIORITY_CHOICES,
    }
    return render(request, 'leads/tasks.html', context)

@login_required
@require_POST
def mark_task_complete(request: HttpRequest, activity_id: int) -> JsonResponse:
    """Mark a task as complete"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, activity_type='task')
        activity.is_completed = not activity.is_completed  # Toggle completion
        activity.save()
        
        status = 'completed' if activity.is_completed else 'pending'
        return JsonResponse({
            'success': True,
            'is_completed': activity.is_completed,
            'message': f'Task marked as {status}!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def add_task_note(request: HttpRequest, activity_id: int) -> JsonResponse:
    """Add a note to a task"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, activity_type='task')
        note_content = request.POST.get('note')
        
        if not note_content:
            return JsonResponse({'success': False, 'error': 'Note content is required.'})
        
        # Create the task note
        task_note = TaskNote(
            activity=activity,
            note=note_content,
            created_by=request.user
        )
        task_note.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Note added successfully!'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def call_recordings_view(request: HttpRequest) -> HttpResponse:
    """View call recordings (Super admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. This feature is only available to super administrators.')
        return redirect('dashboard')
    
    # Get all call activities with recordings
    call_activities = Activity.objects.filter(
        activity_type='call',
        recording__isnull=False
    ).exclude(recording='').select_related('lead', 'created_by').order_by('-created_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        from django.db import models
        call_activities = call_activities.filter(
            models.Q(lead__name__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(created_by__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(call_activities, 20)  # Show 20 recordings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Call Recordings',
        'call_activities': page_obj,
        'search_query': search_query,
        'total_recordings': call_activities.count(),
    }
    return render(request, 'leads/call_recordings.html', context)

@login_required
@require_POST
def postpone_task(request: HttpRequest, activity_id: int) -> JsonResponse:
    """Postpone a task by updating its due date"""
    try:
        activity = get_object_or_404(Activity, id=activity_id, activity_type='task')
        
        new_due_date_str = request.POST.get('new_due_date')
        if not new_due_date_str:
            return JsonResponse({'success': False, 'error': 'New due date is required.'})
        
        try:
            # Parse the datetime string (assuming it's in IST)
            new_due_date = datetime.fromisoformat(new_due_date_str.replace('T', ' '))
            # Convert to UTC for storage
            ist = pytz.timezone('Asia/Kolkata')
            new_due_date = ist.localize(new_due_date).astimezone(pytz.UTC)
            
            old_due_date = activity.get_ist_due_date()
            activity.due_date = new_due_date
            activity.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Task due date updated successfully!',
                'old_date': old_due_date.strftime('%b %d, %Y %I:%M %p') if old_due_date else 'Not set',
                'new_date': activity.get_ist_due_date().strftime('%b %d, %Y %I:%M %p')
            })
            
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
