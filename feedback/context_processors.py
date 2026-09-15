from .forms import StakeholderFeedbackForm


def feedback_form(request):
    return {"global_feedback_form": StakeholderFeedbackForm(initial={"page_url": request.get_full_path()})}
