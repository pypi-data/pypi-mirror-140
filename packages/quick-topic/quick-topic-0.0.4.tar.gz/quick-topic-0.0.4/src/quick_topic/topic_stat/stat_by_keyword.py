from quickcsv.file import *
from collections import OrderedDict
import os
def stat_sentence_by_keywords(meta_csv_file,keywords,id_field,raw_text_folder,contains_keyword_in_sentence="",prefix_file_name=""):
    list_g20_news_final = qc_read(csv_path=meta_csv_file)

    list_trans = []

    for item in list_g20_news_final:
        file_id = item[id_field]
        text_path = raw_text_folder + f"\\{prefix_file_name}" + file_id + ".txt"
        if not os.path.exists(text_path):
            continue
        text = open(text_path, 'r', encoding='utf-8').read()
        for line in text.split("\n"):
            if contains_keyword_in_sentence!="":
                if contains_keyword_in_sentence in line:
                    if line not in list_trans:
                        print(line)
                        print()
                        list_trans.append(line)
            else:
                if line not in list_trans:
                    print(line)
                    print()
                    list_trans.append(line)

    # 能源类别

    print("Len of trans: ", len(list_trans))
    dict_keywords = OrderedDict()
    for line in list_trans:
        for k in keywords:
            if k in line:
                if k in dict_keywords:
                    dict_keywords[k] += 1
                else:
                    dict_keywords[k] = 1

    dict_keywords = OrderedDict(sorted(dict_keywords.items(), key=lambda obj: obj[1], reverse=True))

    print("Keyword stat: ")
    for k in dict_keywords:
        print(f"{k}\t{dict_keywords[k]}")

