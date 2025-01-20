from django.contrib import admin
from .models import GitHubUser, Repository, Commit, Branches

@admin.register(GitHubUser)
class GitHubUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")
    search_fields = ("username",)
    ordering = ("username",)


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "html_url", "description")
    search_fields = ("name", "user__username", "description")
    list_filter = ("user",)
    ordering = ("name",)


@admin.register(Branches)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "repository", "html_url", "description")
    # search_fields = ("name", "user__username", "description")
    list_filter = ("repository",)
    ordering = ("name",)


@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    list_display = ("id", "sha", "branch_name", "branch", "author", "date") #, "message_snippet")
    search_fields = ("sha", "author", "message", "branch")
    list_filter = ("branch_name", "branch", "date")
    ordering = ("-date",)

    # def message_snippet(self, obj):
    #     return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    # message_snippet.short_description = "Commit Message"
