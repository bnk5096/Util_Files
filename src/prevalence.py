"""Performs util-prevalence related calculations and analysis. Requires some manual configuration.
"""

def percentage(rename_dir: str, out:str, extension_dict:dict) -> None:
    """Performs basic prevalence percentage-based calculations

    Args:
        rename_dir (str): the rename record file to analyze
        out (str): the file to write to
        extension_dict (dict): the map of valid languages to valid extensions
    """
    results = {}
    for language in extension_dict:
        util_w_test = 0
        non_util_w_test = 0
        util = 0
        non_util = 0
        with open(rename_dir, 'r') as file:
            for line in file:
                sline = line.strip().lower()
                slines = sline.split(",")
                sline_exts = slines[0].split(".")
                if len(sline_exts) > 1:
                    if sline_exts[1] not in extension_dict[language]:
                        continue
                else:
                    if sline_exts[0] not in extension_dict[language]:
                        continue
                if "util" in sline or "helper" in sline:
                    util_w_test += 1
                    if "test" not in sline:
                        util += 1
                else:
                    non_util_w_test += 1
                    if "test" not in sline:
                        non_util += 1
            results[language] = (util_w_test, non_util_w_test, util, non_util)
    with open(out, 'w') as file:
        for key in results:
            file.write("Language: " + key + "\n")
            file.write("Total Files W/Test: " + str(results[key][0] + results[key][1]) + "\n")
            file.write("Total Util W/Test: " + str(results[key][0]) + "\n")
            file.write("Total Non-Util W/Test: " + str(results[key][1]) + "\n")
            if results[key][1] + results[key][0] > 0:
                file.write("W/Test Percentage: " + str(results[key][0]/(results[key][0] + results[key][1])) + "\n")
            file.write("Total Files: " + str(results[key][2] + results[key][3]) + "\n")
            file.write("Total Util: " + str(results[key][2]) + "\n")
            file.write("Total Non-Util: " + str(results[key][3]) + "\n")
            if results[key][2] + results[key][3] > 0:
                file.write("Percentage: " + str(results[key][2]/(results[key][2] + results[key][3])) + "\n")
            file.write("-" * 25 + "\n\n")


def concentration(rename_record: str, out: str):
    """Performs analysis of util file concentration

    Args:
        rename_record (str): the path to the rename record to analyze
        out (str): the file to write to
    """
    data = {}
    data_no_test = {}
    with open(rename_record, 'r') as file:
        for line in file:
            sline = line.strip().lower()
            if "util" in sline or "helper" in sline:
                    slines = sline.split(",")
                    to_measure = None
                    for entry in slines:
                        if "util" in entry or "helper" in entry:
                            to_measure = entry
                            break
                    step_through = to_measure.split("/")
                    # step_through.reverse()
                    for i in range(len(step_through)):
                        if "util" in step_through[i] or "helper" in step_through[i]:
                            if len(step_through) - i - 1 in data:
                                data[len(step_through) - i - 1].append(to_measure)
                            else:
                                data[len(step_through) - i - 1] = [to_measure]
                            if "test" not in sline:
                                if len(step_through) - i - 1 in data_no_test:
                                    data_no_test[len(step_through) - i - 1].append(to_measure)
                                else:
                                    data_no_test[len(step_through) - i - 1] = [to_measure]
                            break
    with open(out, 'w') as file:
        file.write("Including Tests:\n")
        for key in data:
            file.write(str(key) + ": " + str(len(data[key])) + "\n")
            file.write(str(data[key]) + "\n")
        file.write("-"*25 + "\n")
        file.write("Excluding Tests:\n")
        for key in data_no_test:
            file.write(str(key) + ": " + str(len(data_no_test[key])) + "\n")
            file.write(str(data_no_test[key]) + "\n")

                        

def promotions(rename_record:str, out:str) -> None:
    """Performs analysis of promotions, demotions, and oscilations

    Args:
        rename_record (str): the path to the rename record to analyze
        out (str): the file to write to
    """
    change = set()
    promotion = []
    demotion = []
    both = []
    all = []
    with open(rename_record, 'r') as file:
        for line in file:
            lline = line.strip().lower()
            if len(lline.split(",")) > 1:
                all.append(lline)
            if 'util' in lline or 'helper' in line:
                splits = lline.split(",")
                for entry in splits:
                    if 'util' not in entry and 'helper' not in entry:
                        change.add(line.strip())
    for entry in change:
        last_seen_was_util = None
        promotion_seen = False
        demotion_seen = False
        for path in entry.lower().split(","):
            if last_seen_was_util is None:
                if 'util' in path or 'helper' in path:
                    last_seen_was_util = True
                else:
                    last_seen_was_util = False
            if last_seen_was_util:
                if 'util' in path or 'helper' in path:
                    pass
                else:
                    last_seen_was_util = False
                    promotion_seen = True
            else:
                if 'util' in path or 'helper' in path:
                    last_seen_was_util = True
                    demotion_seen = True
                else:
                    pass
        if promotion_seen and demotion_seen:
            both.append(entry)
        elif promotion_seen:
            promotion.append(entry)
        elif demotion_seen:
            demotion.append(entry)
    with open(out, 'w') as file:
        file.write("Both: " + str(len(both)) + "\n")
        for entry in both:
            file.write(entry + "\n")
        file.write("Promotion: " + str(len(promotion)) + "\n")
        for entry in promotion:
            file.write(entry + "\n")
        file.write("Demotion: " + str(len(demotion)) + "\n")
        for entry in demotion:
            file.write(entry + "\n")
        file.write("Total Renames:" + str(len(all)) + "\n")        
 
def extension_filter(extensions_dir: str) -> dict:
    """Generates a dictionary of languages to valid extensions

    Args:
        extensions_dir (str): the path to the file containing known extensions

    Returns:
        dict: a dictionary mapping languages to extensions
    """
    master_dict = {
        "C/C++": set(['c','ec','pgc','h','cc','cpp','cxx','c++','pcc','ino','hh','hpp','hxx','inl','ipp']),
        "Java": set(['java']),
        "Python": set(['py','pyw','pyi']),
        "JavaScirpt": set(['js','mjs','jsx']),
    }
    full_list = set()
    with open(extensions_dir) as file:
        for line in file:
            full_list.add(line.strip())
    extensions_dict = {"All": full_list}
    for key in master_dict:
        extensions_dict[key] = master_dict[key]
    return extensions_dict

def main():
    x = extension_filter("extension_lists/linux.txt")
    percentage("rename_records/linux.csv", "prevalence_data/linux.txt", x)
    concentration("rename_records/linux.csv","directory_depths/linux.txt")
    promotions('rename_records/linux.csv', 'promotion_data/linux.txt')

if __name__ == '__main__':
    main()
