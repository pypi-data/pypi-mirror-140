import shutil
from quickcsv.file import *
from collections import OrderedDict
import os

def divide_by_tag(meta_csv_file,raw_text_folder,output_folder,category_path, start_year=2010,end_year=2021, tag_field="tag",keyword_field="keyword",time_field="time",id_field="Id"):

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    list_item = qc_read(meta_csv_file)

    dict_field_news = OrderedDict()
    dict_field_news_count = OrderedDict()
    dict_field_news_yearly_count = OrderedDict()

    dict_company = OrderedDict()
    total_num=len(list_item)
    for idx, item in enumerate(list_item):
        print(f"{idx}/{total_num}")
        tag = item[tag_field]
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

        text_path = f"{raw_text_folder}/{Id}.txt"
        if not os.path.exists(text_path):
            continue

        text = open(text_path, 'r', encoding='utf-8').read()

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

        if keyword in dict_company.keys():
            dict_company[keyword] += 1
        else:
            dict_company[keyword] = 1

        # print()
    print()
    dict_field_news_count_sorted = OrderedDict(
        sorted(dict_field_news_count.items(), key=lambda obj: obj[1], reverse=True))

    print("行业\t相关新闻数")
    for k in dict_field_news_count_sorted:
        print(f"{k}\t{dict_field_news_count_sorted[k]}")

    lines = open(category_path, "r", encoding='utf-8').readlines()
    dict_keywords = {}
    for idx, l in enumerate(lines):
        if idx == 0:
            continue
        l = l.strip()
        ls = l.split(",")
        tag = ls[2]
        words = ls[1].split("（")[0]
        if tag in dict_keywords:
            dict_keywords[tag].append(words)
        else:
            dict_keywords[tag] = [words]
    print()
    print("年份\t" + "\t".join(dict_keywords.keys()))
    for year in range(start_year, end_year):
        list_num = []
        for field_code in dict_keywords.keys():
            num = 0
            if field_code in dict_field_news_yearly_count:
                if str(year) in dict_field_news_yearly_count[field_code]:
                    num = len(dict_field_news_yearly_count[field_code][str(year)])
            list_num.append(str(num))
        line = "\t".join(list_num)
        print(f"{year}\t{line}")

    print()
    dict_company = OrderedDict(sorted(dict_company.items(), key=lambda obj: obj[1], reverse=True))

    print("公司\t相关新闻数")
    total = 0
    for k in dict_company:
        total += 1
        print(f"{k}\t{dict_company[k]}")
        if total >= 20:
            break
