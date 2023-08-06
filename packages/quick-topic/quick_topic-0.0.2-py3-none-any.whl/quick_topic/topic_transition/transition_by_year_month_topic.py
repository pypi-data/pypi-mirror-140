import os
from quickcsv.file import *
from collections import OrderedDict
import pandas as pd
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import matplotlib

def show_transition_by_year_month_topic(root_path,label,keywords,start_year,end_year,min_total_num=10,maximum_rate_if_meet_min_num=0.8,font_size=16,style="seaborn-deep"):
    matplotlib.rcParams.update({'font.size': font_size})
    plt.style.use(style)

    dict_year_month_rate = OrderedDict()

    for year in range(start_year, end_year+1):
        for month in range(1, 13):
            year_month = f"{year}-{month}"
            year_month_folder = f"{root_path}/{year}-{month}"
            if not os.path.exists(year_month_folder):
                continue
            total_num = 0
            keyword_num = 0
            for country in os.listdir(year_month_folder):
                country_folder = f"{year_month_folder}/{country}"
                for file in os.listdir(country_folder):
                    text_file = f"{country_folder}/{file}"
                    text = read_text(text_file)
                    # print(text)
                    total_num += 1
                    has_keyword = False
                    for k in keywords:
                        if k in text:
                            has_keyword = True
                            break
                    if has_keyword:
                        keyword_num += 1
            keyword_rate = round(keyword_num * 1.0 / total_num, 4)
            if total_num < min_total_num and keyword_rate > maximum_rate_if_meet_min_num:
                keyword_rate = 0
            dict_year_month_rate[year_month] = keyword_rate


    def show_scatter(title, x, y):
        dates = [pd.to_datetime(d) for d in x]
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel("Share of document")
        plt.scatter(dates, y)
        plt.show()

    dict_year_month_rate = OrderedDict(sorted(dict_year_month_rate.items(), key=lambda obj: obj[0], reverse=False))
    print()
    print(f"Year\t{label} Percent")
    x = []
    y = []
    for year_month in dict_year_month_rate:
        rate = dict_year_month_rate[year_month]
        print(f"{year_month}\t{rate}")
        x.append(year_month)
        y.append(rate)

    show_scatter(label, x, y)
