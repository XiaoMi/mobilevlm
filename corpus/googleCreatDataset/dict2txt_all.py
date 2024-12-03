# compare_image_and_xml(xml_path_1, xml_path_2, threshold_xml, screenshot_filepath_1, screenshot_filepath_2, threshold_image):
#Copyright (C) 2024 Xiaomi Corporation.
#The source code included in this project is licensed under the Apache 2.0 license.


import argparse
import subprocess
import os, sys
import json
import pandas as pd

sys.path.append(os.getcwd())
print(sys.path)
import time

def dict2txt(path,path2):
    length=0
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)


    with open(path2, 'w', encoding='utf-8') as f:
        for key in data_dict:
            tempstr=data_dict[key]
            if isinstance(tempstr,list):
                tempstr=str(tempstr)
            f.write(key+"\t"+str(tempstr)+"\n")
            length+=1
        f.close()
    return length

def loadedge(path,path1,path2):
    length=0
    with open(path1, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_unique2action=json.loads(data)
        file.close()

    count=0
    for name in data_unique2action:
        level_path="/".join(name.split("_")[:-1])+"/"
        #with open(path+level_path+name+"-html.txt", 'r', encoding='utf-8') as f:
        #    html_code=f.read()

        with open(path+level_path+name+".json", 'r', encoding='utf-8') as file:
            data_json = json.load(file)

        action_valid=data_json["action_valid"]
        for temp in action_valid:
            action=temp["action"]
            if action not in  data_unique2action[name]:
                data_unique2action[name].append(action)
        count+=1
        if count %1000==0:
            print(count)


    with open(path1, 'w', encoding='utf-8') as f:
        datajson=json.dumps(data_unique2action)
        json.dump(datajson, f, indent=4,ensure_ascii=False)
        f.write('\n')
        f.close()

    with open(path2, 'w', encoding='utf-8') as f:
        for key in data_unique2action:
            tempstr=data_unique2action[key]
            if isinstance(tempstr,list):
                length+=len(tempstr)
                tempstr=str(tempstr)
            f.write(key+"\t"+str(tempstr)+"\n")
        f.close()
    return length

if __name__ == '__main__':
    #directory_path ="../corpus/random_walk/Qunar_graph_8102"+"/"
    path="corpus/random_walk/"
    dirs=os.listdir(path)


    count=0

    l_uni=[]
    l_edge=[]
    l_all=[]
    l_a=[]
    l_p=[]
    name=[]
    app=[]
    for d in dirs:
        print(d)
        directory_path=path+d+"/"
        if os.path.exists(directory_path+"data_all2unique.json"):
            print(directory_path)
            print(count)
            count+=1
            len_uni=dict2txt(directory_path+"data_unique2all.json",directory_path+"data_unique2all.txt")
            #len_edge=dict2txt(directory_path+"data_unique2action.json",directory_path+"data_unique2action.txt")
            #len_edge=loadedge(directory_path,directory_path+"data_unique2action.json",directory_path+"data_unique2action.txt")
            len_all=dict2txt(directory_path+"data_all2unique.json",directory_path+"data_all2unique.txt")
            len_a=dict2txt(directory_path+"all_action_id.json",directory_path+"all_action_id.txt")
            len_p=dict2txt(directory_path+"all_page_id.json",directory_path+"all_page_id.txt")
            l_uni.append(len_uni)
            #l_edge.append(len_edge)
            l_all.append(len_all)
            l_a.append(len_a)
            l_p.append(len_p)
            name.append("/".join(directory_path.split("/")[-3:-1]))
            app.append(d.split("_")[0])

    path1="corpus/server/arm_01/"
    dirs=os.listdir(path1)
    for d in dirs:
        print(d)
        directory_path=path1+d+"/"
        if os.path.exists(directory_path+"data_all2unique.json"):
            print(directory_path)
            print(count)
            count+=1
            len_uni=dict2txt(directory_path+"data_unique2all.json",directory_path+"data_unique2all.txt")
            #len_edge=dict2txt(directory_path+"data_unique2action.json",directory_path+"data_unique2action.txt")
            #len_edge=loadedge(directory_path,directory_path+"data_unique2action.json",directory_path+"data_unique2action.txt")
            len_all=dict2txt(directory_path+"data_all2unique.json",directory_path+"data_all2unique.txt")
            len_a=dict2txt(directory_path+"all_action_id.json",directory_path+"all_action_id.txt")
            len_p=dict2txt(directory_path+"all_page_id.json",directory_path+"all_page_id.txt")
            l_uni.append(len_uni)
            #l_edge.append(len_edge)
            l_all.append(len_all)
            l_a.append(len_a)
            l_p.append(len_p)
            name.append("/".join(directory_path.split("/")[-3:-1]))
            app.append(d.split("_")[0])

    i=0
    while i < len(app):
        index=-1
        for j in range(i):
            if app[i]==app[j]:
                if l_uni[i]>=l_uni[j]:
                    index=j
                else:
                    index=i
        if index > -1:
            app.pop(index)
            name.pop(index)
            l_uni.pop(index)
            l_all.pop(index)
            #l_edge.pop(index)
            l_a.pop(index)
            l_p.pop(index)
        else:
            i+=1
    data=pd.DataFrame({"APP":app,"name":name,"unique_page_num":l_uni,"all_page_num":l_all,
        "action_vocab":l_a,"page_vocab":l_p})#"all_edge_num":l_edge,

    path="dataStat/"

    data.to_csv(path+"dataStat.csv")
