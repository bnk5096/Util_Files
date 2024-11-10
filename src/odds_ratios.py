"""Performs odds ratios calculations
"""
import json

class Alias:
    def __init__(self, name):
        self.name = name
        if "test" in name.lower():
            self.test = True
        else:
            self.test = False
        if "util" in name.lower() or "helper" in name.lower():
            self.util = True
        else: 
            self.util = False
        self.off = False
        self.aliases = []
        self.aliases.append(name)
    
    def add_alias(self, alias):
        self.aliases.append(alias)
        if "util" in alias.lower() or "helper" in alias.lower():
            self.util = True
    
    def set_off(self):
        self.off = True



def get_file(rename_record:str) -> tuple[dict,list]:
    """Generates a record of known rename files

    Args:
        rename_record (str): the path to the rename records file to analyze

    Returns:
        tuple[dict,list]: a dictionary of files to their Alias object and a list of all alias objects
    """
    data = {}
    alias_list = []
    with open(rename_record, 'r') as file:
        for line in file:
            lines = line.strip().split(",")
            temp_node = None
            for name in lines:
                if temp_node is None:
                    temp_node = Alias(name)
                else:
                    temp_node.add_alias(name)
                data[name] = temp_node
            alias_list.append(temp_node)
    return data, alias_list


def get_vhp(offender_path: str, vhp_project_name: str) -> list:
    """builds a list of known offender files

    Args:
        offender_path (str): the path to the offender file VHP data
        vhp_project_name (str): the string reperesentation of the project as used in the VHP offender file records

    Returns:
        list: a list of offender files
    """
    project_offenders = []
    data = None
    with open(offender_path,'r') as file:
        data = json.load(file)
    for entry in data:
        if entry['project_name'] == vhp_project_name:
            project_offenders.append(entry['filepath'])
    return project_offenders


def analysis(project_offenders: list, alias_dict: dict, alias_list: list, project_name:str) -> None:
    """Performs odds ratio calculations

    Args:
        project_offenders (list): the list of known offender files
        alias_dict (dict): the dictionary of files to their alias objects
        alias_list (list): the list of all alias objects
        project_name (str): the string representation of the project's name
    """
    language_dict = {
        "C/C++": set(['c','ec','pgc','h','cc','cpp','cxx','c++','pcc','ino','hh','hpp','hxx','inl','ipp']),
        "Java": set(['java']),
        "Python": set(['py','pyw','pyi']),
        "JavaScirpt": set(['js','mjs','jsx']),
    }
    for entry in project_offenders:
        if entry in alias_dict:
            alias_dict[entry].set_off()
    util_off = 0
    util_non_off = 0
    util_total = 0
    non_util_off = 0
    non_util_non_off = 0
    non_util_total = 0
    for alias in alias_list:
        if alias.off:
            if alias.util:
                util_off += 1
                util_total += 1
            else:
                non_util_off += 1
                non_util_total += 1
        else:
            if alias.util:
                util_non_off += 1
                util_total += 1
            else:
                non_util_non_off += 1
                non_util_total += 1
    print("Project: " + project_name)
    print("All Extensions: Tests Included")
    if util_non_off > 0 and non_util_non_off > 0 and non_util_off > 0:
        print("Odds Ratio:" + str((util_off/util_non_off)/(non_util_off/(non_util_non_off))))
    print("Total Util Files: " + str(util_total))
    print("total Non-Util Files: " + str(non_util_total))
    print("Util Offenders: " + str(util_off))
    print("Non-Util Offenders: " + str(non_util_off))

    util_off = 0
    util_non_off = 0
    util_total = 0
    non_util_off = 0
    non_util_non_off = 0
    non_util_total = 0
    for alias in alias_list:
        if alias.test:
            continue
        if alias.off:
            if alias.util:
                util_off += 1
                util_total += 1
            else:
                non_util_off += 1
                non_util_total += 1
        else:
            if alias.util:
                util_non_off += 1
                util_total += 1
            else:
                non_util_non_off += 1
                non_util_total += 1
    print("Project: " + project_name)
    print("All Extensions: Tests Excluded")
    if util_non_off > 0 and non_util_non_off > 0 and non_util_off > 0:
        print("Odds Ratio:" + str((util_off/util_non_off)/(non_util_off/(non_util_non_off))))
    print("Total Util Files: " + str(util_total))
    print("total Non-Util Files: " + str(non_util_total))
    print("Util Offenders: " + str(util_off))
    print("Non-Util Offenders: " + str(non_util_off))

    for language in language_dict:
        util_off = 0
        util_non_off = 0
        util_total = 0
        non_util_off = 0
        non_util_non_off = 0
        non_util_total = 0
        for alias in alias_list:
            if alias.name.split(".")[-1] not in language_dict[language]:
                continue
            if alias.off:
                if alias.util:
                    util_off += 1
                    util_total += 1
                else:
                    non_util_off += 1
                    non_util_total += 1
            else:
                if alias.util:
                    util_non_off += 1
                    util_total += 1
                else:
                    non_util_non_off += 1
                    non_util_total += 1
        print("Project: " + project_name)
        print("Language: " + language + " Tests Included")
        if util_non_off > 0 and non_util_non_off > 0 and non_util_off > 0:
            print("Odds Ratio:" + str((util_off/util_non_off)/(non_util_off/(non_util_non_off))))
        print("Total Util Files: " + str(util_total))
        print("total Non-Util Files: " + str(non_util_total))
        print("Util Offenders: " + str(util_off))
        print("Non-Util Offenders: " + str(non_util_off))

        for language in language_dict:
            util_off = 0
            util_non_off = 0
            util_total = 0
            non_util_off = 0
            non_util_non_off = 0
            non_util_total = 0
            for alias in alias_list:
                if alias.test:
                    continue
                if alias.name.split(".")[-1] not in language_dict[language]:
                    continue
                if alias.off:
                    if alias.util:
                        util_off += 1
                        util_total += 1
                    else:
                        non_util_off += 1
                        non_util_total += 1
                else:
                    if alias.util:
                        util_non_off += 1
                        util_total += 1
                    else:
                        non_util_non_off += 1
                        non_util_total += 1
            print("Project: " + project_name)
            print("Language: " + language + " Tests Excluded")
            if util_non_off > 0 and non_util_non_off > 0 and non_util_off > 0:
                print("Odds Ratio:" + str((util_off/util_non_off)/(non_util_off/(non_util_non_off))))
            print("Total Util Files: " + str(util_total))
            print("total Non-Util Files: " + str(non_util_total))
            print("Util Offenders: " + str(util_off))
            print("Non-Util Offenders: " + str(non_util_off))

        


def main():
    alias_dict, alias_list = get_file("rename_records/linux.csv")
    offenders = get_vhp("vhp_records/offender_files.json", "Linux Kernel")
    analysis(offenders, alias_dict, alias_list, "Linux")


if __name__ == '__main__':
    main()
