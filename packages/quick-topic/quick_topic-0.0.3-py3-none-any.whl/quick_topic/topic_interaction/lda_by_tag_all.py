import os
import os
from gensim import corpora, models
import gensim
from quickcsv.file import *
import jieba
import jieba.posseg as pseg

def LDA(field,list_doc,weights_path,list_keywods_path,stopwords_path):

    # ============ begin configure ====================
    NUM_TOPICS = 6
    NUM_WORDS = 50
    FIG_V_NUM = 2
    FIG_H_NUM = 3
    WC_MAX_WORDS = 20
    NUM_PASS = 5
    # ============ end configure ======================
    for pp in list_keywods_path:
        jieba.load_userdict(pp)

    # qc_write("results/result_expert.csv",list_result)

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

    save_topic_weights(field,topics,weights_path)

def save_topic_weights(field,topics,weights_path):
    f_out_k=open(f"{weights_path}/topics_{field}_k.csv",'w',encoding='utf-8')
    f_out_v = open(f"{weights_path}/topics_{field}_v.csv", 'w', encoding='utf-8')
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

def lda_by_tag(root_path="",weights_path="",list_keywords_path=None,stopwords_path=""):
    list_doc = []
    if not os.path.exists(weights_path):
        os.mkdir(weights_path)
    for country in os.listdir(root_path):
        for file in os.listdir(os.path.join(root_path, country)):
            text_path = f"{root_path}/{country}/{file}"
            text = open(text_path, "r", encoding='utf-8').read()
            list_doc.append(text)

    LDA("all", list_doc,weights_path,list_keywords_path,stopwords_path)




