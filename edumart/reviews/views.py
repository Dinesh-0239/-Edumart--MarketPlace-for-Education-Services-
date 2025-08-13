from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden  # 🚀 Unauthorized access prevention
from .models import Review
from services.models import Service
from bookings.models import Booking  

# ✅ List Reviews for a Specific Service
def service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = Review.objects.filter(service=service).order_by('-created_at')
    return render(request, "reviews/service_reviews.html", {"service": service, "reviews": reviews})


# ✅ Submit Review (Restrict multiple reviews per service per provider)
@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # ✅ Ensure user has booked the service before reviewing
    if not Booking.objects.filter(client=request.user, service=service, status="Completed").exists():
        return redirect("service_reviews", service_id=service.id)

    # ✅ Check if the client has already reviewed this service from the same provider
    existing_review = Review.objects.filter(client=request.user, service=service).first()
    if existing_review:
        return redirect("edit_review", review_id=existing_review.id)  # Redirect to edit review

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        # ✅ Ensure rating is a valid number (1-5)
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            return render(request, "reviews/review_form.html", {"service": service, "error": "Invalid rating!"})

        if rating and comment:
            Review.objects.create(
                client=request.user,
                service=service,
                rating=rating,
                comment=comment
            )
            return redirect("profile")

    return render(request, "reviews/review_form.html", {"service": service})


# ✅ Edit Review
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, client=request.user)

    if request.method == "POST":
        review.rating = request.POST.get("rating")
        review.comment = request.POST.get("comment")
        review.save()
        return redirect("profile")

    return render(request, "reviews/edit_review.html", {"review": review})


# ✅ Delete Review (with confirmation page)
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, client=request.user)

    if request.method == "POST":
        service_id = review.service.id
        review.delete()
        return redirect("profile")

    return render(request, "reviews/delete_review.html", {"review": review})


# ✅ View Reviews for a Service (For Service Provider)
@login_required
def view_service_reviews(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    reviews = Review.objects.filter(service=service).order_by('-created_at')

    return render(request, "reviews/view_service_reviews.html", {
        "service": service, 
        "reviews": reviews
    })


# ✅ View All Reviews for a Provider's Services
@login_required
def provider_reviews(request):
    provider_services = Service.objects.filter(provider=request.user)
    provider_reviews = Review.objects.filter(service__in=provider_services).order_by('-created_at')

    return render(request, "reviews/provider_reviews.html", {"provider_reviews": provider_reviews})
