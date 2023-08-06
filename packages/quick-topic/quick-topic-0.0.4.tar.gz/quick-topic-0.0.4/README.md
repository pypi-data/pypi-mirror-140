## Quick Topic Modeling Toolkit
The `quick-topic` toolkit allows us to quickly evaluate topic models in various methods.

### Features

Currently, this version only supports the topic modeling of Chinese text. We will support optimized features for English text. 

1. Topic Prevalence Trends Analysis
2. Topic Interaction Strength Analysis
3. Topic Transition Analysis
4. Topic Trends of Numbers of Document Containing Keywords
5. Topic Trends Correlation Analysis
6. Topic Similarity between Trends
7. Summarize Sentence Numbers By Keywords

### Basic Usage

Example: generate topic models for each category in the dataset files

```python
from quick_topic.topic_modeling.lda import build_lda_models
# step 1: data file
meta_csv_file="datasets/list_country.csv"
raw_text_folder="datasets/raw_text"
# term files used for word segementation
list_term_file = [
        "../datasets/keywords/countries.csv",
        "../datasets/keywords/leaders_unique_names.csv",
        "../datasets/keywords/carbon2.csv"
    ]
# removed words
stop_words_path = "../datasets/stopwords/hit_stopwords.txt"
# run shell
list_category = build_lda_models(
    meta_csv_file=meta_csv_file,
    raw_text_folder=raw_text_folder,
    output_folder="results/topic_modeling",
    list_term_file=list_term_file,
    stopwords_path=stop_words_path,
    prefix_filename="text_",
    num_topics=6
)
```

### Advanced Usage

Example 1: Topic Prevalence over Time

```python
from quick_topic.topic_prevalence.main import *
# data file: a csv file; a folder with txt files named the same as the ID field in the csv file
meta_csv_file = "datasets/list_country.csv"
text_root = r"datasets/raw_text"
# word segmentation data files
list_keywords_path = [
        "../datasets/keywords/countries.csv",
        "../datasets/keywords/leaders_unique_names.csv",
        "../datasets/keywords/carbon2.csv"
    ]
# remove keywords
stop_words_path = "../datasets/stopwords/hit_stopwords.txt"
# date range for analysis
start_year=2010
end_year=2021
# used topics
label_names = ['经济主题', '能源主题', '公众主题', '政府主题']
topic_economics = ['投资', '融资', '经济', '租金', '政府', '就业', '岗位', '工作', '职业', '技能']
topic_energy = ['绿色', '排放', '氢能', '生物能', '天然气', '风能', '石油', '煤炭', '电力', '能源', '消耗', '矿产', '燃料', '电网', '发电']
topic_people = ['健康', '空气污染', '家庭', '能源支出', '行为', '价格', '空气排放物', '死亡', '烹饪', '支出', '可再生', '液化石油气', '污染物', '回收',
                '收入', '公民', '民众']
topic_government = ['安全', '能源安全', '石油安全', '天然气安全', '电力安全', '基础设施', '零售业', '国际合作', '税收', '电网', '出口', '输电', '电网扩建',
                    '政府', '规模经济']
list_topics = [
    topic_economics,
    topic_energy,
    topic_people,
    topic_government
]
# run-all
run_topic_prevalence(
    meta_csv_file=meta_csv_file,
    raw_text_folder=text_root,
    save_root_folder="results/topic_prevalence",
    list_keywords_path=list_keywords_path,
    stop_words_path=stop_words_path,
    start_year=start_year,
    end_year=end_year,
    label_names=label_names,
    list_topics=list_topics,
    tag_field="area",
    time_field="date",
    id_field="fileId",
    prefix_filename="text_",
)
```

Example 2: Estimate the strength of topic interaction (shared keywords) from different topics 

