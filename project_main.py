import pandas as pd
from Utils import *
from similarity import *
from itertools import combinations

df = pd.DataFrame()
n_distinct = 500

for i in range(1, 6):
    df_tmp = pd.read_csv(f'stack-traces data/stack-traces-{i}.csv')
    df = pd.concat([df, df_tmp])

# print(df[:5])

df_distinct = pd.DataFrame()
df_distinct['stackTrace'] = df['stackTrace'].value_counts().index[:n_distinct]

# Taking just the first element of the tuple returned by process_stack_trace()
df_distinct['listStackTrace'] = df_distinct['stackTrace'].apply(lambda x: process_stack_trace(x)[0])

df_distinct['listStackTrace'] = df_distinct['listStackTrace'].apply(lambda x: delete_infoFile(x))
df_distinct['listStackTrace'] = df_distinct['listStackTrace'].apply(lambda x: handle_truncated(x))

# At this point, we got the stack traces in a separate column, as a list of "words"

sim_jaccard = df_distinct.apply(lambda x: jaccard_df(x['listStackTrace'], 
    df_distinct['listStackTrace'], rowIndex(x)), axis=1)

df_distinct['jaccardValues'] = sim_jaccard

print(df_distinct)