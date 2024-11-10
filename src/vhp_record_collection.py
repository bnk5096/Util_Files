"""Performs VHP API calls
"""
import requests
import json

def make_requests():
    """Performs requests on the VHP API to fetch required data
    """
    
    # Get Project data
    url = "https://vulnerabilityhistory.org/api/projects"
    response = requests.get(url)
    with open("vhp_records/project_details.json", 'w') as file:
        json.dump(response.json(), file)

    # Get all offender files
    url = "https://vulnerabilityhistory.org/api/filepaths"
    params = {
        "offenders":"true"
    }
    response = requests.get(url=url, params=params)
    with open('vhp_records/offender_files.json', 'w') as file:
        json.dump(response.json(), file)

    # Get Vulnerability Records
    url = "https://vulnerabilityhistory.org/api/vulnerabilities"
    response = requests.get(url=url)
    with open('vhp_records/vulnerabilities_list.json', 'w') as file:
        json.dump(response.json(), file)

    # Get Tag mapping to identify the CWEs
    url = "https://vulnerabilityhistory.org/api/tags"
    response = requests.get(url=url)
    with open('vhp_records/tag_mapping.json', 'w') as file:
        json.dump(response.json(), file)

    # Get event dates for each CVE
    collection = None
    with open("vhp_records/vulnerabilities_list.json", 'r') as file:
        collection = json.load(file)
    if collection is not None:
        for entry in collection:
            cve = entry['cve']
            url = f"https://vulnerabilityhistory.org/api/vulnerabilities/{cve}/events"
            response = requests.get(url)
            with open(f"vhp_records/event_data/{cve}.json", 'w') as file:
                json.dump(response.json(), file)


def main():
    make_requests()


if __name__ == '__main__':
    main()