```python
from quick_topic.topic_interaction.main import *
# step 1: data file
meta_csv_file = "datasets/list_country.csv"
text_root = r"datasets/raw_text"
# step2: jieba cut words file
list_keywords_path = [
        "../datasets/keywords/countries.csv",
        "../datasets/keywords/leaders_unique_names.csv",
        "../datasets/keywords/carbon2.csv"
    ]
# remove files
stopwords_path = "../datasets/stopwords/hit_stopwords.txt"
# set predefined topic labels
label_names = ['经济主题', '能源主题', '公众主题', '政府主题']
# set keywords for each topic
topic_economics = ['投资', '融资', '经济', '租金', '政府', '就业', '岗位', '工作', '职业', '技能']
topic_energy = ['绿色', '排放', '氢能', '生物能', '天然气', '风能', '石油', '煤炭', '电力', '能源', '消耗', '矿产', '燃料', '电网', '发电']
topic_people = ['健康', '空气污染', '家庭', '能源支出', '行为', '价格', '空气排放物', '死亡', '烹饪', '支出', '可再生', '液化石油气', '污染物', '回收',
                '收入', '公民', '民众']
topic_government = ['安全', '能源安全', '石油安全', '天然气安全', '电力安全', '基础设施', '零售业', '国际合作', '税收', '电网', '出口', '输电', '电网扩建',
                    '政府', '规模经济']
# a list of topics above
list_topics = [
    topic_economics,
    topic_energy,
    topic_people,
    topic_government
]
# if any keyword is the below one, then the keyword is removed from our consideration
filter_words = ['中国', '国家', '工作', '领域', '社会', '发展', '目标', '全国', '方式', '技术', '产业', '全球', '生活', '行动', '服务', '君联',
                '研究', '利用', '意见']
# dictionaries
list_country=[
    '巴西','印度','俄罗斯','南非'
]
# run shell
run_topic_interaction(
    meta_csv_file=meta_csv_file,
    raw_text_folder=text_root,
    output_folder="results/topic_interaction/divided",
    list_category=list_country, # a dictionary where each record contain a group of keywords
    stopwords_path=stopwords_path,
    weights_folder='results/topic_interaction/weights',
    list_keywords_path=list_keywords_path,
    label_names=label_names,
    list_topics=list_topics,
    filter_words=filter_words,
    # set field names
    tag_field="area",
    keyword_field="", # ignore if keyword from csv exists in the text
    time_field="date",
    id_field="fileId",
    prefix_filename="text_",
)
```

Example 3: Divide datasets by year or year-month

By year:
```python
from quick_topic.topic_transition.divide_by_year import *
divide_by_year(
    meta_csv_file="../datasets/list_g20_news_all_clean.csv",
    raw_text_folder=r"datasets\g20_news_processed",
    output_folder="results/test1/divided_by_year",
    start_year=2000,
    end_year=2021,
)
```

By year-month:
```python
from quick_topic.topic_transition.divide_by_year_month import *
divide_by_year_month(
    meta_csv_file="../datasets/list_g20_news_all_clean.csv",
    raw_text_folder=r"datasets\g20_news_processed",
    output_folder="results/test1/divided_by_year_month",
    start_year=2000,
    end_year=2021
)
```

Example 4: Show topic transition by year

```python
from quick_topic.topic_transition.transition_by_year_month_topic import *
label="经济"
keywords=['投资','融资','经济','租金','政府', '就业','岗位','工作','职业','技能']
show_transition_by_year_month_topic(
    root_path="results/test1/divided_by_year_month",
    label=label,
    keywords=keywords,
    start_year=2000,
    end_year=2021
)
```

Example 5: Show keyword-based topic transition by year-month for keywords in addition to mean lines
```python
from quick_topic.topic_transition.transition_by_year_month_term import *
root_path = "results/news_by_year_month"
select_keywords = ['燃煤', '储能', '电动汽车', '氢能', '脱碳', '风电', '水电', '天然气', '光伏', '可再生', '清洁能源', '核电']
list_all_range = [
    [[2010, 2015], [2016, 2021]],
    [[2011, 2017], [2018, 2021]],
    [[2009, 2017], [2018, 2021]],
    [[2011, 2016], [2017, 2021]],
    [[2017, 2018], [2019, 2021]],
    [[2009, 2014], [2015, 2021]],
    [[2009, 2014], [2015, 2021]],
    [[2009, 2015], [2016, 2021]],
    [[2008, 2011], [2012, 2015], [2016, 2021]],
    [[2011, 2016], [2017, 2021]],
    [[2009, 2012], [2013, 2016], [2017, 2021]],
    [[2009, 2015], [2016, 2021]]
]
output_figure_folder="results/figures"
show_transition_by_year_month_term(
    root_path="results/test1/divided_by_year_month",
    select_keywords=select_keywords,
    list_all_range=list_all_range,
    output_figure_folder=output_figure_folder,
    start_year=2000,
    end_year=2021
)
```

Example 6: Get time trends of numbers of documents containing topic keywords with full text.

