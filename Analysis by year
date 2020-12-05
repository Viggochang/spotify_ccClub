import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from decimal import *
import re
import requests
from bs4 import BeautifulSoup
import json
from pyecharts import options as opts
from pyecharts.charts import Page, ThemeRiver
from pyecharts.globals import ThemeType
import bar_chart_race as bcr


df_main = pd.read_csv('your_path/data-main.csv')
df_year = df_main.copy()

df_year = df_year.drop(columns=['id.1'])
df_year = df_year.drop(columns=['Unnamed: 0'])
df_year['album_release_date'] = pd.to_datetime(df_year['album_release_date'])
df_year.insert(5, 'year', pd.DatetimeIndex(df_year['album_release_date']).year)


# add a column of genres_list
df_year['genres_lst'] = df_year['genres'].apply(lambda x: x.split("', '"))
df_year['genres_lst'] = df_year['genres_lst'].apply(lambda x: [_.replace("[", "").replace("]", "").replace("'", "") for _ in x])


# 刪除重複的歌曲、刪除沒有曲風分類的歌曲
df_year = df_year.drop_duplicates(subset=['name', 'artists_name'])
df_year = df_year[df_year['genres'] != '[]']


# add genres label
genres = ['classical', 'country', 'folk', 'blues', 'r&b', 'soul', 'house', 'jazz', 'rock', 'rock-and-roll', 'funk', 'metal', 'punk', 'disco', 'hip hop', 'rap', 'pop', 'reggae', 'ska', 'dance', 'electronic', 'alternative', 'indie', 'others']
def genres_transfer(col, g):
    if g in col:
        return 1
    else:
        return 0

for genre in genres:
    df_year[genre] = df_year['genres'].apply(lambda x: genres_transfer(x, genre))


# add label: 曲風為 Others
boo = df_year[genres].sum(axis=1) == 0
df_year.loc[boo, 'others'] = 1


# 所有曲風歷年折線圖
df_year[genres].groupby(df_year['year']).sum().plot(figsize=(20, 8))
plt.show()


# 曲風河流圖
data_river = []

for g in genres:
    df_river = pd.DataFrame(df_year['year'].unique(), columns=['year'], index=df_year['year'].unique())
    df_river['year'] = df_river['year'].apply(str)
    df_river['count'] = df_year[df_year[g] == 1].groupby(by=['year'])[g].sum()
    df_river['genre'] = np.full(len(df_river), g)
    df_river['count'] = df_river['count'].fillna(0)

    data_river.extend(df_river.values.tolist())

river = ThemeRiver(init_opts=opts.InitOpts(width="2000px", height="600px", theme=ThemeType.LIGHT))
river.add(series_name=genres, 
          data=data_river, 
          label_opts=opts.LabelOpts(font_size=10),
          singleaxis_opts=opts.SingleAxisOpts(
              pos_top="50", pos_bottom="50", type_="time",),
         )
river.set_global_opts(
    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
    title_opts=opts.TitleOpts(title="1901-2020 曲風流變", subtitle = "1901-2020",pos_bottom = "85%", pos_right = "80%"),
    )
river.set_series_opts(label_opts=opts.LabelOpts(is_show = 0))

# themeriver().load_javascript()
river.render_notebook()
