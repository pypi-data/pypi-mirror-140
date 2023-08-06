from quickcsv.file import *
import os

def divide_by_year(meta_csv_file,raw_text_folder,output_folder,start_year=2000,end_year=2021,tag_field="Tag",time_field="PublishTime",id_field="FileId"):
    count = 0
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    list_item = qc_read(meta_csv_file)
    for item in list_item:
        # country
        country=item[tag_field]
        if country=="":
            country="未知"
            # continue
        # # pubtime
        pubtime = item[time_field]
        year=''
        if '-' in pubtime:
            year=pubtime.split("-")[0]
        if year.strip()=="":
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
        year_folder=f'{output_folder}/{year}'
        if not os.path.exists(year_folder):
            os.mkdir(year_folder)
        country_folder=f'{year_folder}/{country}'
        if not os.path.exists(country_folder):
            os.mkdir(country_folder)
        f_out=open(f"{country_folder}/{count}.txt",'w',encoding='utf-8')
        f_out.write(text)
        f_out.close()
        count+=1

