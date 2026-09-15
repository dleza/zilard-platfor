from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from users.permissions import filter_workers_for_user, filter_workplaces_for_user, require_edit_permission

from .forms import (
    DisabilityProfileForm,
    LabourRightsRecordForm,
    OccupationForm,
    TradeUnionForm,
    WorkerDocumentForm,
    WorkerFilterForm,
    WorkerForm,
    WorkplaceForm,
)
from .models import DisabilityProfile, LabourRightsRecord, Occupation, TradeUnion, Worker, Workplace


class SystemAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not getattr(request.user, "is_system_admin", False):
            raise PermissionDenied("Only system administrators can access settings.")
        return super().dispatch(request, *args, **kwargs)


class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker
    template_name = "workers/list.html"
    context_object_name = "workers"
    paginate_by = 25

    def get_queryset(self):
        queryset = filter_workers_for_user(
            Worker.objects.select_related("workplace", "disability_profile", "created_by"),
            self.request.user,
        )
        form = WorkerFilterForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get("q")
            province = form.cleaned_data.get("province")
            district = form.cleaned_data.get("district")
            disability_type = form.cleaned_data.get("disability_type")
            union = form.cleaned_data.get("union")
            if q:
                queryset = queryset.filter(
                    Q(unique_id__icontains=q)
                    | Q(first_name__icontains=q)
                    | Q(last_name__icontains=q)
                    | Q(other_names__icontains=q)
                    | Q(phone__icontains=q)
                    | Q(workplace__employer_name__icontains=q)
                    | Q(workplace__workplace_name__icontains=q)
                )
            if province:
                queryset = queryset.filter(province=province)
            if district:
                queryset = queryset.filter(district=district)
            if disability_type:
                queryset = queryset.filter(disability_profile__disability_type=disability_type)
            if union:
                queryset = queryset.filter(union_name=union)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = WorkerFilterForm(self.request.GET)
        context["can_edit"] = self.request.user.can_edit_records
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request"):
            return render(self.request, "workers/_worker_table.html", context)
        return super().render_to_response(context, **response_kwargs)


