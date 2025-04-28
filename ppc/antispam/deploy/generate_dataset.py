import pandas as pd

# https://www.kaggle.com/datasets/ahsenwaheed/youtube-comments-spam-dataset
df1 = pd.read_csv('Youtube-Spam-Dataset.csv')
df1 = df1[['CONTENT', 'CLASS']]
df1 = df1[df1['CLASS'] == 1]
df1 = df1.rename(columns={'CONTENT': 'content', 'CLASS': 'class'})
df1['class'] = 2

# https://www.kaggle.com/datasets/atifaliak/youtube-comments-dataset
df2 = pd.read_csv('YoutubeCommentsDataSet.csv')
df2 = df2[df2['Sentiment'].isin(['positive', 'negative'])]
df2 = df2.rename(columns={'Comment': 'content', 'Sentiment': 'class'})
df2['class'] = df2['class'].map({'negative': 0, 'positive': 1})

# https://www.kaggle.com/datasets/madhuragl/5000-youtube-spamnot-spam-dataset
df3 = pd.read_csv('5000 YT comments.csv')
df3 = df3[['Comment', 'Spam']]
df3 = df3[df3['Spam'] == 1]
df3 = df3.rename(columns={'Comment': 'content', 'Spam': 'class'})
df3['class'] = 2

merged_df = pd.concat([df1, df2, df3], ignore_index=True)

negative_df = merged_df[merged_df['class'] == 0]
positive_df = merged_df[merged_df['class'] == 1]
spam_df = merged_df[merged_df['class'] == 2]

k = min(len(negative_df), len(positive_df), len(spam_df))
negative_df = negative_df[:k]
positive_df = positive_df[:k]
spam_df = spam_df[:k]

final_df = pd.concat([negative_df, positive_df, spam_df], ignore_index=True)
final_df.to_csv('dataset.csv', index=False)

print(final_df['class'].value_counts())
