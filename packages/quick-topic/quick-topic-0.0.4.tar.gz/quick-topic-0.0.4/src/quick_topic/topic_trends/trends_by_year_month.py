from quickcsv.file import *
from collections import OrderedDict

def show_year_month_trends(
        meta_csv_file='../information_extraction2/datasets/list_g20_news_all_clean.csv',
        id_field="FileId",
        time_field="PublishTime",
        opinion_path="../information_extraction2/datasets/list_g20_leaders_opinion.csv",
        opinion_field="opinion",
        opinion_id_field="file_id",
        list_topics=None,
        label_names=None,
        save_result_path="",
        minimum_year=2019
):
    # load dataset
    list_g20_news_final = qc_read(csv_path=meta_csv_file)

    dict_opinion_year_month = {}

    N = len(list_g20_news_final)
    for idx, item in enumerate(list_g20_news_final):
        print(f"{idx+1}/{N}")
        file_id = item[id_field]
        publishtime = item[time_field]
        year_month = ""
        year = ""
        if '-' in publishtime:
            ps = publishtime.split("-")
            year_month = ps[0] + "-" + ps[1]
            year = int(ps[0])
        if year_month == "":
            continue
        if year < minimum_year:
            continue

        dict_opinion_year_month[file_id] = year_month

    list_item = qc_read(opinion_path)

    list_dict_topic=[]

    for the_keyword in list_topics:
        dict_keywords = OrderedDict()
        list_keywords=[]
        for item in list_item:
            file_id = item[opinion_id_field]
            # print(item["file_id"])
            opinion = item[opinion_field]
            # print(opinion)
            for k in the_keyword:
                if k in opinion:
                    # print(opinion)
                    list_keywords.append(item)
                    get_trend(dict_opinion_year_month,dict_keywords, file_id)
                    break
        # print(list_keywords)
        list_dict_topic.append(dict_keywords)

    # year-month trends
    list_dict_topic[0] = OrderedDict(sorted(list_dict_topic[0].items(), key=lambda obj: obj[0], reverse=False))

    # show_time_trend(dict_energy)
    show_time_trends(
        labels=label_names,
        list_dict_trends=list_dict_topic,
        output_trends_file=save_result_path
    )


def get_trend(dict_opinion_year_month,dict_num,file_id):
    year_month = ""
    if file_id in dict_opinion_year_month:
        year_month = dict_opinion_year_month[file_id]
    if year_month == "":
        return
    if year_month in dict_num:
        if file_id not in dict_num[year_month]:
            dict_num[year_month].append(file_id)
        else:
            dict_num[year_month] = [file_id]
    else:
        dict_num[year_month] = []
        dict_num[year_month].append(file_id)
    return dict_num

def get_trend_total(dict_opinion_year_month,dict_economics,file_id):
    year_month = ""
    if file_id in dict_opinion_year_month:
        year_month = dict_opinion_year_month[file_id]
    if year_month == "":
        return
    if year_month in dict_economics:
        dict_economics[year_month].append(file_id)
    else:
        dict_economics[year_month] = []
        dict_economics[year_month].append(file_id)
    return dict_economics

def show_time_trend(dict_trend):
    print("Year\tDocument frequence")
    for k in dict_trend:
        print(f"{k}\t{len(dict_trend[k])}")

def show_time_trends(labels,list_dict_trends,output_trends_file):
    list_item=[]

    print("Time\t"+"\t".join(labels))
    for k in list_dict_trends[0]:
        ls = f"{k}\t"
        model = {
            "Time": k
        }
        for idx,dict_trend in enumerate(list_dict_trends):
            if k in dict_trend:
                ls+=f"{len(dict_trend[k])}\t"
                model[labels[idx]]=len(dict_trend[k])
            else:
                model[labels[idx]] = 0
                ls+="0\t"
        list_item.append(model)
        print(ls)
    qc_write(output_trends_file,list_item)

