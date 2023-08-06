from quickcsv.file import *
import os

def get_news_by_year(meta_csv_file,raw_text_folder,output_folder,group_by="tag",time_field="time",id_field="Id",
    prefix_filename=""
                     ):
    list_item = qc_read(meta_csv_file)
    count = 0
    total_records=len(list_item)
    for idx,item in enumerate(list_item):
        # print(f"{idx}/{total_records}")
        # country
        country=item[group_by]
        if country=="":
            country="unknown"
            # continue
        # # pubtime
        pubtime = item[time_field]
        year=''
        if '-' in pubtime:
            year=pubtime.split("-")[0]
        if year.strip()=="":
            continue
        # file id
        file_id = item[id_field]
        text_path = f"{raw_text_folder}/{prefix_filename}{file_id}.txt"
        if not os.path.exists(text_path):
            continue
        text = open(text_path, 'r', encoding='utf-8').read()
        # create folder
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
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
    print("Finished")


