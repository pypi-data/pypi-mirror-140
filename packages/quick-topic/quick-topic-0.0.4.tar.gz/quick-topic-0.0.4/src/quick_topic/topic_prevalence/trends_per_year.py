from quickcsv.file import *
import os

'''
show specific topic trends over time 
'''

def get_trends(start_year,end_year, label_names,list_topics, root_path="results/news_by_year_results50"):
    list_year_v = []
    list_year = []
    list_all_words = []

    year_range = range(start_year, end_year+1)

    for year in year_range:
        dict_keyword = {}
        if not os.path.exists(f"{root_path}/{year}_k.csv"):
            continue
        k_lines = open(f"{root_path}/{year}_k.csv", 'r', encoding='utf-8').readlines()
        v_lines = open(f"{root_path}/{year}_v.csv", 'r', encoding='utf-8').readlines()
        for idx, item in enumerate(k_lines):
            fs_k = item.strip().split(",")
            fs_v = v_lines[idx].strip().split(",")
            for kid, k in enumerate(fs_k):
                weight = float(fs_v[kid])
                keyword = k
                if keyword not in list_all_words:
                    list_all_words.append(keyword)
                if keyword not in dict_keyword.keys():
                    dict_keyword[keyword] = [weight]
                else:
                    dict_keyword[keyword].append(weight)
        list_year_v.append(year)
        list_year.append(dict_keyword)

    # find common keywords with all
    list_common_words = []
    for k in list_all_words:
        list_common_words.append(k)

    import numpy as np

    list_year_common_words = []

    # estimate freq of common keyword in each year
    for idx, dict_keywords in enumerate(list_year):
        dict_common_keywords = {}
        for k in list_common_words:
            avg_w = 0
            if k in dict_keywords.keys():
                avg_w = np.mean(dict_keywords[k])
            dict_common_keywords[k] = round(avg_w, 4)
        list_year_common_words.append(dict_common_keywords)

    print("======================Topic Prevalence of each common keyword==============================")

    # get table
    def show_table(fields=None):
        header = "Year\t"
        for k in list_common_words:
            if fields == None or (fields != None and k in fields):
                header += k + "\t"

        print(header)
        for idx, dict_k in enumerate(list_year_common_words):
            list_v = []
            year = list_year_v[idx]
            for k in list_common_words:
                if fields == None or (fields != None and k in fields):
                    list_v.append(str(dict_k[k]))
            print(str(year) + "\t" + "\t".join(list_v))

    show_table()
    print()

    print("==============Topic Prevalence Change per specific topics================")

    print()

    import math
    list_topic_prevalence = []
    header = "年份\t"
    header += "\t".join(label_names)
    print(header)
    for idx, dict_keywords in enumerate(list_year):
        list_topic_w = []
        for a_topic in list_topics:
            list_v = []
            total_w = 0
            for k in a_topic:
                w = 0
                if k in dict_keywords:
                    w = np.sum(dict_keywords[k])
                total_w += w
                list_v.append(w)
            list_topic_w.append(str(round(total_w, 4)))
        line_v = '\t'.join(list_topic_w)
        print(f"{list_year_v[idx]}\t{line_v}")



