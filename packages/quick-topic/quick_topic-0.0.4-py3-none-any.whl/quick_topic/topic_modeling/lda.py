from gensim import corpora, models
import gensim
import jieba
import jieba.posseg as pseg
from quickcsv.file import *
import os

def build_lda_model(list_doc,num_topics=6,num_words=50,num_pass=5,list_term_file=None,stopwords_path="",save_name="topic",output_folder="output"):

    # ============ begin configure ====================
    NUM_TOPICS = num_topics
    NUM_WORDS = num_words
    FIG_V_NUM = 2
    FIG_H_NUM = 3
    WC_MAX_WORDS = 20
    NUM_PASS = num_pass
    # ============ end configure ======================
    if list_term_file!=None:
        for file in list_term_file:
            jieba.load_userdict(file)

    # qc_write("results/result_expert.csv",list_result)
    stopwords=[]
    if stopwords_path!="":
        stopwords = [w.strip() for w in open(stopwords_path, 'r', encoding='utf-8').readlines()
                     if w.strip() != ""]

    # load data
    # dict_dataset=pickle.load(open("datasets/weibo_vae_dataset_prepared_with_domain.pickle", "rb"))

    # compile sample documents into a list
    # doc_set = [doc_a, doc_b, doc_c, doc_d, doc_e]

    doc_set = []
    for doc in list_doc:
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

    save_topic_weights(output_folder,save_name,topics)

def save_topic_weights(output_folder,field,topics):
    print(field)
    f_out_k=open(f"{output_folder}/{field}_k.csv",'w',encoding='utf-8')
    f_out_v = open(f"{output_folder}/{field}_v.csv", 'w', encoding='utf-8')
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
    print()

def build_lda_models(meta_csv_file,raw_text_folder,tag_field="area",id_field="fileId",
                     prefix_filename="text_",list_term_file=None,stopwords_path="",
                     output_folder="results/topic_modeling",
                    num_topics=6,num_words=50,num_pass=5,
                     ):

    #meta_csv_file = "datasets/list_country.csv"
    #raw_text_folder = "datasets/raw_text"

    dict_country = {}
    list_item = read_csv(meta_csv_file)

    for item in list_item:
        area = item[tag_field]
        id = item[id_field]
        text_path = f'{raw_text_folder}/{prefix_filename}{id}.txt'
        if not os.path.exists(text_path):
            continue
        text = read_text(text_path)
        if text.strip() == "":
            continue
        if area in dict_country:
            dict_country[area].append(text)
        else:
            dict_country[area] = [text]

    for country in dict_country:
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        build_lda_model(
            list_doc=dict_country[country],
            output_folder=output_folder,
            stopwords_path=stopwords_path,
            save_name=country,
            list_term_file=list_term_file,
            num_pass=num_pass,
            num_topics=num_topics,
            num_words=num_words
        )
    return list(dict_country.keys())

