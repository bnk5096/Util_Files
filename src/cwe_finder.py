"""Performs analysis of a project to determine the CWEs of relevance
"""
import json
from typing import List

class CVE:
    def __init__(self, id: str, cwe_list: List[str], project: str):
        self.id = id
        self.cwe_list = cwe_list
        self.project = project
        self.files = set()
        self.util = False
    
    def add_file(self, file):
        self.files.add(file)

    def set_util(self):
        self.util = True

def read_vulns(vuln_list: str, tag_map: dict, off_files: str, util_map: dict) -> list:
    """reads through the vulnerabilities from the VHP and builds CVE objects

    Args:
        vuln_list (str): the path to the vulnerability output from the VHP api
        tag_map (dict): the map of tags to CWEs
        off_files (str): the path to the offender file list output from the VHP api
        util_map (dict): the map of files to their util status

    Returns:
        list: a list of CVE objects 
    """
    results = []
    data = None
    with open(vuln_list, 'r') as file:
        data = json.load(file)
    for entry in data:
        cwes = []
        id = entry['cve']
        project = entry['project_name']
        for tag in entry['tag_json']:
            if tag['id'] in tag_map:
                cwes.append(tag_map[tag['id']])
        results.append(CVE(id, cwes, project))
    file_cve_map = {}
    with open(off_files, 'r') as file:
        file_set = json.load(file)
        for file in file_set:
            path = file['filepath']
            for cve in file['cves']:
                if cve not in file_cve_map:
                    file_cve_map[cve] = []
                file_cve_map[cve].append(path)
    for entry_loc in range(len(results)):
        entry = results[entry_loc].id
        if entry in file_cve_map:
            for f in file_cve_map[entry]:
                results[entry_loc].add_file(f)
    for entry in results:
        for file in entry.files:
            if file in util_map and util_map[file] == True:
                entry.set_util()
                break
    return results


def get_tag_cwes(tag_map_file:str) -> dict:
    """Generates a map of VHP tages to CWE numbers

    Args:
        tag_map_file (str): the file to the output from the VHP tag api

    Returns:
        dict: a dictionary mapping VHP Tag IDs to CWE numbers
    """
    created_map = {}
    data = None
    with open(tag_map_file, 'r') as file:
         data = json.load(file)
    for entry in data:
        if 'cwe' in entry['shortname'].lower():
            created_map[entry["id"]] = entry['shortname']
    return created_map


def get_util(rename_dir: str) -> dict:
    """Generates a dictionary of files to their util status

    Args:
        rename_dir (str): the directory containing the set of rename csvs

    Returns:
        dict: a map of files to their util status
    """
    util_map = {}
    for rename_file in ['chromium.csv','django.csv','FFmpeg.csv','httpd.csv','linux.csv','struts.csv','systemd.csv','tomcat.csv']:
        with open(f"{rename_dir}/{rename_file}", 'r') as file:
            for line in file:
                if "util" in line.lower() or "helper" in line.lower():
                    for entry in line.strip().split(","):
                        util_map[entry] = True
                else:
                    for entry in line.strip().split(","):
                        util_map[entry] = False
    return util_map


def cwe_analysis(results: list) -> None:
    """Calculates CWE-related metrics

    Args:
        results (list): The list of CVE objects to analyze
    """
    pack = {}
    for result in results:
        if result.project not in pack:
            pack[result.project] = []
        pack[result.project].append(result)
    overall_util = set()
    overall_non = set()
    for project in pack:
        print(project)
        project_util = set()
        project_non = set()
        for cve in pack[project]:
            if cve.util:
                for cwe in cve.cwe_list:
                    project_util.add(cwe)
                    overall_util.add(cwe)
            else:
                for cwe in cve.cwe_list:
                    project_non.add(cwe)
                    overall_non.add(cwe)
        print("UTIL ONLY:")
        for entry in project_util:
            if entry not in project_non:
                print(entry)
        print("NON-Only:")
        for entry in project_non:
            if entry not in project_util:
                print(entry)
    print("Overall:")
    print("Util Only:")
    for entry in overall_util:
        if entry not in overall_non:
            print(entry)
    print("Non Only:")
    for entry in overall_non:
        if entry not in overall_util:
            print(entry)

def main():
    tag_map = get_tag_cwes("vhp_records/tag_mapping.json")
    util_map = get_util("rename_records")
    results = read_vulns("vhp_records/vulnerabilities_list.json", tag_map, "vhp_records/offender_files.json", util_map)
    cwe_analysis(results)

if __name__ == '__main__':
    main()