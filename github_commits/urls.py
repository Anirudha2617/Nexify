from django.urls import path
from . import views

app_name = 'github'

urlpatterns = [
    path("", views.github_repo_commit_view, name="github_repo_commit"),
    path("store-repo/", views.store_repository, name="store_repository"),
    path("database/", views.database_view, name="database_view"),
    path("update/<int:repo_id>/", views.update_commits, name="update_commits"),
    path("view/<int:repo_id>/", views.view_commits, name="view_commits"),
    path("edit/<int:repo_id>/", views.edit_repo, name="edit_repo"),
    path("fetch-branches/", views.fetch_branches, name="fetch_branches"),
]
