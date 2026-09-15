from django.urls import path

from users.views import (
    SettingsUserCategoryFormView,
    SettingsUserCategoryListView,
    SettingsUserFormView,
    SettingsUserListView,
)

from .views import (
    OccupationCreateView,
    OccupationListView,
    OccupationUpdateView,
    SettingsHomeView,
    TradeUnionCreateView,
    TradeUnionListView,
    TradeUnionUpdateView,
    WorkerDetailView,
    WorkerListView,
    WorkerUpsertView,
    WorkplaceCreateView,
    WorkplaceListView,
    WorkplaceUpdateView,
)

app_name = "workers"

urlpatterns = [
    path("", WorkerListView.as_view(), name="list"),
    path("new/", WorkerUpsertView.as_view(), name="create"),
    path("settings/", SettingsHomeView.as_view(), name="settings"),
    path("settings/occupations/", OccupationListView.as_view(), name="settings-occupations"),
    path("settings/occupations/new/", OccupationCreateView.as_view(), name="settings-occupation-create"),
    path("settings/occupations/<int:pk>/edit/", OccupationUpdateView.as_view(), name="settings-occupation-edit"),
    path("settings/trade-unions/", TradeUnionListView.as_view(), name="settings-trade-unions"),
    path("settings/trade-unions/new/", TradeUnionCreateView.as_view(), name="settings-trade-union-create"),
    path("settings/trade-unions/<int:pk>/edit/", TradeUnionUpdateView.as_view(), name="settings-trade-union-edit"),
    path("settings/users/", SettingsUserListView.as_view(), name="settings-users"),
    path("settings/users/new/", SettingsUserFormView.as_view(), name="settings-user-create"),
    path("settings/users/<int:pk>/edit/", SettingsUserFormView.as_view(), name="settings-user-edit"),
    path("settings/user-categories/", SettingsUserCategoryListView.as_view(), name="settings-user-categories"),
    path("settings/user-categories/new/", SettingsUserCategoryFormView.as_view(), name="settings-user-category-create"),
    path("settings/user-categories/<int:pk>/edit/", SettingsUserCategoryFormView.as_view(), name="settings-user-category-edit"),
    path("<int:pk>/", WorkerDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", WorkerUpsertView.as_view(), name="edit"),
    path("workplaces/", WorkplaceListView.as_view(), name="workplaces"),
    path("workplaces/new/", WorkplaceCreateView.as_view(), name="workplace-create"),
    path("workplaces/<int:pk>/edit/", WorkplaceUpdateView.as_view(), name="workplace-edit"),
]
