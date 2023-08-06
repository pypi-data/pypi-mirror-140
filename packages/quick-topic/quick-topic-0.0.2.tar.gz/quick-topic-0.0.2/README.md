## Quick Topic Modeling Toolkit
The `quick-topic` toolkit allows us to quickly evaluate topic models in various methods.

### Functions
1. Topic Prevalence Trends Analysis
2. Topic Interaction Strength Analysis
3. Topic Transition Analysis

### Usage

Example 1: Topic Prevalence over Time

```python
from quick_topic.topic_prevalence.main import *
# data file: a csv file; a folder with txt files named 
# the same as the ID field in the csv file
meta_csv_file = "../datasets/list_company_news_meta.csv"
text_root = r"../datasets/text_data_processed2"

# word segmentation data files
list_keywords_path = [
        "../datasets/keywords/countries.csv",
        "../datasets/keywords/leaders_unique_names.csv",
        "../datasets/keywords/carbon2.csv"
    ]

# remove keywords
stop_words_path = "../datasets/stopwords/hit_stopwords.txt"

# date range for analysis
start_year=2000
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
    save_root_folder="results/target1",
    list_keywords_path=list_keywords_path,
    stop_words_path=stop_words_path,
    start_year=start_year,
    end_year=end_year,
    label_names=label_names,
    list_topics=list_topics
)
```

Example 2: Estimate the strength of topic interaction (shared keywords) from different topics 

```python
from quick_topic.topic_interaction.main import *
# step 1: data file
meta_csv_file = "../datasets/list_company_news_meta.csv"
text_root = r"D:\UIBE科研\国自科青年\开源项目\autobr\examples-industry\datasets\company\text_data_processed2"
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

# run shell
run_topic_interaction(
    meta_csv_file=meta_csv_file,
    raw_text_folder=text_root,
    output_folder="results/target1/divided",
    category_csv_file='keywords_companies.csv',
    stopwords_path="../datasets/stopwords/hit_stopwords.txt",
    weights_folder='results/target1/weights',
    list_keywords_path=list_keywords_path,
    label_names=label_names,
    list_topics=list_topics,
    filter_words=filter_words
)
```

Example 3: Divide datasets by year or year-month

By year:
```python
from quick_topic.topic_transition.divide_by_year import *
divide_by_year(
    meta_csv_file="../datasets/list_g20_news_all_clean.csv",
    raw_text_folder=r"D:\UIBE科研\国自科青年\开源项目\carbon2-research\information_extraction2\datasets\g20_news_processed",
    output_folder="results/test1/divided_by_year",
    start_year=2000,
    end_year=2021
)
```

By year-month:
```python
from quick_topic.topic_transition.divide_by_year_month import *
divide_by_year_month(
    meta_csv_file="../datasets/list_g20_news_all_clean.csv",
    raw_text_folder=r"D:\UIBE科研\国自科青年\开源项目\carbon2-research\information_extraction2\datasets\g20_news_processed",
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


## License

The `quick-topic` toolkit is provided by [Donghua Chen](https://github.com/dhchenx) with MIT License.