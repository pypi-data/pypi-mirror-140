import shutil
from quickcsv.file import *
from collections import OrderedDict
import os

def divide_by_tag(meta_csv_file,raw_text_folder,output_folder,list_category, start_year=2010,end_year=2021, tag_field="tag",keyword_field="keyword",time_field="time",id_field="Id",prefix_filename=""):

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    list_item = qc_read(meta_csv_file)

    dict_field_news = OrderedDict()
    dict_field_news_count = OrderedDict()
    dict_field_news_yearly_count = OrderedDict()

    dict_company = OrderedDict()
    total_num=len(list_item)
    for idx, item in enumerate(list_item):
        # print(f"{idx}/{total_num}")
        tag = item[tag_field]
        keyword=""
        if keyword_field in item.keys():
            keyword = item[keyword_field]
        Id = item[id_field]
        time = item[time_field]
        year = ""
        if '-' in time:
            year = time.split("-")[0]

        model = {
            "Id": Id,
            "Year": year,
            "Field": tag,
            "Keyword": keyword
        }
        # print(model)
        if year == "":
            continue

        text_path = f"{raw_text_folder}/{prefix_filename}{Id}.txt"
        if not os.path.exists(text_path):
            continue

        text = open(text_path, 'r', encoding='utf-8').read()

        if keyword.strip()!="":
            if keyword not in text:
                continue

        target_folder = f"{output_folder}/{tag}"
        if '/' in tag:
            continue
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)
        target_file = f"{target_folder}/{Id}.txt"
        shutil.copy(text_path, target_file)

        if tag in dict_field_news:
            dict_field_news[tag].append(model)
            dict_field_news_count[tag] += 1
            if year in dict_field_news_yearly_count[tag]:
                dict_field_news_yearly_count[tag][year].append(Id)
            else:
                dict_field_news_yearly_count[tag][year] = []
                dict_field_news_yearly_count[tag][year].append(Id)
        else:
            dict_field_news[tag] = [model]
            dict_field_news_count[tag] = 1
            dict_field_news_yearly_count[tag] = OrderedDict()
            dict_field_news_yearly_count[tag][year] = []
            dict_field_news_yearly_count[tag][year].append(Id)



        # print()
    print()
    dict_field_news_count_sorted = OrderedDict(
        sorted(dict_field_news_count.items(), key=lambda obj: obj[1], reverse=True))

    print("Category\tNews Number")
    for k in dict_field_news_count_sorted:
        print(f"{k}\t{dict_field_news_count_sorted[k]}")
    print()

    # stat by category and sub category by year
    if list_category!=None:
        print("Year\t" + "\t".join(list_category))
        for year in range(start_year, end_year):
            list_num = []
            for field_code in list_category:
                num = 0
                if field_code in dict_field_news_yearly_count:
                    if str(year) in dict_field_news_yearly_count[field_code]:
                        num = len(dict_field_news_yearly_count[field_code][str(year)])
                list_num.append(str(num))
            line = "\t".join(list_num)
            print(f"{year}\t{line}")

    print()

