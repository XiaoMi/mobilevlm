# compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):
#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.


import argparse
import subprocess
import os, sys
import json

sys.path.append(os.getcwd())
print(sys.path)
import time

def dict2txt(path,path2):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)


    with open(path2, 'w', encoding='utf-8') as f:
        for key in data_dict:
            tempstr=data_dict[key]
            if isinstance(tempstr,list):
                tempstr=str(tempstr)
            f.write(key+"\t"+str(tempstr)+"\n")
        f.close()

if __name__ == '__main__':
    directory_path ="../corpus/random_walk/Qunar_graph_8102"+"/"

    dict2txt(directory_path+"data_unique2all.json",directory_path+"data_unique2all.txt")
    dict2txt(directory_path+"data_unique2action.json",directory_path+"data_unique2action.txt")
    dict2txt(directory_path+"data_all2unique.json",directory_path+"data_all2unique.txt")
    dict2txt(directory_path+"all_action_id.json",directory_path+"all_action_id.txt")
    dict2txt(directory_path+"all_page_id.json",directory_path+"all_page_id.txt")
