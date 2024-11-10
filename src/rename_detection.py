"""Performs rename detection related operations with variable processing options
"""
from git import Repo
import argparse
import subprocess
import csv

def get_all_files(project_path: str, src_extensions: str, out_file:str) -> None:
    """Writes a list of all files that have existed in the specified repository to the specified output location

    Args:
        project_path (str): the path to the repository to analyze
        src_extensions (str): The path to a file containing allowed extensions, one per line
        out_file (str): the output path for the list of files to be written to
    """
    file_set = set()
    extensions = set()
    out_list = []
    repo = Repo(project_path)
    
    for commit in repo.iter_commits():
        stats = commit.stats
        changed_files = stats.files.keys()
        for file in changed_files:
            if file not in file_set:
                file_set.add(file)
                out_list.append(file)
    with open(src_extensions, 'r') as file:
        for line in file:
            extensions.add(line.strip())


    with open(out_file, 'w') as file:
        for entry in out_list:
            if "chromium" in project_path.lower() and entry.startswith("third_party"):
                continue
            if entry.split(".")[-1] in extensions:
                file.write(entry + "\n")
    return


def rename_track(project_path: str, files_path: str, out_file:str) -> None:
    """the default rename tracking operation (File by File, every file)

    Args:
        project_path (str): the path to the project repo
        files_path (str): the path to the list of all known files
        out_file (str): the destination to write to
    """
    rename_records = {}
    repo = Repo(project_path)
    seen = set()
    files = []
    with open(files_path, 'r') as file:
        for line in file:
            files.append(line.strip())
    total = len(files)
    counter = 0
    for file in files:
        print("file: " + str(counter) + " of " + str(total))
        print(str((counter/total) * 100) + "%\n")
        if file not in seen:
            seen.add(file)
            current = file
            record = [file]
            commit_ops = subprocess.getoutput("git -C " + project_path + " log --stat --follow --pretty= --name-status  -- \"" + file + "\"")
            split_commit_ops = commit_ops.split("\n")
            for commit_op in split_commit_ops:
                op = commit_op.split("\t")
                try:
                    if (op[0][0] == 'R') and op[2] == current:
                        new = op[1]
                        seen.add(new)
                        record.append(new)
                        current = new
                except IndexError:
                    continue
            rename_records[file] = tuple(record)
        counter += 1
    with open(out_file, 'w') as file:
        writer = csv.writer(file)
        for key in rename_records:
            writer.writerow(rename_records[key])
    return


def rename_track_2(project_path: str, files_path: str, out_file:str) -> None:
    """the second fastest rename tracking op (File by File, only files identified in the repo's git log rename records)

    Args:
        project_path (str): the path to the project repo
        files_path (str): the path to the list of all known files
        out_file (str): the destination to write to
    """
    rename_records = {}
    track = set()
    files = []
    with open(files_path, 'r') as file:
        for line in file:
            files.append(line.strip())
    seen = set()
    renamed_set = subprocess.getoutput("git -C " + project_path + " log --name-status --diff-filter=R --pretty=")
    split_ops = renamed_set.split("\n")
    for entry in split_ops:
        try:
            op = entry.split("\t")
            track.add(op[1])
            track.add(op[2])
        except IndexError:
            continue
    total = len(files)
    counter = 0
    for file in files:
        print("file: " + str(counter) + " of " + str(total))
        print(str((counter/total) * 100) + "%\n")
        if file not in seen:
            seen.add(file)
            current = file
            record = [file]
            if file in track:
                commit_ops = subprocess.getoutput("git -C " + project_path + " log --stat --follow --pretty= --name-status  -- \"" + file + "\"")
                split_commit_ops = commit_ops.split("\n")
                for commit_op in split_commit_ops:
                    op = commit_op.split("\t")
                    try:
                        if (op[0][0] == 'R') and op[2] == current:
                            new = op[1]
                            seen.add(new)
                            record.append(new)
                            current = new
                    except IndexError:
                        continue
            rename_records[file] = tuple(record)
        counter += 1
    with open(out_file, 'w') as file:
        writer = csv.writer(file)
        for key in rename_records:
            writer.writerow(rename_records[key])
    return


def rename_track_3(project_path: str, files_path: str, out_file:str) -> None:
    """the fastest rename tracking operation (Only rename operations logged in the repo's git log)

    Args:
        project_path (str): the path to the project repo
        files_path (str): the path to the list of all known files
        out_file (str): the destination to write to
    """
    rename_records = {}
    track = {}
    files = []
    with open(files_path, 'r') as file:
        for line in file:
            files.append(line.strip())
    seen = set()
    renamed_set = subprocess.getoutput("git -C " + project_path + " log --name-status --diff-filter=R --pretty=")
    split_ops = renamed_set.split("\n")
    for entry in split_ops:
        op = entry.split("\t")
        track[op[2]] = op[1]
    total = len(files)
    counter = 0
    for file in files:
        print("file: " + str(counter) + " of " + str(total))
        print(str((counter/total) * 100) + "%\n")
        if file not in seen:
            seen.add(file)
            record = [file]
            pointer = file
            while pointer in track:
                record.append(track[pointer])
                pointer = track[pointer]
                if pointer in seen:
                    break
                seen.add(pointer)
            rename_records[file] = tuple(record)
        counter += 1
    with open(out_file, 'w') as file:
        writer = csv.writer(file)
        for key in rename_records:
            writer.writerow(rename_records[key])
    return



def main():
    parser = argparse.ArgumentParser(
        prog="rename_detection.py",
        description="Finds all source code files from a given git repository's entire history and identifies renamed files",
    )
    subparsers = parser.add_subparsers(dest='mode', help="Mode selection")
    parser_records = subparsers.add_parser('records', help="Operation to gather all historical source files from the given repository")
    parser_renames = subparsers.add_parser('rename', help="Operation to identify all renames for all files in the historical records")
    parser_both = subparsers.add_parser('both', help="Collect historical records and perform rename analysis")
    parser_records.add_argument('repository', type=str, help="The filepath to the repository of analysis")
    parser_records.add_argument('out', type=str, help="The path to write final output to")
    parser_records.add_argument('extensions', type=str, help="The path to the file containing the valid source code extensions for the repository")
    parser_renames.add_argument('repository', type=str, help="The filepath to the repository of analysis")
    parser_renames.add_argument('out', type=str, help="The path to write final output to")
    parser_renames.add_argument('files', type=str, help="The path to the file containing the historical records")
    parser_both.add_argument('repository', type=str, help="The filepath to the repository of analysis")
    parser_both.add_argument('out', type=str, help="The path to write final output to")
    parser_both.add_argument('extensions', type=str, help="The path to the file containing the valid source code extensions for the repository")
    parser_both.add_argument('intermediate', type=str, help="The path to write the full list of records to")
    args = parser.parse_args()

    if args.mode == 'records':
        get_all_files(args.repository, args.extensions, args.out)
    elif args.mode == 'rename':
        rename_track_3(args.repository, args.files, args.out)
    else:
        get_all_files(args.repository, args.extensions, args.intermediate)
        rename_track(args.repository, args.intermediate, args.out)


if __name__ == '__main__':
    main()
