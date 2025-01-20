import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import GitHubUser, Repository, Commit, Branches

GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_TOKEN = "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"  # Replace with your token


def fetch_repositories(username):
    url = f"{GITHUB_API_BASE_URL}/users/{username}/repos"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    print(f"Fetching repos for {username}: Status {response.status_code}")

    if response.status_code == 200:
        return response.json()
    return []

import time

def fetch_branches(request):
    if request.method == "POST":
        time.sleep(2)
        username = request.POST.get("username")
        repo_name = request.POST.get("repo_name")

        url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/branches"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            branches = response.json()
            return JsonResponse({"branches": branches})
        return JsonResponse({"message": "Failed to fetch branches."}, status=400)


def fetch_commits(username, repo_name, branch_name):
    url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/commits?sha={branch_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    print("This mis myt response:",response)

    if response.status_code == 200:
        return response.json()
    return []


# Single Page for GitHub ID and Repo Selection
def github_repo_commit_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        repos = fetch_repositories(username)
        return JsonResponse({"repos": repos, "username": username})
    return render(request, "github_commits/single_page.html")

def edit_repo(request , repo_id):
    repo = get_object_or_404(Repository, pk=repo_id)
    branches = repo.branches.all()
    print("Came here to edit ....")
    if request.method == "POST":
        username = request.POST.get("username")
        repos = fetch_repositories(username)
        return JsonResponse({"repos": repos, "username": username})
    return render(request, "github_commits/single_page.html" , context={"repo": repo , "username": repo.user.username , 'branches': branches})


def store_repository(request):
    if request.method == "POST":
        username = request.POST.get("username")
        repo_name = request.POST.get("repo_name")
        branch_name = request.POST.get("branch_name")
        print(username, repo_name, branch_name)
        branch_list = []

        if username and repo_name:
            user, _ = GitHubUser.objects.get_or_create(username=username)
            repos = fetch_repositories(username)
            repo = next((r for r in repos if r["name"] == repo_name), None)

            if repo:
                repository, _ = Repository.objects.get_or_create(
                    user=user,
                    name=repo["name"],
                    description=repo.get("description", ""),
                    html_url=repo["html_url"],
                )

                if branch_name == "all":
                    branches_url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/branches"
                    branches_response = requests.get(branches_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
                    
                    if branches_response.status_code == 200:
                        branches = branches_response.json()
                        for branch in branches:
                            branch_id = fetch_and_store_commits(username, repo_name, repository, branch["name"])
                            if branch_id:
                                branch_list.append(branch_id)
                else:
                    branch_id = fetch_and_store_commits(username, repo_name, repository, branch_name)
                    branch_list.append(branch_id)

                print(branch_list)
                return JsonResponse({"message": "Repository and commits stored successfully!", "repo_id": repository.id , "branch_list": branch_list , }, status=200)

        return JsonResponse({"message": "Invalid data provided."}, status=400)


def fetch_and_store_commits(username, repo_name, repository, branch_name):
    commits_url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/commits?sha={branch_name}"
    commits_response = requests.get(commits_url, headers={"Authorization": f"token {GITHUB_TOKEN}"})

    if commits_response.status_code == 200:
        commits_data = commits_response.json()
        # Create or fetch the branch instance
        branch, created = Branches.objects.get_or_create(name=branch_name, repository=repository)
        # print(branch , branch.id ," this is the branch id le")

        for commit in commits_data:
            commit_info = commit.get("commit", {})
            # Store the commit
            Commit.objects.get_or_create(
                branch=branch,  # Now using `branch` as the ForeignKey
                sha=commit["sha"],
                message=commit_info.get("message", ""),
                author=commit_info.get("author", {}).get("name", "Unknown"),
                date=commit_info.get("author", {}).get("date", None),
                
            )
        return branch.id
    return


# View & Update Database Records
def database_view(request):
    repositories = Repository.objects.all()
    return render(request, "github_commits/database_view.html", {"repositories": repositories})


def update_commits(request, repo_id):
    repository = Repository.objects.get(id=repo_id)
    username = repository.user.username
    repo_name = repository.name

    branches = repository.branches.all()
    for branch in branches:
        commits_data = fetch_commits(username, repo_name, branch.name)
        for commit in commits_data:
            commit_info = commit.get("commit", {})
            Commit.objects.get_or_create(
                sha=commit["sha"],
                message=commit_info.get("message", ""),
                author=commit_info.get("author", {}).get("name", "Unknown"),
                date=commit_info.get("author", {}).get("date", None),
                branch=branch
            )
    return redirect("github:database_view")


def view_commits(request, repo_id):
    repository = Repository.objects.get(id=repo_id)
    branches = repository.branches.all()
    return render(request, "github_commits/commit_list.html", {"repository": repository, "branches": branches})
