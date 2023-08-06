from quickcsv.file import *
import os

def divide_by_year_month(meta_csv_file,raw_text_folder,output_folder,tag_field="Tag",time_field="PublishTime",id_field="FileId",start_year=2000,end_year=2021):
    list_item = qc_read(meta_csv_file)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    count=0
    for item in list_item:
        # country
        country=item[tag_field]
        if country=="":
            country="未知"
            # continue
        # # pubtime
        pubtime = item[time_field]
        year_month=''
        year=-1
        month=""
        if '-' in pubtime:
            year=pubtime.split("-")[0]
            month=pubtime.split("-")[1]
            year_month=f"{year}-{month}"
        if year_month.strip()=="":
            continue
        if int(year)<start_year or int(year)>end_year:
            continue

        # file id
        file_id = item[id_field]
        text_path = f"{raw_text_folder}/{file_id}.txt"
        if not os.path.exists(text_path):
            continue
        text = open(text_path, 'r', encoding='utf-8').read()
        # create folder
        year_month_folder=f'{output_folder}/{year_month}'
        if not os.path.exists(year_month_folder):
            os.mkdir(year_month_folder)
        country_folder=f'{year_month_folder}/{country}'
        if not os.path.exists(country_folder):
            os.mkdir(country_folder)
        f_out=open(f"{country_folder}/{count}.txt",'w',encoding='utf-8')
        f_out.write(text)
        f_out.close()
        count+=1

