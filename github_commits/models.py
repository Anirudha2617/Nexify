from django.db import models

class GitHubUser(models.Model):
    username = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.username

class Repository(models.Model):
    user = models.ForeignKey(GitHubUser, on_delete=models.CASCADE, related_name="repositories")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    html_url = models.URLField()

    class Meta:
        unique_together = ('user', 'name', 'html_url')
    def __str__(self):
        return self.name
    
class Branches(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="branches" )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    html_url = models.URLField()

    def __str__(self):
        return self.name

class Commit(models.Model):
    branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name="commits", null = True)
    sha = models.CharField(max_length=40)
    message = models.TextField()
    author = models.CharField(max_length=100)
    date = models.DateTimeField()
    branch_name = models.CharField(max_length=100, default="main")

    def __str__(self):
        return f"{self.sha[:7]} - {self.message[:50]}"
