import streamlit as st
from datetime import date


import os
import numpy as np
import pandas as pd

import math

import random
import datetime
from dateutil.relativedelta import relativedelta
from babel.dates import format_date

import nltk
nltk.download('brown')
from nltk.corpus import brown

import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

from IPython.display import display


from PIL import ImageColor
from io import BytesIO
from wordcloud import WordCloud
import base64
import colorlover as cl

def load_data():
    folder_path = os.getcwd()
    file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    
    channels = pd.read_csv(os.path.join(folder_path, file_list[0]))
    posts = pd.read_csv(os.path.join(folder_path, file_list[1]))
    reactions = pd.read_csv(os.path.join(folder_path, file_list[2]))
    subscribers = pd.read_csv(os.path.join(folder_path, file_list[3]))
    views = pd.read_csv(os.path.join(folder_path, file_list[4]))
    
    return channels, posts, reactions, subscribers, views


def date_ago(tp, num=0):
    if tp == 'today':
        return datetime.datetime.now().strftime("%Y-%m-%d") 
    elif tp == 'yesterday':
        return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif tp == 'days':
        return (datetime.datetime.now() - datetime.timedelta(days=num+1)).strftime("%Y-%m-%d")
    elif tp == 'weeks':
        return (datetime.datetime.now() - datetime.timedelta(days= 7*num + 1)).strftime("%Y-%m-%d") 
    elif tp == 'months':
        return (datetime.datetime.now() - relativedelta(months=num) - datetime.timedelta(days=1)).strftime("%Y-%m-%d") 
    else:
        print('Неправильно задан тип даты или не указано количество повторений (возможные типы дат: today, yesterday, days, weeks, months')

def convert_date(date, format_date = '%Y-%m-%d %H:%M:%S.%f'):
    try:
        return datetime.datetime.strptime(date, format_date)
    except ValueError:
        # Если строка не может быть преобразована в дату, возвращаем NaT (Not a Time)
        return pd.NaT
        
def get_current_previous_sums(df, col, period):
    mask1 = (df.date <= convert_date(date_ago(period[0]), '%Y-%m-%d').date())
    mask2 = (df.date > convert_date(date_ago(period[1], period[2]), '%Y-%m-%d').date())
    mask3 = (df.date <= convert_date(date_ago(period[1], period[2]), '%Y-%m-%d').date())
    mask4 = (df.date > convert_date(date_ago(period[1], period[2]*2), '%Y-%m-%d').date())
    
    current = df[mask1&mask2][col].sum()
    previous = df[mask3&mask4][col].sum()    
    
    return current, previous


channels, posts, reactions, subscribers, views = load_data()

posts.rename(columns={'date': 'datetime'}, inplace=True)
posts = posts.merge(channels[['id', 'channel_name']].rename(columns={'id':'channel_id'}), on='channel_id', how='left')
posts['date'] = pd.to_datetime(posts.datetime).dt.date
posts['time'] = posts.datetime.str[10:]
posts['cnt'] = posts.groupby(['channel_id', 'date'])['message_id'].transform('count')
posts['hour'] = pd.to_datetime(posts.datetime).dt.hour
posts = posts[~posts.text.isnull() & (posts.text != 'Нет текста')].copy()


# Объединённые стили
combined_styles = """ <style> body { background-color: #ffb347; /* Замените на нужный вам цвет */ } .title h1 { font-family: 'Open Sans', sans-serif; font-size: 28px; line-height: 36px; color: #333; background-color: #ffb347; padding: 20px; box-shadow: 0 10px 15px rgba(0,0,0,0.05); border-radius: 10px; text-align: center; } .subheader h2 { font-family: 'Open Sans', sans-serif; font-size: 16px; line-height: 24px; color: #666; margin-top: 20px; margin-bottom: 20px; font-weight: bold; } </style> """

# Основная функция приложения
def main():
    st.set_page_config(layout="wide")


    # Применяем объединённые стили
    st.markdown(combined_styles, unsafe_allow_html=True)
    
    # Заголовок
    st.markdown('<div class="title"><h1>Simulative</h1></div>', unsafe_allow_html=True)
    
    # Подзаголовок
    st.markdown('<div class="subheader"><h2>Дашборд по анализу Telegram-каналов</h2></div>', unsafe_allow_html=True)



    
    # Выбор канала
    channels = posts['channel_name'].unique()
    selected_channel = st.selectbox('Выберите канал:', channels)
    
    # Графики
    subdf = posts[posts.channel_name == selected_channel][['channel_name', 'date', 'cnt']].drop_duplicates()
    
    # Создание subplots
    fig = make_subplots(
        rows=3,
        cols=2,
        specs=[
            [{"rowspan": 3}, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
        ],
        vertical_spacing=0.08
    )
    
    mean_cnt = subdf.cnt.mean()
    colors = ['#8B4513' if val >= 2 * mean_cnt else '#F5DEB3' for val in subdf['cnt']]
    
    fig.add_trace(go.Bar(x=subdf.date, y=subdf.cnt, marker_color=colors,
                         hovertemplate='%{x} <br>Публикаций: %{y}<extra></extra>'), row=1, col=1)
    
    period_names = dict({'days': 'вчера', 'weeks': 'неделю', 'months': 'месяц'})
    for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
        current, previous = get_current_previous_sums(subdf, 'cnt', period)
        
        fig.add_trace(
            go.Indicator(
                value=current,
                title={"text": f"<span style='font-size:0.8em;color:gray'>Публикаций за {period_names[period[0]]}</span>"},
                mode="number+delta",
                delta={'reference': previous, 'relative': True, "valueformat": ".2%"},
            ), row=i + 1, col=2
        )
    
    # Настройка стиля графика
    fig.update_layout(
        template="simple_white",
        font_family="Georgia",
        font_size=12,
        margin=dict(l=40, r=20, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            rangeselector=dict(  # Добавляем элементы управления диапазоном
                bgcolor='#f5dfbf',  # Фоновый цвет области с кнопками
                font=dict(color="#333"),  # Цвет текста на кнопках
                activecolor='#ffb347',  # Цвет активной кнопки
                bordercolor='#f5dfbf',  # Цвет рамки вокруг кнопок
                buttons=list([
                    dict(count=2, label="2д", step="day", stepmode="backward"),
                    dict(count=14, label="2н", step="day", stepmode="backward"),
                    dict(count=2, label="2м", step="month", stepmode="backward"),
                    dict(step="all")  # Кнопка для просмотра всего диапазона
                ])
            )
        )
    )
    
    # Отображение графика
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
