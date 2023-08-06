from quickcsv import *
import datetime
import random
import matplotlib.pyplot as plt


def get_dict_trends(time_field,trends,selected_field,start_year,end_year):
    dict_t={}
    for item in trends:
        time=item[time_field]
        year=time.split("-")[0]
        month=time.split("-")[1]
        if int(year)<start_year or int(year)>end_year:
            continue

        dict_t[time]=item[selected_field]
    return dict_t

def show_plot(time,x,y):

    # plot
    plt.plot(time, x)
    plt.plot(time, y)
    # beautify the x-labels
    plt.gcf().autofmt_xdate()

    plt.show()

def estimate_topic_trends_correlation_single_file(trend_file,selected_field1,selected_field2,start_year=2000,end_year=2021,time_field="Time",show_figure=True):
    print(f"{selected_field1} <--> {selected_field2}")
    leader_trends = read_csv(trend_file)
    industry_trends = read_csv(trend_file)


    dict_leader_trends = get_dict_trends(time_field, leader_trends, selected_field1,start_year,end_year)
    dict_industry_trends = get_dict_trends(time_field,industry_trends, selected_field2,start_year,end_year)

    #print(dict_leader_trends)
    #print(dict_industry_trends)
    list_v1 = []
    list_v2 = []
    list_time = []
    count = 0
    for k in dict_leader_trends:
        if k in dict_industry_trends:
            time = k
            count += 1
            list_time.append(count)
            list_v1.append(int(dict_leader_trends[k]))
            list_v2.append(int(dict_industry_trends[k]))

    # print(list_v1)
    # print(list_v2)

    import pandas as pd
    from correlation_kit.ck_wrapper import CorrelationKit

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

    results = {
        "pearson":get_correlation(x, y, "pearson"),
        "spearman":get_correlation(x, y, "spearman"),
        "kendalltau": get_correlation(x, y, "kendalltau")
    }
    # print results
    #print("pearson = ", get_correlation(x, y, "pearson"))
    #print("spearman = ", get_correlation(x, y, "spearman"))
    #print("kendalltau = ", get_correlation(x, y, "kendalltau"))

    for k in results:
        print(f"{k}\t{results[k]}")
    if show_figure:
        show_plot(list_time, list_v1, list_v2)


    return results


def estimate_topic_trends_correlation(trend_file1,trend_file2,selected_field,start_year=2000,end_year=2021,time_field="Time"):
    leader_trends = read_csv(trend_file1)
    industry_trends = read_csv(trend_file2)


    dict_leader_trends = get_dict_trends(time_field, leader_trends, selected_field,start_year,end_year)
    dict_industry_trends = get_dict_trends(time_field,industry_trends, selected_field,start_year,end_year)

    print(dict_leader_trends)
    print(dict_industry_trends)
    list_v1 = []
    list_v2 = []
    list_time = []
    count = 0
    for k in dict_leader_trends:
        if k in dict_industry_trends:
            time = k
            count += 1
            list_time.append(count)
            list_v1.append(int(dict_leader_trends[k]))
            list_v2.append(int(dict_industry_trends[k]))

    print(list_v1)
    print(list_v2)

    import pandas as pd
    from correlation_kit.ck_wrapper import CorrelationKit

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
    print("pearson = ", get_correlation(x, y, "pearson"))
    print("spearman = ", get_correlation(x, y, "spearman"))
    print("kendalltau = ", get_correlation(x, y, "kendalltau"))

    show_plot(list_time, list_v1, list_v2)


