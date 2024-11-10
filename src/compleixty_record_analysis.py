"""Performs complexity analysis given the collected output from SCC, requires manual configuration of target files and directories
"""

import os
import csv
import statistics

def get_files(comeplxity_data_dir:str) -> list[str]:
    """_summary_

    Args:
        comeplxity_data_dir (str): the directory where the desired complexity files are stored

    Returns:
        list[str]: list of files containing scc output
    """
    files = os.listdir(comeplxity_data_dir)
    # print(files)
    to_return = []
    for file in files:
        if "unique" in file:
            to_return.append(file)
    return to_return


def analyze(file_list: list[str], complexity_data_dir: str, project:str) -> tuple[dict, dict]:
    """Performs the analysis of the scc files

    Args:
        file_list (list[str]): list of the scc output files to analyze
        complexity_data_dir (str): the directory containing the files to analyze
        project (str): the project under analysis

    Returns:
        tuple[dict, dict]: dictionaries containing the collected data. The first being inclusive of test files, the second being exclusive of tests
    """

    data = {}
    data_no_test = {}

    for file in file_list:
        date = file.split("_")[0]
        data[date] = [{},{}]
        data_no_test[date] = [{},{}]
        with open(f"{complexity_data_dir}/{file}") as f:
            results = csv.DictReader(f)
            for row in results:
                if project == "chromium" and "thirdparty" in row["Provider"]:
                    continue
                else:
                    if "util" in row["Provider"].lower() or "helper" in row["Provider"].lower():
                        if row["Language"] in data[date][0]:
                            data[date][0][row["Language"]].append((float(row["Complexity"]), float(row["Code"]), float(row["ULOC"])))
                        else:
                            data[date][0][row["Language"]] = [(float(row["Complexity"]), float(row["Code"]), float(row["ULOC"]))]
                    else:
                        if row["Language"] in data[date][1]:
                            data[date][1][row["Language"]].append((float(row["Complexity"]), float(row["Code"]), float(row["ULOC"])))
                        else:
                            data[date][1][row["Language"]] = [(float(row["Complexity"]), float(row["Code"]), float(row["ULOC"]))]
                    if "test" not in row["Provider"].lower():
                        if "util" in row["Provider"].lower() or "helper" in row["Provider"].lower():
                            if row["Language"] in data_no_test[date][0]:
                                data_no_test[date][0][row["Language"]].append((float(row["Complexity"]), float(row["Code"]), float(row["ULOC"])))
                            else:
                                data_no_test[date][0][row["Language"]] = [(float(row["Complexity"]), float(row["Code"]), float(row["ULOC"]))]
                        else:
                            if row["Language"] in data_no_test[date][1]:
                                data_no_test[date][1][row["Language"]].append((float(row["Complexity"]), float(row["Code"]), float(row["ULOC"])))
                            else:
                                data_no_test[date][1][row["Language"]] = [(float(row["Complexity"]), float(row["Code"]), float(row["ULOC"]))]
    return data, data_no_test


def calculate_results(data:dict) -> None:
    """Calculates total metrics based on the SCC data

    Args:
        data (dict): The data to process as produced by the analyze function of this module
    """
    util = {}
    util_results = {}
    non = {}
    non_results = {}
    util_lines = {}
    non_lines = {}
    util_uloc = {}
    non_uloc = {}
    for day in data:
        util[day] = {}
        non[day] = {}
        overall_util = 0
        overall_code_util = 0
        overall_ucode_util = 0
        overall_non = 0
        overall_code_non = 0
        overall_ucode_non = 0
        for language in data[day][0]:
            l_util = 0
            l_code_util = 0
            l_ucode_util = 0
            for entry in data[day][0][language]:
                l_util += entry[0]
                l_code_util += entry[1]
                l_ucode_util += entry[2]
            util[day][language] = (l_util, l_code_util, l_ucode_util)
            overall_util += l_util
            overall_code_util += l_code_util
            overall_ucode_util += l_ucode_util
        for language in data[day][1]:
            l_non = 0
            l_code_non = 0
            l_ucode_non = 0
            for entry in data[day][1][language]:
                l_non += entry[0]
                l_code_non += entry[1]
                l_ucode_non += entry[2]
            non[day][language] = (l_non, l_code_non, l_ucode_non)
            overall_non += l_non
            overall_code_non += l_code_non
            overall_ucode_non += l_ucode_non
    for day in util:
        if util[day] == {}:
            continue
        total_uloc = 0
        total_lines = 0
        total_complexity = 0
        for language in util[day]:
            total_lines += util[day][language][1]
            total_complexity += util[day][language][0]
            total_uloc += util[day][language][2]
        # print(util)
        util_results[day] = total_complexity/total_lines
        util_lines[day] = total_lines
        util_uloc[day]  = total_uloc
    for day in non:
        if non[day] == {}:
            continue
        total_uloc = 0
        total_lines = 0
        total_complexity = 0
        for language in non[day]:
            total_lines += non[day][language][1]
            total_complexity += non[day][language][0]
            total_uloc += non[day][language][2]
        non_results[day] = total_complexity/total_lines
        non_lines[day] = total_lines
        non_uloc[day] = total_uloc
    # print(util_results)
    # print(non_results)
    util_list = list(util_results.values())
    non_list = list(non_results.values())

    util_mean = statistics.mean(util_list)
    util_std = statistics.stdev(util_list)
    non_mean = statistics.mean(non_list)
    non_std = statistics.stdev(non_list)

    util_line_list = list(util_lines.values())
    non_line_list = list(non_lines.values())
    util_line_mean = statistics.mean(util_line_list)
    util_line_std = statistics.stdev(util_line_list)
    non_line_mean = statistics.mean(non_line_list)
    non_line_std = statistics.stdev(non_line_list)

    util_uloc_list = list(util_uloc.values())
    non_uloc_list = list(non_uloc.values())
    util_uloc_mean = statistics.mean(util_uloc_list)
    util_uloc_std = statistics.stdev(util_uloc_list)
    non_uloc_mean = statistics.mean(non_uloc_list)
    non_uloc_std = statistics.stdev(non_uloc_list)
    
    print("Util Mean: ", util_mean)
    print("Util STD: ", util_std)
    print("Non Mean: ", non_mean)
    print("Non STD: ", non_std)

    print("Util Line Mean: ", util_line_mean)
    print("Util Line STD: ", util_line_std)
    print("Non Line Mean: ", non_line_mean)
    print("Non Line STD: ", non_line_std)

    print("Util Uloc Mean: ", util_uloc_mean)
    print("Util Uloc STD: ", util_uloc_std)
    print("Non Uloc Mean: ", non_uloc_mean)
    print("Non Uloc STD: ", non_uloc_std)
    
def main():
    files = get_files("complexity_data/chromium")
    data, no_test = analyze(files, "complexity_data/chromium", "chromium")
    print("W/Test")
    calculate_results(data)
    print("Wo/Test")
    calculate_results(no_test)

if __name__ == '__main__':
    main()