# -*- coding: utf-8 -*-
"""
Read the txt files containing the raw design tables from Chen, Sun and Wu (1993), format them and store them
in a new excel file, with one sheet per run size.
Created on Wed Jan 19 15:57:58 2022

@author: Alexandre Bohyn - alexandre dot bohyn [at] kuleuven dot be
"""
import os

# % Packages
import re

import pandas as pd

# Function to format the file


def format_file(fname: str):
    # Create dictionary for the designs
    designs_dict = pd.DataFrame()
    # Run size and author are in filename
    regex_match = re.match(r"^(\w[^0-9]+)_(\d+)_?(\d?)", fname)
    n_runs = int(regex_match.group(2))
    author = regex_match.group(1).capitalize()

    with open("raw_data/" + fname, "r") as f:
        text_by_lines = f.readlines()
    if author == "Xu":
        text_by_lines[0] = ""
    text = "".join(text_by_lines)

    # Line is split in index of the design and rest of the informations
    # If author is Xu, there are two types of indices: XX-XX.XX and XX-XX, so the .XX is optional in the regex search
    if author == "Xu" and n_runs != 128:
        regex_pattern = r"\d+-\d+[\.\d+]*(?!,)"
    elif n_runs == 128:
        regex_pattern = r"\d+-\d+\.\d+(?!,)"
    # If author is CSW, all indices are XX-XX.XX
    else:
        regex_pattern = r"\d+-\d+\.\d+"
    col_info = [
        c for c in re.split(regex_pattern, text) if c is not None and len(c) > 0
    ]
    design_names = [i.group(0) for i in re.finditer(regex_pattern, text)]

    # Loop through the names
    for num, name in enumerate(design_names):
        # Base info extracted from names
        info = col_info[num]
        info_list = list(map(int, re.findall(r"\d+", name)))
        if len(info_list) == 2:
            info_list.append(1)
        n, p, i = info_list
        # XU: If the column numbers contains text, replace it
        string_info = re.search(r"same as design (\d+-\d+\.\d+), plus", info)
        if string_info is not None:
            # Find the reference columns
            ref_design = string_info.group(1)
            is_ref_design = designs_dict["index"] == ref_design
            ref_cols = designs_dict[is_ref_design]["cols"].tolist()[0]
            ref_cols = re.sub(",", " ", ref_cols)
            # Replace it in the string
            new_info = re.sub(r"same as design (\d+-\d+\.\d+), plus", ref_cols, info)
            info = new_info
        # CSW: if we have x-y, then all numbers between x and y should be there
        if author == "Csw":
            range_number_match = re.finditer(r"(\d+)-(\d+)", info)
            if range_number_match:
                for match in range_number_match:
                    missing_range = list(
                        range(int(match.group(1)), int(match.group(2)) + 1)
                    )
                    missing_range_str = " ".join(list(map(str, missing_range)))
                    info = re.sub(
                        f"{missing_range[0]}-{missing_range[-1]}",
                        missing_range_str,
                        info,
                    )
        # Remove decimal for thousands
        info = re.sub(",", "", info)
        # All numbers from information extracted from the raw text
        nums = list(map(int, re.findall(r"\d+", info)))
        # Xu does not provide number of CFI
        if author == "Xu":
            # If there aren't enough information, there are no column numbers
            if len(nums) < p:
                cols = []
                wlp = nums
            # p last numbers must be the added factors and the rest is the WLP
            else:
                cols = nums[-p:]
                wlp = nums[:-p]
            c = None
        else:
            cols = nums[:p]
            # Dynamic allocation of the WLP size
            wlp = nums[p:-1]
            # Only last number is the CFI
            c = nums[-1]
        design_dict = {
            "author": author,
            "n.runs": n_runs,
            "index": name,
            "n.cols": n,
            "n.added": p,
            "design.rank": i,
            "cols": ",".join(map(str, cols)),
            "wlp": ",".join(map(str, wlp)),
            "clear.2fi": c,
        }
        designs_dict = designs_dict.append(design_dict, ignore_index=True)
    return designs_dict


# % Activation
if __name__ == "__main__":
    # Read file
    table_fnames = os.listdir("raw_data/")
    # Create dictionary for the designs
    designs = pd.DataFrame()
    # Generate new dict and append to intial one
    for table in table_fnames:
        temp_dict = format_file(table)
        designs = designs.append(temp_dict, ignore_index=True)
    designs.to_csv("tables.csv", index=False, float_format="%.0f", na_rep="NA")
