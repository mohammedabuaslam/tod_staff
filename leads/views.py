from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from .models import Lead
from django.contrib.auth.models import User

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
        lead.whatsapp_url = request.POST.get('whatsapp_url')
        lead.notes = request.POST.get('notes')
        lead.remarks = request.POST.get('remarks')
        lead.lead_status = request.POST.get('lead_status', 'new')
        lead.lead_stage = request.POST.get('lead_stage', 'prospect')
        lead.activity = request.POST.get('activity')
        lead.interested_product_url = request.POST.get('interested_product_url')
        lead.budget = request.POST.get('budget') or None
        lead.interested_categories = request.POST.get('interested_categories')
        lead.task = request.POST.get('task')
        
        # Set lead manager if provided
        lead_manager_id = request.POST.get('lead_manager')
        if lead_manager_id:
            try:
                lead.lead_manager = User.objects.get(id=lead_manager_id)
            except User.DoesNotExist:
                pass
        
        # Save the lead
        lead.save()
        messages.success(request, f'Lead "{lead.name or "New Lead"}" has been created successfully!')
        return redirect('leads:lead_detail', lead_id=lead.lead_id)
    
    # Get all users for lead manager dropdown
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    context = {
        'title': 'Create New Lead',
        'users': users,
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
    
    context = {
        'title': f'Lead Details - {lead.name or "Unknown"}',
        'lead': lead,
    }
    return render(request, 'leads/lead_detail.html', context)

@login_required
def tasks_view(request: HttpRequest) -> HttpResponse:
    """View tasks related to leads"""
    # Get leads that have tasks assigned
    leads_with_tasks = Lead.objects.filter(task__isnull=False).exclude(task='')
    
    context = {
        'title': 'Tasks',
        'leads_with_tasks': leads_with_tasks,
    }
    return render(request, 'leads/tasks.html', context)