```python
from quick_topic.topic_trends.trends_by_year_month_fulltext import *
# define a group of topics with keywords, each topic has a label
label_names=['经济','能源','公民','政府']
keywords_economics = ['投资', '融资', '经济', '租金', '政府', '就业', '岗位', '工作', '职业', '技能']
keywords_energy = ['绿色', '排放', '氢能', '生物能', '天然气', '风能', '石油', '煤炭', '电力', '能源', '消耗', '矿产', '燃料', '电网', '发电']
keywords_people = ['健康', '空气污染', '家庭', '能源支出', '行为', '价格', '空气排放物', '死亡', '烹饪', '支出', '可再生', '液化石油气', '污染物', '回收',
                   '收入', '公民', '民众']
keywords_government = ['安全', '能源安全', '石油安全', '天然气安全', '电力安全', '基础设施', '零售业', '国际合作', '税收', '电网', '出口', '输电', '电网扩建',
                       '政府', '规模经济']
list_topics = [
    keywords_economics,
    keywords_energy,
    keywords_people,
    keywords_government
]
# call function to show trends of number of documents containing topic keywords each year-month
show_year_month_trends_with_fulltext(
    meta_csv_file="datasets/list_country.csv",
    list_topics=list_topics,
    label_names=label_names,
    save_result_path="results/topic_trends/trends_fulltext.csv",
    minimum_year=2010,
    raw_text_path=r"datasets/raw_text",
    id_field='fileId',
    time_field='date',
    prefix_filename="text_"
)
```

Example 7: Estimate the correlation between two trends
```python
from quick_topic.topic_trends_correlation.topic_trends_correlation_two import *
trends_file="results/topic_trends/trends_fulltext.csv"
label_names=['经济','能源','公民','政府']
list_result=[]
list_line=[]
for i in range(0,len(label_names)-1):
    for j in range(i+1,len(label_names)):
        label1=label_names[i]
        label2=label_names[j]
        result=estimate_topic_trends_correlation_single_file(
            trend_file=trends_file,
            selected_field1=label1,
            selected_field2=label2,
            start_year=2010,
            end_year=2021,
            show_figure=False,
            time_field='Time'
        )
        list_result=[]
        line=f"({label1},{label2})\t{result['pearson'][0]}\t{result['pearson'][1]}"
        list_line.append(line)
        print()
print("Correlation analysis resutls:")
print("Pair\tPearson-Stat\tP-value")
for line in list_line:
    print(line)
```

Example 8: Estimate topic similarity between two groups of LDA topics
```python
from quick_topic.topic_modeling.lda import build_lda_models
from quick_topic.topic_similarity.topic_similarity_by_category import *
# Step 1: build topic models
meta_csv_file="datasets/list_country.csv"
raw_text_folder="datasets/raw_text"
list_term_file = [
        "../datasets/keywords/countries.csv",
        "../datasets/keywords/leaders_unique_names.csv",
        "../datasets/keywords/carbon2.csv"
    ]
stop_words_path = "../datasets/stopwords/hit_stopwords.txt"
list_category = build_lda_models(
    meta_csv_file=meta_csv_file,
    raw_text_folder=raw_text_folder,
    output_folder="results/topic_similarity_two/topics",
    list_term_file=list_term_file,
    stopwords_path=stop_words_path,
    prefix_filename="text_",
    num_topics=6,
    num_words=50
)
# Step 2: estimate similarity
output_folder = "results/topic_similarity_two/topics"
keywords_file="../datasets/keywords/carbon2.csv"
estimate_topic_similarity(
    list_topic=list_category,
    topic_folder=output_folder,
    list_keywords_file=keywords_file,
)
```

Example 9: Stat sentence numbers by keywords

```python
from quick_topic.topic_stat.stat_by_keyword import *
meta_csv_file='datasets/list_country.csv'
raw_text_folder="datasets/raw_text"
keywords_energy = ['煤炭', '天然气', '石油', '生物', '太阳能', '风能', '氢能', '水力', '核能']
stat_sentence_by_keywords(
    meta_csv_file=meta_csv_file,
    keywords=keywords_energy,
    id_field="fileId",
    raw_text_folder=raw_text_folder,
    contains_keyword_in_sentence='',
    prefix_file_name='text_'
)
```

## License

The `quick-topic` toolkit is provided by [Donghua Chen](https://github.com/dhchenx) with MIT License.

