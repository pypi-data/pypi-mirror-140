from quickcsv import *
import matplotlib.pyplot as plt
import pandas as pd
from correlation_kit.ck_wrapper import CorrelationKit

def get_dict_trends(time_field,trends,field):
    dict_t={}
    for item in trends:
        time=item[time_field]
        year=time.split("-")[0]
        month=time.split("-")[1]
        if int(year)<2020 or (int(year)==2022 and int(month)==2):
            continue

        dict_t[time]=item[field]
    return dict_t

def show_plot(time,x,y):

    # plot
    plt.plot(time, x)
    plt.plot(time, y)
    # beautify the x-labels
    plt.gcf().autofmt_xdate()

    plt.show()



def estimated_correlation(time_field,trends_folder,trend_name1,trend_name2, field):

    trends1 = read_csv(f"{trends_folder}/{trend_name1}_trends.csv")
    trends2 = read_csv(f"{trends_folder}/{trend_name2}_trends.csv")

    dict_trends1 = get_dict_trends(time_field,trends1, field)
    dict_trends2 = get_dict_trends(time_field,trends2, field)

    # print(dict_trends1)
    # print(dict_trends2)
    list_v1 = []
    list_v2 = []
    list_time = []
    count = 0
    for k in dict_trends1:
        if k in dict_trends2:
            time = k
            count += 1
            list_time.append(count)
            list_v1.append(int(dict_trends1[k]))
            list_v2.append(int(dict_trends2[k]))

    # print(list_v1)
    # print(list_v2)



    # set a dataframe or read from a csv file
    d = {'x': list_v1, 'y': list_v2}
    df = pd.DataFrame(data=d)

    # set x label and y label for correlation
    x = "x"
    y = "y"

    # calc
    def get_correlation(x, y, corr_type):
        stat = 0
        p = 0
        if corr_type == "pearson":
            stat, p = CorrelationKit(df).get_pearson(x, y)
        elif corr_type == "spearman":
            stat, p = CorrelationKit(df).get_spearman(x, y)
        elif corr_type == "kendalltau":
            stat, p = CorrelationKit(df).get_kendalltau(x, y)
        return stat, p

    # print results
    result={
        "pearson":get_correlation(x, y, "pearson"),
        "spearman":get_correlation(x, y, "spearman"),
        "kendalltau":get_correlation(x,y,"kendalltau")
    }

    # print("pearson = ", get_correlation(x, y, "pearson"))
    # print("spearman = ", get_correlation(x, y, "spearman"))
    # print("kendalltau = ", get_correlation(x, y, "kendalltau"))

    # show_plot(list_time, list_v1, list_v2)
    return result

def estimate_trends_corrleation_matrix(trends_folder,list_compare,labels,time_field="Time"):
    print(f"相关性分析\t变量\t统计量\tp-value")


    for compare_item in list_compare:
        trend_name1 = compare_item[0]
        trend_name2 = compare_item[1]


        # field='政府'

        list_result = []

        for label in labels:
            # print(label)
            result = estimated_correlation(time_field,trends_folder,trend_name1, trend_name2, label)
            list_result.append(result)
            # print()

        # print(f"{trend_name1} <-> {trend_name2}")

        for idx, result in enumerate(list_result):
            compare = f"{trend_name1} <-> {trend_name2}"
            # print(labels[idx],result)
            line = f"{trend_name1} <-> {trend_name2}\t{labels[idx]}\t{result['pearson'][0]}\t{result['pearson'][1]}"
            print(line)



