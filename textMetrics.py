import pandas as pd
import re
from collections import Counter

def counts(df):
    pals = ' '.join(list(df.text.values)).split()
    pals = [re.sub(r'[^#@\w]', '', pal) for pal in pals]
    pals = [re.sub(r'[#@][\w_]+', '', pal) for pal in pals]
    pals = [re.sub(r'http.+', '', pal) for pal in pals]
    pals = [x.lower() for x in pals if not x == '']
    return pd.Series(dict(Counter(pals))).sort_values(ascending = False)

def groupCounts(df, n=10):
    hashtags = (
        df.text.str
        .extractall(r'(#[\w_]+)')
        .reset_index(drop = True)
        .rename({0:'hashtag'}, axis = 'columns')
        .hashtag.value_counts()
        .reset_index(name = 'cantidad')
        .rename({'index':'item'}, axis = 'columns')
        .head(n + 1)
    )
    mentions = (
        df.text.str
        .extractall(r'(@[\w_]+)')
        .reset_index(drop = True)
        .rename({0:'mention'}, axis = 'columns')
        .mention.value_counts()
        .reset_index()
        .rename({'index':'item', 'mention':'cantidad'}, axis = 'columns')
        .head(n + 1)
    )
    languages = (df['language']
        .value_counts()
        .reset_index()
        .rename({'index':'item', 'language':'cantidad'}, axis = 'columns')
        .head(n + 1)
    )
    return hashtags, mentions, languages

if __name__ == '__main__':
    df = pd.read_csv('myLocations.csv')
    groupCounts(df)