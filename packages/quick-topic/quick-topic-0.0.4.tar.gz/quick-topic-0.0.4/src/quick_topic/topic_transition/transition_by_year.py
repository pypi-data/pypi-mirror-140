import os
from quickcsv.file import *
from collections import OrderedDict

def show_transition(root_path,keyword,start_year,end_year):

    dict_year_rate = OrderedDict()

    for year in range(start_year, end_year+1):
        year_folder = f"{root_path}/{year}"
        total_num = 0
        keyword_num = 0
        for country in os.listdir(year_folder):
            country_folder = f"{year_folder}/{country}"
            for file in os.listdir(country_folder):
                text_file = f"{country_folder}/{file}"
                text = read_text(text_file)
                # print(text)
                total_num += 1
                if keyword in text:
                    keyword_num += 1
        keyword_rate = round(keyword_num * 1.0 / total_num, 4)
        dict_year_rate[year] = keyword_rate
    dict_year_rate = OrderedDict(sorted(dict_year_rate.items(), key=lambda obj: obj[0], reverse=False))
    print()
    print("Year\tWeight")
    for year in dict_year_rate:
        rate = dict_year_rate[year]
        print(f"{year}\t{rate}")
