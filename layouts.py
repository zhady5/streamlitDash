from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import string

# Создание компонентов фильтра для каждого столбца таблицы "Поисковика"
filter_columns_table_id = ['id']  #['id','date', 'time',  'text']
filter_components = []
columns_table_id  = ['id','date', 'time',  'text']
#label_style = {'display': 'inline-block', 'vertical-align': 'middle', 'white-space': 'nowrap'}
for col in filter_columns_table_id :
    filter_components.append(
        html.Div([
            dcc.Input(id=f'input_{col}'
                      , placeholder = "Введите номер id поста"
                      , type='text'
                      , style={'width': '100%', 'margin-bottom': '10px', 'color': 'brown', "background-color": '#ffb347'})
        ])
    ) 
    
def create_layout(data):
    channels = data['channels']
    subs = data['subs']
    posts = data['posts']    
    subs['datetime'] = pd.to_datetime(subs['datetime'])
    #Добавляем выпадающий список для названия канала
    filtr_channels = sorted(channels.channel_name.unique())
     
    #-------------------------------------------------------------------------------------------------------------
    # Определение стилей
    styles = {
        'container': {
            'padding': '30px',
            'maxWidth': '1200px',
            'margin': '0 auto',
            'backgroundColor': '#ffb347',
            'boxShadow': '0 10px 15px rgba(0,0,0,0.05)',
            'borderRadius': '10px'
        },
        'header': {
            'backgroundColor': '#ffb347',
            'fontFamily': 'Open Sans, sans-serif', #'Merriweather, serif',
            'fontSize': '28px',
            'lineHeight': '36px',
            'color': '#333',
            'marginTop': '20px',
            'marginBottom': '5px',
            "font-weight": "bold"
        },
        'subheader_title': {
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '16px',
            'lineHeight': '24px',
            'color': '#666',
            'marginBottom': '20px',
            "font-weight": "bold"
        },
        'subheader': {
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '14px',
            'lineHeight': '24px',
            'color': '#666',
            'marginBottom': '10px',
        },
        'dropdown': {
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '14px',
            'lineHeight': '21px',
            'color': '#444',
            'backgroundColor': '#ffb347',  # Фон блока
            'border': '3px solid #f5dfbf',  # Рамки блока
            'borderRadius': '14px',
            'padding': '0px 0px',
            'marginTop': '0px',
            'marginBottom': '0px'
        }
    ,
            'dropdown_options': {  # Дополнительные стили для опций
            'backgroundColor': '#f5dfbf',  # Фон выпадающего списка
            'color': '#444'             # Цвет текста внутри опции
        }
    ,
        'slider': {
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '14px',
            'lineHeight': '21px',
            'color': '#444',
            'marginBottom': '20px',
            "trackBackgroundColor": "lightgray",  # Цвет фона дорожки ползунка
            "highlightColor": "#f5dfbf",             # Цвет выделенной области между ползунками
            "handleBorderColor": "red"       # Цвет рамки ползунков        
        },
        'graph_container': {
            'marginBottom': '40px'
            
        },
        'data_table': {
            'fontFamily': 'Open Sans, sans-serif',
            'fontSize': '12px',
            'lineHeight': '21px',
            'color': '#444',
            'borderCollapse': 'separate', #'collapse',
            'borderSpacing': '0',
            'width': '100%',
            'marginBottom': '40px'
        },
        'data_table_header': {
            'backgroundColor': '#f5dfbf', #'#eaeaea',
            'fontWeight': '600',
            'textAlign': 'left',
            'padding': '8px',
            'borderBottom': '1px solid #ddd'
        },
        'data_table_row': {
            'borderBottom': '1px solid #ddd',
            'padding': '8px'
        },
        'data_table_cell': {
            'padding': '8px',
            'textAlign': 'left',
            'border': '2px solid #ddd',
            'border-radius': '18px'
        }
        , 'buttons': {"font-size": "11px"
                      , 'margin-right': '7px'
                      , "background-color": '#ffb347' 
                      , "border-radius": "35px"
                      , "border-width": "2px"
                      , "border-color": '#f5dfbf'
                      , "box-shadow": "0px"
                      , 'color': 'black'
            
        }
        , 'metric_numbers': {
            'fontSize': '14px'
            , 'color': 'brown'
            , "font-weight": "bold"      
        }
    }
    
            
    # Макет приложения
    return html.Div([
        
        html.Div(className='container', style=styles['container'], children=[
    
         html.Div(className='row', style={'display': 'flex', 'margin-bottom': '40px'}, children=[
         
                 html.Div(style={'width': '67%', 'height': '100%', 'marginRight': '30px'},  children=[   
                    html.H1('Simulative', style=styles['header']),
                    html.H2('Дашборд по анализу Telegram-каналов', style=styles['subheader_title']),
                    html.Div(className='col-md-12', children=[
                            dcc.Dropdown(
                                id='channel-dropdown',
                                options=[{'label': c, 'value': c} for c in posts['channel_name'].unique()],
                                value=posts['channel_name'].unique()[0],
                                clearable=False,
                                #className = 'custom-select',
                                style=styles['dropdown']
                                        )
                            ])
                  ]),
            
                     html.Div(style={'width': '27%', 'height': '100%', 'marginLeft': '30px'},  children=[
                          html.Img(id="image_wc", style={'width': '100%', 'height': '100%'})
                         ])
            ])
    
     , html.Div(className='row', style={'display': 'flex',  'margin-bottom': '40px'}, children=[       
       # Карточки с метриками
    
         # Колонка1
         html.Div(style={'width': '22%', 'height': '100%', 'marginRight': '30px'}, children=[    
                        html.Div([
                            html.Span('📈', style={'fontSize': '24px'}), 
                            html.Span('Средний ежедневный прирост  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_subs_pos', style=styles['metric_numbers'])
                        ]),
                        html.Div([
                            html.Span('📉', style={'fontSize': '24px'}), 
                            html.Span('Средний ежедневный отток  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_subs_neg', style=styles['metric_numbers'])
                        ]),
                        html.Div([
                            html.Span('🚀', style={'fontSize': '24px'}), 
                            html.Span('Максимальный прирост  ', style={'fontSize': '12px'}),
                            html.Span(id='max_subs_pos', style=styles['metric_numbers'])
                        ]),
                        html.Div([
                            html.Span('🆘', style={'fontSize': '24px'}), 
                            html.Span('Максимальный отток  ', style={'fontSize': '12px'}),
                            html.Span(id='max_subs_neg', style=styles['metric_numbers'])
                        ])
         ]),
    
        # Колонка2
        html.Div(style={'width': '22%',  'height': '100%', 'marginRight': '30px'}, children=[         
                        html.Div([
                            html.Span('📋', style={'fontSize': '24px'}), 
                            html.Span('В среднем постов в день  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_posts_day', style=styles['metric_numbers'])
                        ]),
                         html.Div([
                            html.Span('📜', style={'fontSize': '24px'}), 
                            html.Span('В среднем постов в неделю  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_posts_week', style=styles['metric_numbers'])
                        ]),    
                        html.Div([
                            html.Span('🗂️', style={'fontSize': '24px'}), 
                            html.Span('В среднем постов в месяц  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_posts_month', style=styles['metric_numbers'])
                        ]),        
         ]),   
    
        # Колонка3
        html.Div(style={'width': '22%', 'height': '100%', 'marginRight': '30px'}, children=[      
                        html.Div([
                            html.Span('👀', style={'fontSize': '24px'}), 
                            html.Span('В среднем просмотров  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_views', style=styles['metric_numbers'])
                        ]),   
    
     
                        html.Div([
                            html.Span('🐾', style={'fontSize': '24px'}), 
                            html.Span('В среднем реакций  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_reacts', style=styles['metric_numbers'])
                        ]),   
    
                        html.Div([
                            html.Span('💎', style={'fontSize': '24px'}), 
                            html.Span('В среднем уровень активности  ', style={'fontSize': '12px'}),
                            html.Span(id='mean_idx', style=styles['metric_numbers'])
                        ]),   
          ]),
    
        # Колонка4
        html.Div(style={'width': '22%', 'height': '100%', 'marginLeft': '30px'}, children=[         
                        html.Div([
                            html.Span('🥇', style={'fontSize': '24px'}),
                            html.Span('  Доля реакции ', style={'fontSize': '12px'}),
                            html.Span(id='react1', style={'fontSize': '24px'}),
                            html.Span(':  ', style={'fontSize': '12px'}),
                            html.Span(id='perc1', style=styles['metric_numbers'])
                        ]),   
                        html.Div([
                            html.Span('🥈', style={'fontSize': '24px'}),
                            html.Span('  Доля реакции ', style={'fontSize': '12px'}),
                            html.Span(id='react2', style={'fontSize': '24px'}),
                            html.Span(':  ', style={'fontSize': '12px'}),
                            html.Span(id='perc2', style=styles['metric_numbers'])
                        ]), 
                        html.Div([
                            html.Span('🥉', style={'fontSize': '24px'}),
                            html.Span('  Доля реакции ', style={'fontSize': '12px'}),
                            html.Span(id='react3', style={'fontSize': '24px'}),
                            html.Span(':   ', style={'fontSize': '12px'}),
                            html.Span(id='perc3', style=styles['metric_numbers'])
                        ]),         
        ])   
         
     ])
        
       , html.Div(className='row', style={'display': 'flex', 'margin-bottom': '40px'}, children=[
            
                # Правая колонка 
                html.Div(style={'width': '47%', 'height': '100%', 'marginRight': '30px'},  children=[
                    html.Div(className='row', children=[
                        html.Div(className='col-md-12', style=styles['graph_container'], children=[  
                            html.H4("Аудитория на момент измерения", style=styles['subheader_title']),
                             html.P("График показывает изменение общего количества подписчиков с течением времени. Он помогает отслеживать динамику роста аудитории и выявлять периоды активного притока или оттока подписчиков. Анализ графика позволяет корректировать стратегию продвижения и создавать контент, который привлечет и удержит больше подписчиков (Процентные значения индикаторов указывают на изменения по сравнению с предыдущими аналогичными периодами).", style=styles['subheader']),
                                                   
                            dcc.Graph(id='graph2')
                        ]),
    
                        html.Div(className='col-md-12',  style={'marginBottom': '40px'}, children=[
                            html.H4("Динамика подписок", style=styles['subheader_title']),
                            html.P("Этот график показывает два ключевых показателя: количество пользователей, которые подписались на канал, и тех, кто отписался. Он помогает отслеживать, насколько эффективно ваш контент привлекает новую аудиторию и удерживает существующую. Анализируя этот график, можно сделать выводы о том, какие периоды были наиболее успешными в привлечении подписчиков, а также выявить моменты, когда наблюдалось значительное снижение аудитории. Этот анализ позволит вам скорректировать стратегию создания контента и время его публикации для достижения лучших результатов.", style=styles['subheader'])
                            , dcc.Graph(id='graph-with-slider')
                        ]),
    
    
                        html.Div(className='col-md-12', style={'marginBottom': '40px', 'marginTop': '0px'}, children=[
                            dcc.RangeSlider(
                                id='date-slider',
                                min=0,
                                max=(subs['datetime'].max() - subs['datetime'].min()).total_seconds(),
                                value=[0, (subs['datetime'].max() - subs['datetime'].min()).total_seconds()],
                                marks={
                                    int((date - subs['datetime'].min()).total_seconds()): {
                                        'label': date.strftime("%b %d, %H:%M"),
                                        'style': {'fontSize': '12px'}
                                    } for date in subs['datetime'][::len(subs) // 5]
                                },
                                step=None,
                                updatemode='drag'
                            )
                        ]),
    
                        html.Div(className='col-md-12',  style={'marginBottom': '40px'}, children=[
                            html.H4("Визуализация интереса к контенту", style=styles['subheader_title']),
                            html.P("Ось Y здесь показывает, насколько активно аудитория реагирует на ваш контент, а ось X – сколько раз этот контент просмотрен. Чем крупнее пузырек, тем больше реакций собрал пост. Если пузырёк высоко взлетел, значит тема 'зашла' – люди не только смотрят, но и активно реагируют. А вот маленькие и низко расположенные пузырьки подсказывают, что стоит задуматься над изменениями. Этот график поможет вам понять, какие темы цепляют аудиторию, когда лучше всего публиковать новые материалы и как улучшить те посты, которые пока не так популярны.", style=styles['subheader'])
                            #, dcc.Graph(id='graph-with-slider')
                        ]),                    
    
    
                        html.Div(className='col-md-12', style=styles['graph_container'], children=[  
                            #html.H4("Аудитория на момент измерения", style=styles['subheader_title']),
                             #html.P("График показывает изменение общего количества подписчиков с течением времени. Он помогает отслеживать динамику роста аудитории и выявлять периоды активного притока или оттока подписчиков. Анализ графика позволяет корректировать стратегию продвижения и создавать контент, который привлечет и удержит больше подписчиков (Процентные значения индикаторов указывают на изменения по сравнению с предыдущими аналогичными периодами).", style=styles['subheader']),
                             html.Div(
                               # className='d-flex justify-content-end mb-2',  # Bootstrap классы для выравнивания по правому краю
                                children=[
                                    html.Button("3д", id="btn-3d_2", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("1н", id="btn-1w_2", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("1м", id="btn-1m_2", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("All (6м)", id="btn-all_2", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat")
                                ]
                            )                                               
                            , dcc.Graph(id='graph6')
                        ]),
                        
                    ])
                ]),
    
                # Левая колонка с графиками
                html.Div(style={'width': '47%', 'height': '100%', 'marginLeft': '30px'}, children=[
                         
                    html.Div(className='row', children=[
                        html.Div(className='col-md-12', style=styles['graph_container'], children=[
                            html.H4("Суточные показатели публикаций", style=styles['subheader_title']),
                             html.P("График показывает количество публикаций конкурента. Процентные значения  за разные периоды (день, неделя и месяц) указывают на изменения активности по сравнению с предыдущими аналогичными периодами. Анализ этих данных поможет понять, как часто и интенсивно конкурент публикует материалы, что может быть полезным для корректировки вашей собственной стратегии создания контента.", style=styles['subheader']),
                            dcc.Graph(id='graph1')
                        ]),
                        
                        html.Div(className='col-md-12', children=[
                            html.H4("График публикаций", style=styles['subheader_title']),
                            html.P("Этот график является полезным инструментом для понимания того, когда ваши конкуренты выпускают контент или если вы планируете протестировать новый график публикации своих постов (учитываются последние шесть месяцев).", style=styles['subheader']),
                               # Контейнер для кнопок
                            html.Div(
                               # className='d-flex justify-content-end mb-2',  # Bootstrap классы для выравнивания по правому краю
                                children=[
                                    html.Button("3д", id="btn-3d", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("1н", id="btn-1w", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("1м", id="btn-1m", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat"),
                                    html.Button("All (6м)", id="btn-all", n_clicks=0, style=styles['buttons'], className="btn btn-primary btn-flat")
                                ]
                            )
                            
                            
                            , dcc.Graph(id='graph3')
    
    
                        ]),
    
                        html.Div(className='col-md-12', style={'overflow-y': 'auto', 'max-height': '870px', 'margin-left': '20px'}, children=[
                            html.H4("Динамика просмотров по дням", style=styles['subheader_title']),
                            html.P("Эта таблица помогает определить оптимальное время для публикаций: если в первые сутки после публикации она собирает более 35% всех просмотров, это успешное время публикации; иначе стоит пересмотреть график размещения контента, чтобы новые публикации не затерялись среди конкурентов. Также можно обнаружить возможную мошенническую активность: например, если за одни сутки видео набирает 80% общего количества просмотров, следует проявить осторожность, проанализировать частоту подобных аномалий и сделать выводы (проценты приведены, как пример).", style=styles['subheader'])
                            
                            , dcc.Slider(
                                id='hours-slider',
                                min=0,
                                max=72,
                                step=1,
                                value=5,
                                marks={i: str(i) + 'д' for i in range(1, 73, 4)} 
                                , className='my-custom-slider' 
                            ),
                            html.Table(id='table-container', style=styles['data_table'], children=[
                                html.Thead(children=[
                                    html.Tr(children=[
                                        html.Th('ID поста и дата', style=styles['data_table_header']),
                                        html.Th('Текущие просмотры', style=styles['data_table_header']),
                                        *[html.Th(f'{i}д', style=styles['data_table_header']) for i in range(1, 25)]
                                    ])
                                ]),
                                html.Tbody(id='table-body', children=[])
                            ])
                        ])
    
                        , html.Div(className='col-md-12', style={'marginTop': '50px'}, children=[
                            html.H4("Просмотр текста поста и даты по номеру ID: ", style=styles['subheader']),
                            # Фильтры
                            *filter_components,
                                    # Таблица
                                    html.Br(),
                                    html.Table(id='table_id')                        
                        ]),
                    ])
                ]),
            
            ])
        ])
    ], style={'font-family': 'Open Sans, sans-serif'})
