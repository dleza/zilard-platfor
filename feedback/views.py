from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView

from users.models import User

from .forms import StakeholderFeedbackForm
from .models import StakeholderFeedback


class FeedbackCreateView(View):
    def post(self, request):
        form = StakeholderFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
                if not feedback.contact_name:
                    feedback.contact_name = request.user.get_full_name() or request.user.username
                if not feedback.contact_email:
                    feedback.contact_email = request.user.email
                if not feedback.role_or_group:
                    feedback.role_or_group = request.user.get_role_display()
            feedback.save()
            messages.success(request, "Feedback received.")
            status = 201
            template = "feedback/_thanks.html"
            return render(request, template, {"feedback": feedback}, status=status)
        return render(request, "feedback/_form.html", {"global_feedback_form": form}, status=400)


class FeedbackListView(LoginRequiredMixin, ListView):
    model = StakeholderFeedback
    template_name = "feedback/list.html"
    context_object_name = "feedback_items"
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.role in {User.ROLE_SYSTEM_ADMIN, User.ROLE_NATIONAL_MANAGER}:
            return queryset
        return queryset.filter(user=user)
