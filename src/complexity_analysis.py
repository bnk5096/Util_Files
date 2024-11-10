"""Orchestrates the running the scc tool on a repository at various points in a project's history. Requires some manual configuration
"""
import argparse
import subprocess


def orchestrate(commit_list: str, repo_path: str, output_dir: str) -> None:
    """Runs the checking out of git commits and the operation of the SCC tool

    Args:
        commit_list (str): the file/path containing the commits to analyze
        repo_path (str): The path to the repo to process
        output_dir (str): the path to write the output to
    """
    commits = {}
    with open(commit_list, 'r') as file:
        for line in file:
            sline = line.strip().split(",")
            date = sline[0].split(" ")[0]
            commit = sline[1]
            commits[date] = commit
    for entry in commits:
        subprocess.getoutput(f"git -C {repo_path} checkout {commits[entry]}")
        subprocess.getoutput(f"git -C {repo_path} pull")
        subprocess.getoutput(f"scc {repo_path} --by-file --format csv -o {output_dir}/{entry}.csv")
        subprocess.getoutput(f"scc {repo_path} --by-file --uloc --format csv -o {output_dir}/{entry}_unique_lines.csv")
        subprocess.getoutput(f"scc {repo_path} --format csv -o {output_dir}/{entry}_by_language.csv")
        subprocess.getoutput(f"git -C {repo_path} checkout -")
        subprocess.getoutput(f"git -C {repo_path} pull")



def main():
    parser = argparse.ArgumentParser(
        prog="complexity_analysis.py",
        description="Performs complexity analysis for the entire history of a project on a set basis of time",
    )
    # Project
    # VHP Data File
    # Time scale
    # Output location
    orchestrate("selected_commits/django.csv", "", "complexity_data/django")

if __name__ == '__main__':
    main()
