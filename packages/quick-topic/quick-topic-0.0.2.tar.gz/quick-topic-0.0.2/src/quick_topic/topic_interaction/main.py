from quick_topic.topic_interaction.divide_by_tag import *
from quick_topic.topic_interaction.lda_by_tag_each import *
from quick_topic.topic_interaction.interaction_among_tag import *

def run_topic_interaction(meta_csv_file,raw_text_folder, output_folder,category_csv_file,stopwords_path,weights_folder,list_keywords_path,
    label_names,list_topics,filter_words):
    # step 1
    divide_by_tag(
        meta_csv_file=meta_csv_file,
        raw_text_folder=raw_text_folder,
        output_folder=output_folder,
        category_path=category_csv_file
    )
    # step 2


    lda_by_tag_each(
        category_path=category_csv_file,
        root_path=output_folder,
        weights_path=weights_folder,
        list_keywords_path=list_keywords_path,
        stopwords_path=stopwords_path
    )
    # step 3


    # run analysis for weights and interaction analysis
    interaction_among_tag(
        category_path=category_csv_file,
        weights_folder=weights_folder,
        label_names=label_names,
        list_topics=list_topics,
        filter_keywords=filter_words
    )


