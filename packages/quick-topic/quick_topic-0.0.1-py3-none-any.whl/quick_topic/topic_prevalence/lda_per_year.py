import os
from gensim import corpora, models
import gensim
from quickcsv.file import *
import jieba
import jieba.posseg as pseg
import numpy as np

def LDA( year,list_doc,save_topic_weights_folder,list_keywords_path,stop_words_path,
    # ============ begin configure ====================
    NUM_TOPICS = 10,
    NUM_WORDS = 50,
    FIG_V_NUM = 2,
    FIG_H_NUM = 3,
    WC_MAX_WORDS = 20,
    NUM_PASS = 5
    # ============ end configure ======================
         ):

    if list_keywords_path!=None:
        for keyword_path in list_keywords_path:
            jieba.load_userdict(keyword_path)

    # qc_write("results/result_expert.csv",list_result)

    stopwords = [w.strip() for w in open(stop_words_path, 'r', encoding='utf-8').readlines()
                 if w.strip() != ""]

    # load data
    # dict_dataset=pickle.load(open("datasets/weibo_vae_dataset_prepared_with_domain.pickle", "rb"))

    # compile sample documents into a list
    # doc_set = [doc_a, doc_b, doc_c, doc_d, doc_e]

    doc_set = []
    for doc in list_doc:
        # if not is_keyword_in_doc(doc):
        #     continue
        # list_words=jieba.cut(doc,cut_all=False)
        list_words = pseg.cut(doc)
        list_w = []
        for w, f in list_words:
            if f in ['n', 'nr', 'ns', 'nt', 'nz', 'vn', 'nd', 'nh', 'nl', 'i']:
                if w not in stopwords and len(w) != 1:
                    list_w.append(w)
        # print(list_w)
        doc_set.append(list_w)

    # list for tokenized documents in loop
    texts = []

    # loop through document list
    for tokens in doc_set:
        # clean and tokenize document string

        # stem tokens
        # stemmed_tokens = [p_stemmer.stem(i) for i in tokens]

        # add tokens to list
        texts.append(tokens)

    # turn our tokenized documents into a id <-> term dictionary
    dictionary = corpora.Dictionary(texts)

    # convert tokenized documents into a document-term matrix
    corpus = [dictionary.doc2bow(text) for text in texts]

    # generate LDA model
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=NUM_PASS)

    # print keywords
    topics = ldamodel.print_topics(num_words=NUM_WORDS, num_topics=NUM_TOPICS)

    save_topic_weights(save_topic_weights_folder,year,topics)


def save_topic_weights(topic_weight_folder, year,topics):
    if not os.path.exists(topic_weight_folder):
        os.mkdir(topic_weight_folder)
    f_out_k=open(f"{topic_weight_folder}/{year}_k.csv",'w',encoding='utf-8')
    f_out_v = open(f"{topic_weight_folder}/{year}_v.csv", 'w', encoding='utf-8')
    for topic in topics:
        print(topic)
        topic_id=topic[0]
        list_keywords=[]
        list_weight=[]
        s=str(topic[1])
        for k in s.split("+"):
            fs=k.split("*")
            w=fs[0].strip()
            keyword=fs[1].replace("\"","").strip()
            # print(keyword,w)
            list_keywords.append(keyword)
            list_weight.append(str(w))
        # print(','.join(list_keywords))
        # print("total weight:",round(np.sum(list_weight,4)))
        f_out_k.write(','.join(list_keywords)+"\n")
        f_out_v.write(','.join(list_weight)+"\n")
    f_out_v.close()
    f_out_k.close()

def do_lda_per_year(start_year,end_year, yearly_data_folder = "results/news_by_year",
                    save_topic_weight_folder="results/topic_weights",list_keywords_path=None,
                    stopwords_path="hit_stopwords.txt"
                    ):
    for year in range(start_year, end_year+1):
        year_folder = f"{yearly_data_folder}/{year}"
        list_doc = []
        if not os.path.exists(year_folder):
            continue
        for country in os.listdir(year_folder):
            for file in os.listdir(os.path.join(year_folder, country)):
                text_path = f"{year_folder}/{country}/{file}"
                if not os.path.exists(text_path):
                    continue
                # print(country,file)
                if '.txt' not in file:
                    continue
                text = open(text_path, "r", encoding='utf-8').read()
                list_doc.append(text)
        print(f"{year}'s news count: ", len(list_doc))
        LDA(year, list_doc,save_topic_weight_folder,list_keywords_path,stopwords_path)
        print()

