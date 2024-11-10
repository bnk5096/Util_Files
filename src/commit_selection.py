"""Determines commits at 30-day intervals for a given GitHub project
"""

import requests
import json
from datetime import datetime, timedelta
from git import Repo

def process_for_project(owner: str, repo_name: str, project_path: str, out_dir: str, auth_file: str):
    """Collects the set of commits to use for the historical complexity analysis

    Args:
        owner (str): The owner of the repository of analysis on GitHub
        repo_name (str): The name of the repository on GitHub
        project_path (str): The local path to the cloned repository
        out_dir (str): the file/path to write the list of commits to
        auth_file (str): the file/path to where the access token for GitHub use is stored
    """

    # Get the first commit
    pathway = []
    repo = Repo(project_path)
    init_commit = next(repo.iter_commits(reverse=True))
    first_date = datetime.fromtimestamp(init_commit.committed_date)
    new_date = datetime(first_date.year, first_date.month, first_date.day)
    print(init_commit.hexsha)
    pathway.append((str(new_date),str(init_commit.hexsha)))
    target_date = new_date
    with open(auth_file, 'r') as file:
        auth = file.readline().strip()
    while target_date < datetime.now():
        target_date = target_date + timedelta(days=30)
        since = target_date.isoformat() + "Z"
        until = (target_date + timedelta(days=1) - timedelta(microseconds=1)).isoformat() + "Z"
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
        params = {
            'since': since,
            'until': until
        }
        headers = {
            'Authorization':f'Bearer {auth}',
            'X-GitHub-Api-Version': '2022-11-28'
            }
        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            commits = response.json()
            if not commits:
                target_date = target_date - timedelta(days=29)
            else:
                new_commit = commits[0]['sha']
                pathway.insert(0,(str(target_date), str(new_commit)))
        # If we get nothing back, add 1 day, try again, repeat until we get a result
        else:
            print(response.status_code)
            break
    with open(out_dir, 'w') as file:
        for entry in pathway:
            file.write(entry[0] + "," + entry[1] + "\n")

def main():
    process_for_project("chromium","chromium","D:/util_repos/chromium", "selected_commits/chromium.csv", 'auth.txt')


if __name__ == '__main__':
    main()
