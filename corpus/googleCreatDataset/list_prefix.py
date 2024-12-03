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


def dict2dict(path,path2):
    length=0
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)

        data_count={}
        for key in data_dict:
            list_=key.split("_")
            pre="_".join(list_[:2])
            if pre not in data_count:
                data_count[pre]=1
            else:
                data_count[pre]+=1
    return data_count

def dictcount(path):
    length=0
    triple=0
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        data_dict=json.loads(data)

    for key in data_dict:
        length+=1
        keylist=key.split("_")
        triple+=len(keylist)-1
    return length,triple

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
    count=0

    l_uni=[]
    l_edge=[]
    l_all=[]
    l_a=[]
    l_p=[]
    name=[]
    app=[]


    path1="corpus/arm_01/"
    dirs=os.listdir(path1)
    count_eposide=0
    count_triples=0
    for d in dirs:
        print(d)
        directory_path=path1+d+"/"
        if os.path.exists(directory_path+"data_all2unique.json"):
            print(directory_path)
            print(count)
            count+=1
            dict_unique=dict2dict(directory_path+"data_unique2all.json",directory_path+"data_unique2all.txt")
            l_uni.append(dict_unique)
            name.append("/".join(directory_path.split("/")[-3:-1]))
            app.append(d.split("_")[0])


    dict_postfix={}
    list_posfix=[]
    for index in range(len(name)):
        postfix=name[index].split("_")[-1]
        list_posfix.append(postfix+name[index])
        dict_postfix[postfix+name[index]]=index
    list_posfix.sort()
    print(list_posfix)
    print(dict_postfix)
    new_APP=[]
    new_name=[]
    new_l_uni=[]
    new_l_all=[]
    new_l_a=[]
    new_l_p=[]
    for postfix in list_posfix:
        i=dict_postfix[postfix]
        for key in l_uni[i]:
            new_APP.append(app[i])
            new_name.append(name[i])

            new_l_uni.append(key)
            new_l_all.append(l_uni[i][key])

    #print("count_eposide",count_eposide)

    #print("count_triples",count_triples)
    #print("average steps",float(count_triples)/float(count_eposide))


    data=pd.DataFrame({"APP":new_APP,"name":new_name,"unique_page_num":new_l_uni,"all_page_num":new_l_all,
        })#"all_edge_num":l_edge,

    path="dataStat/"

    data.to_csv(path+"dataPrefix.csv")
