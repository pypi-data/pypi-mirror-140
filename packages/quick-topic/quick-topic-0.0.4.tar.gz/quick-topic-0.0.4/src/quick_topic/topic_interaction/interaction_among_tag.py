from quickcsv.file import *
from collections import OrderedDict
import numpy as np

'''
show specific topic trends over time 
'''

def interaction_among_tag(list_category,weights_folder,label_names,list_topics,filter_keywords=None,top_keywords_n=15,max_num_for_interaction_estimation=15):

    list_year = []
    list_all_words = []

    dict_keyword_weights = {}
    dict_topic_topic_keywords = OrderedDict()
    import os
    for field in list_category:
        if not os.path.exists(f"{weights_folder}/{field}_k.csv"):
            continue
        k_lines = open(f"{weights_folder}/{field}_k.csv", 'r', encoding='utf-8').readlines()
        v_lines = open(f"{weights_folder}/{field}_v.csv", 'r', encoding='utf-8').readlines()
        if field not in dict_keyword_weights:
            dict_keyword_weights[field] = {}

        for idx, item in enumerate(k_lines):
            fs_k = item.strip().split(",")
            fs_v = v_lines[idx].strip().split(",")
            for kid, k in enumerate(fs_k):
                weight = float(fs_v[kid])
                keyword = k
                if keyword not in list_all_words:
                    list_all_words.append(keyword)
                if keyword not in dict_keyword_weights[field].keys():
                    dict_keyword_weights[field][keyword] = [weight]
                else:
                    dict_keyword_weights[field][keyword].append(weight)

    # 统计每个行业的主要关键词
    for field in dict_keyword_weights:
        if field not in dict_topic_topic_keywords:
            dict_topic_topic_keywords[field] = OrderedDict()
        for k in dict_keyword_weights[field]:
            # if k not in carbon2_keywords:
            #    continue
            if filter_keywords!=None:
                if k in filter_keywords:
                    continue
            list_w = dict_keyword_weights[field][k]
            total_w = np.sum(list_w)
            if k not in dict_topic_topic_keywords:
                dict_topic_topic_keywords[field][k] = total_w

        dict_topic_topic_keywords[field] = OrderedDict(
            sorted(dict_topic_topic_keywords[field].items(), key=lambda obj: obj[1], reverse=True))

    # find common keywords with all
    list_common_words = []
    for k in list_all_words:
        list_common_words.append(k)

    print()


    for field in dict_keyword_weights:
        print(field)
        for topic in list_topics:
            list_v = []
            total_w = 0
            for keyword in topic:
                w = 0
                if keyword in dict_keyword_weights[field]:
                    w = float(np.sum(dict_keyword_weights[field][keyword]))

                list_v.append(w)
            total_w = np.sum(list_v)
            print(topic, round(total_w, 4))
        print()

    print()
    print("Tag\tTopKeywords\t"+"\t".join(label_names))
    for field in dict_topic_topic_keywords:
        dict_keywords = dict_topic_topic_keywords[field]
        top_keywords = list(dict_keywords.keys())[:top_keywords_n]
        # 计算每个主题的关键词权重和
        list_v = []
        total_w = 9
        for keyword in top_keywords:
            w = 0
            if keyword in dict_keyword_weights[field]:
                w = float(np.sum(dict_keyword_weights[field][keyword]))
            list_v.append(w)
        total_w = np.sum(list_v)
        # 计算每个主题的之和
        list_total_w = []
        for topic in list_topics:
            list_v = []
            total_w = 0
            for keyword in topic:
                w = 0
                if keyword in dict_keyword_weights[field]:
                    w = float(np.sum(dict_keyword_weights[field][keyword]))

                list_v.append(w)
            total_w = np.sum(list_v)
            list_total_w.append(str(round(total_w, 4)))

        print(field + "\t" + ','.join(top_keywords) + "\t" + str(round(total_w, 4)) + "\t" + "\t".join(list_total_w))
    # ##################################KInteraction#########################################
    def get_common_words(ks1, ks2, vs1, vs2):
        list_common_words = []
        list_w = []
        for k in ks1:
            if k in ks1 and k in ks2:
                list_common_words.append(k)
                v1 = vs1[k]
                v2 = vs2[k]
                list_w.append((v1 + v2) / 2)
        dict_w = OrderedDict()
        for idx, k in enumerate(list_common_words):
            dict_w[k] = list_w[idx]
        dict_w = OrderedDict(sorted(dict_w.items(), key=lambda obj: obj[1], reverse=True))
        list_w = []
        for k in dict_w:
            list_w.append(dict_w[k])
        return list(dict_w.keys()), list_w

    print()
    list_field_keyword = list(dict_topic_topic_keywords.keys())
    print("TagInteraction\tSharedKeywords\tInteractionStrength")
    for idx1 in range(0, len(list_field_keyword) - 1):
        field1 = list_field_keyword[idx1]
        dict_keywords1 = dict_topic_topic_keywords[field1]
        top_keywords1 = list(dict_keywords1.keys())
        for idx2 in range(idx1 + 1, len(list_field_keyword)):
            field2 = list_field_keyword[idx2]
            dict_keywords2 = dict_topic_topic_keywords[field2]
            top_keywords2 = list(dict_keywords2.keys())
            list_w, list_v = get_common_words(top_keywords1, top_keywords2, dict_keywords1, dict_keywords2)
            max_num = max_num_for_interaction_estimation
            list_w = list_w[:max_num]
            list_v = list_v[:max_num]
            if len(list_w) != 0:
                keyword_list = ','.join(list_w)
                total_w = round(np.sum(list_v), 4)

                print(f"{field1}<-->{field2}\t{keyword_list}\t{total_w}")
