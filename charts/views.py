import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
import sqlite3

import io
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
import sqlite3

def get_data():
    conn = sqlite3.connect('/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/im.db')
    bom = pd.read_csv('/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/bom.movie_gross.csv')
    tn = pd.read_csv('/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/tn.movie_budgets.csv')
    tn = tn.rename(columns={'movie': 'title'})
    merged_df = pd.merge(tn, bom, on='title', how='left')
    tn = merged_df.drop(columns=[col for col in merged_df.columns if col not in tn.columns])
    imdb = pd.read_sql("""
        SELECT *
        FROM movie_basics
        LEFT JOIN movie_ratings 
        USING(movie_id)
        """, conn)
    imdb = imdb.dropna()
    rt = pd.read_csv('/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/rt.movie_info.tsv', sep='\t')
    rt_review = pd.read_csv("/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/rt.reviews.tsv", sep='\t', encoding='windows-1252')
    rt_merged = pd.merge(rt, rt_review, on='id', how='inner')
    tmdb = pd.read_csv('/home/sudheer/sudheer/convert_notebook_files/film_analysis/charts/data/tmdb.movies.csv', index_col=0)
    tmdb = tmdb.drop(columns='genre_ids')
    imdb_tm = pd.merge(imdb, tmdb, on='original_title', how='inner')
    imdb_tm.drop_duplicates(inplace=True)
    imdb_tm = imdb_tm.dropna()
    imdb_tm['avg_rating'] = (imdb_tm['averagerating'] + imdb_tm['vote_average']) / 2
    imdb_tm['release_year'] = pd.to_datetime(imdb_tm['release_date'], errors='coerce', infer_datetime_format=True).dt.year
    imdb_tm = imdb_tm[['original_title', 'genres', 'original_language', 'runtime_minutes', 'avg_rating', 'release_year']]
    return imdb_tm, tn

def chart_genre_distribution(request):
    imdb_tm, _ = get_data()
    genre_count = imdb_tm.dropna(subset=['genres'])
    genre_count['genres'] = genre_count['genres'].str.split(',')
    genre_count = genre_count.explode('genres')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x=genre_count['genres'].value_counts()[:10].index,
                y=genre_count['genres'].value_counts()[:10].values,
                ax=ax, palette='viridis')
    ax.set_xlabel('Count')
    ax.set_ylabel('Genre')
    ax.set_title('Distribution of Top 10 Genres')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def chart_language_distribution(request):
    imdb_tm, _ = get_data()
    top5_lang = imdb_tm['original_language'].value_counts()[:5]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(top5_lang, autopct='%1.1f%%')
    ax.set_title('Top 5 Languages for Films')
    ax.legend(labels=top5_lang.index, title="Languages", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def chart_runtime_distribution(request):
    imdb_tm, _ = get_data()
    plt.boxplot(imdb_tm['runtime_minutes'].value_counts().values)
    plt.title('Runtime Plot')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return HttpResponse(buffer, content_type='image/png')

def chart_runtime_bins(request):
    imdb_tm, tn = get_data()
    bins = [0, 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 700]
    labels = ['< 60 min', '60-120 min', '120-180 min', '180-240 min', '240-300 min', '300-360 min', '360-420 min', '420-480 min', '480-540 min', '540-600 min', '600-660 min', '660 >']
    min_class = pd.cut(imdb_tm['runtime_minutes'], bins=bins, labels=labels, right=False)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(min_class.value_counts()[:4], autopct='%1.1f%%')
    ax.legend(labels=min_class.value_counts()[:4].index, title="Runtime", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title('Average Length of a Film in Minutes')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def chart_rating_distribution(request):
    imdb_tm, _ = get_data()
    fig, ax = plt.subplots(figsize=(10, 8))
    mean_r = imdb_tm['avg_rating'].mean()
    ax.bar(imdb_tm['avg_rating'].value_counts().index, imdb_tm['avg_rating'].value_counts().values)
    ax.axvline(x=mean_r, color='r')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Ratings')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def chart_seasonal_performance(request):
    _, tn = get_data()
    tn['release_date'] = pd.to_datetime(tn['release_date'], format='%b %d, %Y')
    tn['month'] = tn['release_date'].dt.month
    tn['season'] = tn['month'].apply(get_season)
    tn['production_budget'] = tn['production_budget'].str.replace(',', '').str.replace('$','').astype(float)
    tn['worldwide_gross'] = tn['worldwide_gross'].str.replace(',', '').str.replace('$','').astype(float)
    seasonal_performance = tn.groupby('season').agg({'worldwide_gross': 'mean'}).reset_index()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x='season', y='worldwide_gross', data=seasonal_performance, palette='viridis', ax=ax)
    plt.title('Average Worldwide Gross by Season')
    plt.ylabel('Average Worldwide Gross ($)')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def chart_monthly_trend(request):
    _, tn = get_data()
    monthly_trend = tn.groupby('month').agg({'worldwide_gross': 'mean'}).reset_index()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.lineplot(x='month', y='worldwide_gross', data=monthly_trend, marker='o', color='b', ax=ax)
    plt.title('Average Worldwide Gross by Month Across All Years')
    plt.xlabel('Month')
    plt.ylabel('Average Worldwide Gross ($)')
    plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    return HttpResponse(buffer, content_type='image/png')

def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'


def chart_page(request):
    return render(request, 'charts/chart.html')
