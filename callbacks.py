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

import string
from collections import Counter

from functions import date_ago, convert_date, get_gradient_color, get_current_previous_sums, create_table, hex_to_rgb\
                            , interpolate_color, gradient_color_func \
                        , calculate_mean_max_subs, calculate_mean_posts, calculate_mean_views, calculate_mean_reacts\
                        , load_stopwords_from_file

filter_columns_table_id = ['id']  #['id','date', 'time',  'text']
columns_table_id  = ['id','date', 'time',  'text']

def register_callbacks(app, data):
    subs = data['subs']
    posts = data['posts']
    
    post_view = data['post_view']
    gr_pvr = data['gr_pvr']  
    
    
    #-----------------------------Метрики----------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------    
    # Обновление метрик при выборе канала
    @app.callback(
        [
            Output('mean_subs_pos', 'children'),
            Output('mean_subs_neg', 'children'),
            Output('max_subs_pos', 'children'),
            Output('max_subs_neg', 'children'),
            Output('mean_posts_day', 'children'),
            Output('mean_posts_week', 'children'),
            Output('mean_posts_month', 'children'),
            Output('mean_views', 'children'),
            Output('mean_reacts', 'children'),
            Output('mean_idx', 'children'),
            Output('react1', 'children'),
            Output('perc1', 'children'),
            Output('react2', 'children'),
            Output('perc2', 'children'),
            Output('react3', 'children'),
            Output('perc3', 'children')
            
        ],
        Input('channel-dropdown', 'value'))
    
    def update_metrics(channel):
        mean_subs_pos, mean_subs_neg, max_subs_pos, max_subs_neg = calculate_mean_max_subs(subs, channel)
        mean_posts_day, mean_posts_week, mean_posts_month = calculate_mean_posts(posts, channel)
        mean_views  = calculate_mean_views(post_view, channel)
        mean_reacts, mean_idx, react1, perc1, react2, perc2, react3, perc3 = calculate_mean_reacts(gr_pvr, channel)
        
        return str(mean_subs_pos), str(mean_subs_neg), str(max_subs_pos), str(max_subs_neg), str(mean_posts_day),\
        str(mean_posts_week), str(mean_posts_month), str(mean_views),\
        str(mean_reacts), f"{mean_idx}%", str(react1), f"{perc1}%", str(react2), f"{perc2}%", str(react3), f"{perc3}%"     

    #-----------------------------Динамика публикаций с индикаторами-------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------
    
    @app.callback(Output('graph1', 'figure'), [Input('channel-dropdown', 'value')])
    def update_graph1(channel):
        
        subdf = posts[posts.channel_name == channel][['channel_name', 'date', 'cnt']].drop_duplicates()
    
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
        colors = ['#8B4513' if val >= 2*mean_cnt else '#F5DEB3' for val in subdf['cnt']]
     
        fig.add_trace(go.Bar(x = subdf.date, y=subdf.cnt, marker_color=colors,
                            hovertemplate='%{x} <br>Публикаций: %{y}<extra></extra>'), row=1, col=1)
        period_names = dict({'days':'вчера', 'weeks': 'неделю', 'months': 'месяц'})

        for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
            
            current, previous = get_current_previous_sums(subdf, 'cnt', period)
                
            fig.add_trace(
                    go.Indicator(
                        value=current,
                        title={"text": f"<span style='font-size:0.8em;color:gray'>Публикаций за {period_names[period[0]]}</span>"},
                        mode="number+delta",
                        delta={'reference': previous, 'relative': True, "valueformat": ".2%"},
                    ), row=i+1, col=2
                )
        
        # Настройки стиля
        fig.update_layout(
            template="simple_white",
            font_family="Georgia",
            font_size=12,
            margin=dict(l=40, r=20, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                rangeselector=dict(  # Добавляем элементы управления диапазоном
                    bgcolor= '#f5dfbf' ,  # Фоновый цвет области с кнопками
                    font=dict(color="#333"),  # Цвет текста на кнопках
                    activecolor= '#ffb347',  # Цвет активной кнопки
                    bordercolor='#f5dfbf',  # Цвет рамки вокруг кнопок                     
                    buttons=list([
                        dict(count=2, label="2д", step="day", stepmode="backward"),
                        dict(count=14, label="2н", step="day", stepmode="backward"),
                        dict(count=2, label="2м", step="month", stepmode="backward"),
                        dict(step="all")  # Кнопка для просмотра всего диапазона
                    ])
                )  ) 
        )
        return fig

    #-----------------------------Динамика подписчиков с индикаторами------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------
    @app.callback(Output('graph2', 'figure'), [Input('channel-dropdown', 'value')])
    def update_graph1(channel):
        
        subdf = subs[subs.channel_name == channel][['channel_name', 'date'
                                                          ,'subs_cnt', 'subs_change', 'datetime']].drop_duplicates()
        subdf.sort_values(by=['channel_name', 'datetime'], inplace=True)
        
        # Создание subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            specs=[
                [ {"rowspan": 3}, {'type': 'indicator'}],
                [None, {'type': 'indicator'}],
                [ None, {'type': 'indicator'}],
          ],
            vertical_spacing=0.08
        )
        
        fig.add_trace(
            go.Scatter(
                x=subdf.datetime,
                y=subdf.subs_cnt,
                fill='tozeroy',
                mode='lines+markers',
                line_color= '#f5dfbf', #'#7F7F7F',
                marker_color='#f5dfbf', #'#7F7F7F',
                marker_line_color='#f5dfbf', #'#7F7F7F',
                marker_line_width=1,
                marker_size=5,
                showlegend=False,
                hovertemplate='%{x}  <br>Подписчиков вс: %{y}<extra></extra>'
            ),
            row=1,
            col=1
        )
            
        period_names = dict({'days':'вчера', 'weeks': 'неделю', 'months': 'месяц'})   
        for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
            subdf.sort_values(by='date', inplace=True)
            current, previous = get_current_previous_sums(subdf, 'subs_change', period)
    
            fig.add_trace(
                go.Indicator(
                    value=current,
                    title={"text": f"<span style='font-size:0.8em;color:gray'>Подписчиков за {period_names[period[0]]}</span>"},
                    mode="number+delta",
                    delta={'reference': previous, 'relative': True, "valueformat": ".2%"},
                ), row=i+1, col=2
            )
    
    
        # Настройки стиля
        fig.update_layout(
            template="simple_white",
            font_family="Georgia",
            font_size=12,
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                rangeselector=dict(  # Добавляем элементы управления диапазоном
                    bgcolor= '#f5dfbf' ,  # Фоновый цвет области с кнопками
                    font=dict(color="#333"),  # Цвет текста на кнопках
                    activecolor= '#ffb347',  # Цвет активной кнопки
                    bordercolor='#f5dfbf',  # Цвет рамки вокруг кнопок                    
                    buttons=list([
                        dict(count=2, label="2д", step="day", stepmode="backward"),
                        dict(count=14, label="2н", step="day", stepmode="backward"),
                        dict(count=2, label="2м", step="month", stepmode="backward"),
                        dict(step="all")  # Кнопка для просмотра всего диапазона
                    ])
                )  ) 
        )
        return fig    


    #-----------------------------График публикаций (матрица)------------------------------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------
    
    # Модифицируем существующий callback
    @app.callback(
        Output('graph3', 'figure'),
        Input('channel-dropdown', 'value'),
        Input("btn-3d", "n_clicks"),
        Input("btn-1w", "n_clicks"),
        Input("btn-1m", "n_clicks"),
        Input("btn-all", "n_clicks")
    )
    def update_graph3(channel, btn_3d_n_clicks, btn_1w_n_clicks, btn_1m_n_clicks, btn_all_n_clicks):
        if channel is None:
            return {}
            
        # Получаем контекст вызова
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = None
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
        # Фильтрация данных в зависимости от нажатой кнопки
        if button_id == "btn-3d":
            filtered_df = posts[(posts.channel_name == channel)&(pd.to_datetime(posts.date)>=date_ago('days', 2))]
        elif button_id == "btn-1w":
            filtered_df = posts[(posts.channel_name == channel)&(pd.to_datetime(posts.date)>=date_ago('weeks', 1))]
        elif button_id == "btn-1m":
            filtered_df = posts[(posts.channel_name == channel)&(pd.to_datetime(posts.date)>=date_ago('months', 1))]
        else:
            filtered_df = posts[(posts.channel_name == channel)&(pd.to_datetime(posts.date)>=date_ago('months', 6))]
    
        # Генерация данных
        filtered_df = filtered_df[['date', 'hour', 'cnt']].rename(columns={'cnt': 'publications'}).sort_values('date')
        raw_index = filtered_df.set_index(['date', 'hour'])
        
        dates = pd.to_datetime(filtered_df.date).unique().tolist()
        index = pd.MultiIndex.from_product([filtered_df.date.unique(), range(1, 25)], names=['date', 'hour'])
        raw = pd.DataFrame(index=index)
        df = raw.merge(raw_index, left_index=True, right_index=True, how='left')
        df.fillna(0, inplace=True)
        df = df.reset_index().drop_duplicates(subset=['date', 'hour']).set_index(['date', 'hour'])
        
        # Преобразование данных в формат, подходящий для heatmap
        z_values = df['publications'].unstack(level=-1)
        x_labels = [str(hour) for hour in range(1,25)]
        y_labels = [date.strftime('%Y-%m-%d') for date in dates]  
        
        fig = go.Figure(
            data=[
               go.Heatmap(
                        z= pd.DataFrame([[1] * len(x_labels)]*len(y_labels), columns=range(1,25), index=y_labels), #[[1] * len(x_labels)] * len(y_labels),  # Матрица одинаковых значений для всех ячеек
                        
                        x=x_labels,
                        y=y_labels,
                        colorscale=[[0, '#ffb347'], [1, '#ffb347']],  # Градиент от белого к темно-синему
                        showscale=False,
                        hovertemplate='%{y} <br>%{x} ч <br>Публикаций: %{z}<extra></extra>'
                    ),
                    go.Heatmap(
                    z=z_values,
                    x=x_labels,
                    y=y_labels,
                    colorscale=[[0, '#F5DEB3'], [1, "#006a4e"]],  # [[0, "#e5e4e2"], [1, "#006a4e"]], Серый цвет для фона
                    showscale=False,
                    xgap=10,  # Зазор между ячейками по горизонтали
                    ygap=10,   # Зазор между ячейками по вертикали
                    hovertemplate='%{y} <br>%{x} ч <br>Публикаций: %{z}<extra></extra>'
                )
            ],
        ).update_layout(
            font_family='Arial',
        
            margin=dict(l=30, r=50, t=50, b=20),
            paper_bgcolor='#ffb347',
            plot_bgcolor='#ffb347',
            legend_title_font_color="#212121",
            legend_font_color="#212121",
            legend_borderwidth=0,
            hoverlabel_font_family='Arial',
            hoverlabel_font_size=12,
            hoverlabel_font_color='#212121',
            hoverlabel_align='auto',
            hoverlabel_namelength=-1,
            hoverlabel_bgcolor='#FAFAFA',
            hoverlabel_bordercolor='#E5E4E2'
            
        )
    
        # Ограничиваем количество меток на оси Y до 10
        if len(y_labels) > 10:
            y_labels_subset = y_labels[::max(len(y_labels)//10,1)]
        else:
            y_labels_subset = y_labels
        
        # Перемещение подписей часов наверх
        fig.update_xaxes(side="top", tickfont=dict(family='Arial', size=12), title_font=dict(family='Arial', size=14))
        
        fig.update_yaxes(
            autorange="reversed",
            ticktext=y_labels,
            tickformat="%b %d, %y",
            tickfont={"family": "Arial", "size": 8},  # Уменьшаем размер шрифта для компактности
            title_font={"family": "Arial", "size": 14}
        )
        
        # Добавляем полосу прокрутки для оси Y
        fig.update_layout(
            font_size=9,
            yaxis_title="Дата",
            xaxis_title="Часы",    
            yaxis=dict(
                autorange="reversed",
     ) 
        )    
        return fig    

    #---------------------------------Подписчики (прирост/отток)------------------------------------------------------------------------
    #-----------------------------------------------------слайдер (ползунок со временем)------------------------------------------------
            
    @app.callback(
        Output('graph-with-slider', 'figure'),
        Input('channel-dropdown', 'value'),
        Input('date-slider', 'value'))
    def update_graph4(channel, slider_range):
        if channel is None or slider_range is None:
            return {}
            
        subdf_channel = subs[subs['channel_name'] == channel]
        
        # Проверяем, что дата присутствует и не пуста
        if len(subdf_channel) == 0 or 'datetime' not in subdf_channel.columns:
            return {}    
        # Преобразуем строку в datetime
        subdf_channel.loc[:, 'datetime'] = pd.to_datetime(subdf_channel['datetime'])
        start_time = subdf_channel['datetime'].min() + pd.Timedelta(seconds=slider_range[0])
        end_time = subdf_channel['datetime'].min() + pd.Timedelta(seconds=slider_range[1])
    
        filtered_df = subdf_channel[(subdf_channel['datetime'] >= start_time) & (subdf_channel['datetime'] <= end_time)]
        
        filtered_df_uniq = filtered_df[['date', 'day_change_pos', 'day_change_neg']].drop_duplicates()
    
        fig = go.Figure()
        fig.add_trace(go.Bar(x=filtered_df_uniq['date'], y=filtered_df_uniq['day_change_pos'], marker_color='#F5DEB3', hovertemplate='%{x} <br>Подписались: %{y} <extra></extra>'))
        fig.add_trace(go.Bar(x=filtered_df_uniq['date'], y=filtered_df_uniq['day_change_neg'], marker_color='#8B0000', hovertemplate='%{x} <br>Отписались: %{y}<extra></extra>'))
    
        fig.update_layout(
            showlegend=False,
            paper_bgcolor= '#ffb347', #'#FFFFFF',
            plot_bgcolor=  '#ffb347', #'#FFFFFF',
            font_family='Georgia',
            title_font_size=24,
            title_x=0.5,
            margin=dict(l=40, r=60, t=40, b=10),
            yaxis_title="Изменение подписок",
            xaxis_title="Дата и время",
            xaxis=dict(
                rangeselector=dict(  # Добавляем элементы управления диапазоном
                    bgcolor= '#f5dfbf' ,  # Фоновый цвет области с кнопками
                    font=dict(color="#333"),  # Цвет текста на кнопках
                    activecolor= '#ffb347',  # Цвет активной кнопки
                    bordercolor='#f5dfbf',  # Цвет рамки вокруг кнопок                
                    buttons=list([
                        dict(count=3, label="3д", step="day", stepmode="backward"),
                        dict(count=7, label="1н", step="day", stepmode="backward"),
                        dict(count=1, label="1м", step="month", stepmode="backward"),
                        dict(step="all")  # Кнопка для просмотра всего диапазона
                    ])
                )  ) 
        )
        return fig


    @app.callback(
        Output('date-slider', 'marks'),
        Input('channel-dropdown', 'value'))
    def update_slider_marks(channel):
        if channel is None:
            return {}
    
        subdf_channel = subs[subs['channel_name'] == channel]
        dates = sorted(subdf_channel.date)
        # Преобразуем список строк в список дат
        dates = [datetime.datetime.strptime(str(date),'%Y-%m-%d') for date in dates]
        date_min = min(dates)
        if len(dates) > 0:
            marks = {
                int(pd.Timedelta(date - date_min).total_seconds()): {
                    'label': date.strftime("%b %d"), #format_date(date, "MMM d", locale='ru_RU').title()
                    'style': {
                        'fontSize': '12px',
                        'color': 'black',
                        'backgroundColor': '#f5dfbf', #'white',
                        'borderRadius': '5px',
                        'padding': '2px',
                        'display': 'block',
                        'width': 'auto',
                        'transform': 'translateX(-50%)'
                    }
                } for date in dates[::len(dates)//6]
            }
        else:
            marks = {}
        return marks    

    #----------------------------------Динамика просмотров по дням (таблица по дням)-------------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------
    @app.callback(
        Output("table-container", "children"),
        Input("hours-slider", "value"),
         Input("channel-dropdown", "value") 
    )
    def update_table(max_days, channel):
        return create_table(post_view, max_days, channel)


    #---------------------------------Визуализация интереса к контенту (пузырьковый график)------------------------------------------
    #--------------------------------------------------------------------------------------------------------------------------------    
    
    # Модифицируем существующий callback
    @app.callback(
        Output('graph6', 'figure'),
        Input('channel-dropdown', 'value'),
        Input("btn-3d_2", "n_clicks"),
        Input("btn-1w_2", "n_clicks"),
        Input("btn-1m_2", "n_clicks"),
        Input("btn-all_2", "n_clicks")
    )
    def update_graph6(channel, btn_3d_n_clicks, btn_1w_n_clicks, btn_1m_n_clicks, btn_all_n_clicks):
        if channel is None:
            return {}
            
        # Получаем контекст вызова
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = None
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
        
        # Фильтрация данных в зависимости от нажатой кнопки  
        def buttons_cond(df, channel, button_id):
            if button_id == "btn-3d_2":
                filtered_df = df[(df.channel_name == channel)&(pd.to_datetime(df.post_datetime.str[:10])>=date_ago('days', 2))]
            elif button_id == "btn-1w_2":
                filtered_df = df[(df.channel_name == channel)&(pd.to_datetime(df.post_datetime.str[:10])>=date_ago('weeks', 1))]
            elif button_id == "btn-1m_2":
                filtered_df = df[(df.channel_name == channel)&(pd.to_datetime(df.post_datetime.str[:10])>=date_ago('months', 1))]
            else:
                filtered_df = df[(df.channel_name == channel)&(pd.to_datetime(df.post_datetime.str[:10])>=date_ago('months', 6))]
                
            return filtered_df
    
        # Генерация данных
        filtered_gr_pvr = buttons_cond(gr_pvr, channel, button_id)
        #table
        gr_pvr_sum = filtered_gr_pvr.drop(['reaction_type', 'react_cnt'], axis=1).drop_duplicates()
    
        if gr_pvr_sum.shape[0] == 0:
            return {}
        
        # Создаем градиент 
        colors = cl.scales['9']['seq']['OrRd'][::-1] 
        
    # Предположим, что у тебя уже есть DataFrame под названием gr_pvr_sum
        fig = go.Figure()
        
        # Добавление точек на график
        fig.add_trace(go.Scatter(
            x=gr_pvr_sum['current_views'],
            y=gr_pvr_sum['idx_active'],
            mode='markers',
            marker=dict(
                size=gr_pvr_sum['react_cnt_sum'],
                color=gr_pvr_sum['current_views'],
                colorscale=colors,
                showscale=False,  # Скрывает colorbar
                sizemode='area',
                sizeref=2. * max(0, max(gr_pvr_sum['react_cnt_sum'])) / (18.**2),
                sizemin=4
            ),
            text=gr_pvr_sum[['post_id']],  # Показывает post_id и дату при наведении
            hoverinfo='text+x+y+z',  # Настройка информации во всплывающей подсказке
            hovertemplate=
                '<b>ID Поста:</b> %{text}<br>' +
                '<b>Текущие Просмотры:</b> %{x}<br>' +
                '<b>Количество реакций:</b> %{marker.size}<br>' +  # Добавлен размер пузыря
                '<b>Активность:</b> %{y} %<extra></extra>'
        ))
        
        # Логарифмическая ось X
        fig.update_xaxes(type="log")
    
    
        # Скрыть colorbar
        fig.update_layout(coloraxis_showscale=False)
    
        fig.update_layout(    
            yaxis_title="Индекс активности, %",
            xaxis_title="Текущее количество просмотров",         
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='rgb(102, 102, 102)',
                tickfont_color='rgb(102, 102, 102)',
                showticklabels=True,
                #dtick=10,
                ticks='outside',
                tickcolor='rgb(102, 102, 102)',
            ),
            margin=dict(l=40, r=60, t=10, b=10),
            showlegend=False,
            paper_bgcolor='#ffb347',
            plot_bgcolor='#ffb347',
            hovermode='closest',
        )
        return fig    

    #---------------Облако слов--------------------------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------


    file_path = 'stopwords-ru.txt'  # Укажите путь к вашему файлу со стоп-словами
    puncts = set(list(string.punctuation) + ['—', '»', '«', '``', '–', "''"])
    stopwords_ru = set(load_stopwords_from_file(file_path))
    predlogi = set(['без' , 'в' , 'до' , 'для' , 'за' , 'из' , 'к' , 'на' , 'над' , 'о' , 'об' , 'от' , 'по' , 'под' , 'пред' , 'при' , 'про' , 'с' , 'у' , 'через']) 
    souzy = set(['а' , 'и' , 'чтобы' , 'если', 'потому что' , 'как будто' , 'то есть'])
    exclude = set(['например', 'какие', 'кто-то', 'что-то', 'кстати', 'многие', 'таких', 'может', 'любой', 'поэтому', 'https'])
    numbers = set('1234567890')
    dell_words = stopwords_ru | predlogi | souzy | numbers | exclude

    @app.callback(Output('image_wc', 'src'), Input('channel-dropdown', 'value'))
    def update_graph7(channel):
            
        posts_channel = posts[posts['channel_name'] == channel]
    
    
        words = posts_channel.text.apply(lambda t: list(set([w.lower() for w in nltk.word_tokenize(t)])- puncts - dell_words)).tolist()
        df_words = pd.DataFrame(Counter(sum(words, [])).most_common(50), columns = ['word', 'count'])
            
        def plot_wordcloud(data):
            d = {a: x for a, x in data.values}
            wc = WordCloud(background_color='#f5dfbf', color_func=gradient_color_func) #, width=480, height=360
            wc.fit_words(d)
            return wc.to_image()
                
        def make_image():
            img = BytesIO()
            plot_wordcloud(data=df_words).save(img, format='PNG')
            return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())
        return make_image()

    #-------------------------Поисковик текста поста по айди---------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------------------------------
    
    @app.callback(
        Output('table_id', 'children'),
        [Input(f'input_{col}', 'value') for col in filter_columns_table_id]
    )

    def update_table(*args):  
        # Проверка наличия введённых значений
        if any(value is not None and value != '' for value in args):
            # Получаем текущие значения фильтров
            filters = dict(zip(filter_columns_table_id, args))
            
            # Создаем маску для фильтрации данных
            mask = pd.Series(True, index=posts.index)  # Начальная маска
            for col, value in filters.items():
                if value is not None and value != '':
                    try:
                        # Преобразуем значение в число, если возможно
                        numeric_value = float(value)
                        
                        # Если столбец содержит числа, применяем числовое сравнение
                        if pd.api.types.is_numeric_dtype(posts[col]):
                            mask &= (posts[col] == numeric_value)
                        else:
                            # Иначе используем текстовое сравнение
                            mask &= (posts[col].astype(str).str.contains(value))
                    except ValueError:
                        # Если преобразование в число невозможно, используем текстовое сравнение
                        mask &= (posts[col].astype(str).str.contains(value))
                    
            # Применяем маску к данным
            filtered_df = posts[columns_table_id][mask]
            
            # Формируем таблицу
            table_rows = [
                html.Tr([html.Th(col) for col in filtered_df.columns]),
                *[
                    html.Tr([html.Td(cell, style={'vertical-align': 'top','padding': '8px'}) for cell in row])
                    for _, row in filtered_df.iterrows()
                ]
            ]
            
            return table_rows
        else:
            return []  # Возвращаем пустую таблицу, если нет введённых значений

    
    return app

