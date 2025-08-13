from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Service

def search_services(request):
    query = request.GET.get('q', '').strip()  
    results = []

    if query:
        results = Service.objects.filter(
            Q(title__icontains=query) |  
            Q(category__icontains=query) |  
            Q(provider__username__icontains=query)  
        ).distinct()

    return render(request, 'services/service_list.html', {'services': results, 'query': query})

# Service List View
def service_list(request):
    services = Service.objects.filter(available=True)
    return render(request, "services/service_list.html", {"services": services})


# Create Service
@login_required
def create_service(request):
    category_choices = Service.CATEGORY_CHOICES 

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        other_category = request.POST.get("other_category", "").strip()
        price = request.POST.get("price", "").strip()
        image = request.FILES.get("image")
        available = request.POST.get("available") == "on"

        # Handle "Other" category selection
        if category == "Other" and other_category:
            category = other_category.strip()

        # Validation
        if not title or not description or not category or not price:
            messages.error(request, "All fields are required.")
            return render(request, "services/service_form.html", {
                "category_choices": category_choices
            })

        # Create service
        Service.objects.create(
            provider=request.user,
            title=title,
            description=description,
            category=category,
            price=price,
            image=image,
            available=available,
        )

        messages.success(request, "Service created successfully!")
        return redirect("profile")

    return render(request, "services/service_form.html", {"category_choices": category_choices})


# Update Service
@login_required
def update_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, provider=request.user)
    category_choices = Service.CATEGORY_CHOICES  # Pass categories to template

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "").strip()
        other_category = request.POST.get("other_category", "").strip()
        price = request.POST.get("price", "").strip()
        image = request.FILES.get("image")
        available = request.POST.get("available") == "on"

        # Handle "Other" category selection
        if category == "Other" and other_category:
            category = other_category.strip()

        # Validation
        if not title or not description or not category or not price:
            messages.error(request, "All fields are required.")
            return render(request, "services/service_form.html", {
                "service": service,
                "category_choices": category_choices
            })

        # Update service
        service.title = title
        service.description = description
        service.category = category
        service.price = price
        service.available = available

        if image:
            service.image = image

        service.save()
        messages.success(request, "Service updated successfully!")
        return redirect("profile")

    return render(request, "services/service_form.html", {
        "service": service,
        "category_choices": category_choices
    })


# Delete Service
@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, provider=request.user)

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted successfully!")
        return redirect("profile")

    return render(request, "services/service_confirm_delete.html", {"service": service})