class WorkerDetailView(LoginRequiredMixin, DetailView):
    model = Worker
    template_name = "workers/detail.html"
    context_object_name = "worker"

    def get_queryset(self):
        return filter_workers_for_user(
            Worker.objects.select_related(
                "workplace",
                "disability_profile",
                "labour_rights",
                "created_by",
                "updated_by",
            ).prefetch_related("documents"),
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["profile"] = self.object.disability_profile
        except ObjectDoesNotExist:
            context["profile"] = None
        try:
            context["rights"] = self.object.labour_rights
        except ObjectDoesNotExist:
            context["rights"] = None
        context["can_edit"] = self.request.user.can_edit_records
        return context


class WorkerUpsertView(LoginRequiredMixin, View):
    template_name = "workers/worker_form.html"
    worker = None

    def dispatch(self, request, *args, **kwargs):
        require_edit_permission(request.user)
        if "pk" in kwargs:
            self.worker = get_object_or_404(filter_workers_for_user(Worker.objects.all(), request.user), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_related_instances(self):
        if not self.worker:
            return None, None
        disability, _ = DisabilityProfile.objects.get_or_create(
            worker=self.worker,
            defaults={"disability_type": "physical", "severity": "moderate"},
        )
        rights, _ = LabourRightsRecord.objects.get_or_create(worker=self.worker)
        return disability, rights

    def get(self, request, *args, **kwargs):
        disability, rights = self.get_related_instances()
        context = {
            "worker": self.worker,
            "worker_form": WorkerForm(instance=self.worker),
            "disability_form": DisabilityProfileForm(instance=disability),
            "rights_form": LabourRightsRecordForm(instance=rights),
            "document_form": WorkerDocumentForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        disability, rights = self.get_related_instances()
        worker_form = WorkerForm(request.POST, request.FILES, instance=self.worker)
        disability_form = DisabilityProfileForm(request.POST, instance=disability)
        rights_form = LabourRightsRecordForm(request.POST, instance=rights)
        document_form = WorkerDocumentForm(request.POST, request.FILES)

        document_requested = bool(request.FILES.get("file") or request.POST.get("title"))
        document_valid = document_form.is_valid() if document_requested else True

        if worker_form.is_valid() and disability_form.is_valid() and rights_form.is_valid() and document_valid:
            worker = worker_form.save(commit=False)
            if not worker.pk:
                worker.created_by = request.user
                worker.capture_source = Worker.CAPTURE_SOURCE_WEB
                worker.capture_mode = Worker.CAPTURE_MODE_ONLINE
            worker.updated_by = request.user
            worker.save()
            worker_form.save_m2m()

            disability = disability_form.save(commit=False)
            disability.worker = worker
            disability.save()

            rights = rights_form.save(commit=False)
            rights.worker = worker
            rights.save()

            if document_requested:
                document = document_form.save(commit=False)
                if not document.title:
                    document.title = document.file.name
                document.worker = worker
                document.uploaded_by = request.user
                document.save()

            messages.success(request, "Worker record saved.")
            return redirect("workers:detail", pk=worker.pk)

        return render(
            request,
            self.template_name,
            {
                "worker": self.worker,
                "worker_form": worker_form,
                "disability_form": disability_form,
                "rights_form": rights_form,
                "document_form": document_form,
            },
            status=400,
        )


class WorkplaceListView(LoginRequiredMixin, ListView):
    model = Workplace
    template_name = "workers/workplace_list.html"
    context_object_name = "workplaces"
    paginate_by = 25

    def get_queryset(self):
        queryset = filter_workplaces_for_user(Workplace.objects.all(), self.request.user)
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                Q(employer_name__icontains=q)
                | Q(workplace_name__icontains=q)
                | Q(district__icontains=q)
                | Q(province__icontains=q)
            )
        return queryset


class WorkplaceCreateView(LoginRequiredMixin, View):
    template_name = "workers/workplace_form.html"

    def dispatch(self, request, *args, **kwargs):
        require_edit_permission(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": WorkplaceForm()})

    def post(self, request):
        form = WorkplaceForm(request.POST)
        if form.is_valid():
            workplace = form.save()
            messages.success(request, "Workplace saved.")
            return redirect("workers:workplaces")
        return render(request, self.template_name, {"form": form}, status=400)


class WorkplaceUpdateView(WorkplaceCreateView):
    def dispatch(self, request, *args, **kwargs):
        self.workplace = get_object_or_404(filter_workplaces_for_user(Workplace.objects.all(), request.user), pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        return render(request, self.template_name, {"form": WorkplaceForm(instance=self.workplace), "workplace": self.workplace})

    def post(self, request, pk):
        form = WorkplaceForm(request.POST, instance=self.workplace)
        if form.is_valid():
            form.save()
            messages.success(request, "Workplace saved.")
            return redirect("workers:workplaces")
        return render(request, self.template_name, {"form": form, "workplace": self.workplace}, status=400)


class SettingsHomeView(SystemAdminRequiredMixin, TemplateView):
    template_name = "settings/index.html"


class SettingsLookupListView(SystemAdminRequiredMixin, ListView):
    template_name = "settings/lookup_list.html"
    context_object_name = "items"
    paginate_by = 25
    model = None
    title = ""
    description = ""
    create_url_name = ""
    edit_url_name = ""

    def get_queryset(self):
        queryset = self.model.objects.all()
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.title,
                "description": self.description,
                "create_url_name": self.create_url_name,
                "edit_url_name": self.edit_url_name,
            }
        )
        return context


class OccupationListView(SettingsLookupListView):
    model = Occupation
    title = "Occupation Settings"
    description = "Define occupations users can select when entering worker records."
    create_url_name = "workers:settings-occupation-create"
    edit_url_name = "workers:settings-occupation-edit"


class TradeUnionListView(SettingsLookupListView):
    model = TradeUnion
    title = "Trade Union Settings"
    description = "Define trade unions users can select when entering worker records."
    create_url_name = "workers:settings-trade-union-create"
    edit_url_name = "workers:settings-trade-union-edit"


class SettingsLookupFormView(SystemAdminRequiredMixin, View):
    template_name = "settings/lookup_form.html"
    model = None
    form_class = None
    list_url_name = ""
    title_create = ""
    title_update = ""

    def dispatch(self, request, *args, **kwargs):
        self.instance = None
        if "pk" in kwargs:
            self.instance = get_object_or_404(self.model, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context(self, form):
        return {
            "form": form,
            "item": self.instance,
            "title": self.title_update if self.instance else self.title_create,
            "list_url_name": self.list_url_name,
        }

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.instance)
        return render(request, self.template_name, self.get_context(form))

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings record saved.")
            return redirect(self.list_url_name)
        return render(request, self.template_name, self.get_context(form), status=400)


class OccupationCreateView(SettingsLookupFormView):
    model = Occupation
    form_class = OccupationForm
    list_url_name = "workers:settings-occupations"
    title_create = "Add Occupation"
    title_update = "Edit Occupation"


class OccupationUpdateView(OccupationCreateView):
    pass


class TradeUnionCreateView(SettingsLookupFormView):
    model = TradeUnion
    form_class = TradeUnionForm
    list_url_name = "workers:settings-trade-unions"
    title_create = "Add Trade Union"
    title_update = "Edit Trade Union"


class TradeUnionUpdateView(TradeUnionCreateView):
    pass
