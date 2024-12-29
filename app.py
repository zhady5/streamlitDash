import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import logging

from data_processing import load_data, process_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="Telegram Channel Analytics", layout="wide")

# Load and process data
channels, posts, reactions, subscribers, views = load_data()
processed_data = process_data(channels, posts, reactions, subscribers, views)

if processed_data is None:
    st.error("Не удалось загрузить или обработать данные. Пожалуйста, проверьте файлы данных и попробуйте снова.")
    st.stop()

# Sidebar for channel selection
st.sidebar.title("Channel Selection")
selected_channel = st.sidebar.selectbox(
    "Choose a channel",
    options=processed_data['posts']['channel_name'].unique(),
    index=0
)

# Main content
st.title("Telegram Channel Analytics Dashboard")

# Publication Trend and Subscriber Growth
col1, col2 = st.columns(2)

with col1:
    st.subheader("Publication Trend")
    df = processed_data['posts'][processed_data['posts'].channel_name == selected_channel]
    if not df.empty and 'date' in df.columns:
        df = df.groupby('date').size().reset_index(name='count')
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Daily Publications', 'Publication Trend'))
        
        fig.add_trace(go.Bar(x=df['date'], y=df['count'], name='Daily Publications'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['date'], y=df['count'].rolling(window=7).mean(),
                                 name='7-day Moving Average'), row=2, col=1)
        
        fig.update_layout(height=400, title_text=f"Publication Trend for {selected_channel}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных о публикациях для выбранного канала.")

with col2:
    st.subheader("Subscriber Growth")
    df = processed_data['subs'][processed_data['subs'].channel_name == selected_channel]
    if not df.empty and 'datetime' in df.columns and 'subs_cnt' in df.columns and 'subs_change' in df.columns:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('Total Subscribers', 'Daily Subscriber Change'))
        
        fig.add_trace(go.Scatter(x=df['datetime'], y=df['subs_cnt'], name='Total Subscribers'), row=1, col=1)
        fig.add_trace(go.Bar(x=df['datetime'], y=df['subs_change'], name='Daily Change'), row=2, col=1)
        
        fig.update_layout(height=400, title_text=f"Subscriber Growth for {selected_channel}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных о подписчиках для выбранного канала.")

# Channel Metrics
st.subheader("Channel Metrics")
col1, col2, col3, col4 = st.columns(4)

subs = processed_data['subs']
posts = processed_data['posts']
post_view = processed_data['post_view']
gr_pvr = processed_data['gr_pvr']

subs_channel = subs[subs.channel_name == selected_channel]
posts_channel = posts[posts.channel_name == selected_channel]
post_view_channel = post_view[post_view.channel_name == selected_channel]
gr_pvr_channel = gr_pvr[gr_pvr.channel_name == selected_channel]

with col1:
    if not subs_channel.empty and 'day_change_pos' in subs_channel.columns and 'day_change_neg' in subs_channel.columns:
        st.metric("Avg Daily Gain", f"{subs_channel.day_change_pos.mean():.2f}")
        st.metric("Avg Daily Loss", f"{subs_channel.day_change_neg.mean():.2f}")
        st.metric("Max Daily Gain", f"{subs_channel.day_change_pos.max():.2f}")
        st.metric("Max Daily Loss", f"{subs_channel.day_change_neg.min():.2f}")
    else:
        st.warning("Нет данных о изменениях подписчиков.")

with col2:
    if not posts_channel.empty and 'date' in posts_channel.columns:
        posts_channel['date'] = pd.to_datetime(posts_channel['date'])
        st.metric("Avg Posts/Day", f"{posts_channel.groupby('date').size().mean():.2f}")
        st.metric("Avg Posts/Week", f"{posts_channel.groupby(pd.Grouper(key='date', freq='W')).size().mean():.2f}")
        st.metric("Avg Posts/Month", f"{posts_channel.groupby(pd.Grouper(key='date', freq='M')).size().mean():.2f}")
    else:
        st.warning("Нет данных о постах.")

with col3:
    if not post_view_channel.empty and 'current_views' in post_view_channel.columns:
        st.metric("Avg Views/Post", f"{post_view_channel.groupby('post_id')['current_views'].first().mean():.2f}")
        if not gr_pvr_channel.empty and 'react_cnt_sum' in gr_pvr_channel.columns and 'idx_active' in gr_pvr_channel.columns:
            st.metric("Avg Reactions/Post", f"{gr_pvr_channel.groupby('post_id')['react_cnt_sum'].first().mean():.2f}")
            st.metric("Avg Activity Index", f"{gr_pvr_channel.groupby('post_id')['idx_active'].first().mean():.2f}%")
        else:
            st.warning("Нет данных о реакциях.")
    else:
        st.warning("Нет данных о просмотрах.")

with col4:
    st.subheader("Top Reactions")
    if not gr_pvr_channel.empty and 'reaction_type' in gr_pvr_channel.columns and 'react_cnt' in gr_pvr_channel.columns:
        top_reactions = gr_pvr_channel.groupby('reaction_type')['react_cnt'].sum().nlargest(3)
        for reaction, count in top_reactions.items():
            st.text(f"{reaction}: {count}")
    else:
        st.warning("Нет данных о топ реакциях.")

# Publication Heatmap and Subscriber Change
col1, col2 = st.columns(2)

with col1:
    st.subheader("Publication Heatmap")
    df = processed_data['posts'][processed_data['posts'].channel_name == selected_channel]
    if not df.empty and 'date' in df.columns and 'hour' in df.columns:
        pivot = df.pivot_table(values='message_id', index='date', columns='hour', aggfunc='count', fill_value=0)
        
        fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale='Viridis'))
        fig.update_layout(title=f'Publication Heatmap for {selected_channel}', xaxis_title='Hour of Day', yaxis_title='Date')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Недостаточно данных для построения тепловой карты публикаций.")

with col2:
    st.subheader("Subscriber Change")
    df = processed_data['subs'][processed_data['subs'].channel_name == selected_channel]
    if not df.empty and 'datetime' in df.columns and 'subs_change' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        date_range = st.slider(
            "Select Date Range",
            min_value=df['datetime'].min().date(),
            max_value=df['datetime'].max().date(),
            value=(df['datetime'].min().date(), df['datetime'].max().date())
        )
        
        mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
        df_filtered = df.loc[mask]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_filtered['datetime'], y=df_filtered['subs_change'], name='Subscriber Change'))
        fig.update_layout(title=f'Subscriber Change for {selected_channel}', xaxis_title='Date', yaxis_title='Change in Subscribers')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Недостаточно данных для отображения изменений подписчиков.")

# Post Performance Analysis
st.subheader("Post Performance Analysis")
hours = st.slider("Select Hours", min_value=1, max_value=72, value=24, step=1)

df = processed_data['post_view']
if not df.empty and 'channel_name' in df.columns and 'hours_diff' in df.columns:
    df = df[(df.channel_name == selected_channel) & (df.hours_diff <= hours)]
    df = df.sort_values('post_datetime', ascending=False).head(10)  # Show only the 10 most recent posts

    if not df.empty:
        st.dataframe(df[['post_id', 'post_datetime', 'current_views', 'view_change', 'percent_new_views']])
    else:
        st.warning("Нет данных о производительности постов для выбранного периода.")
else:
    st.warning("Недостаточно данных для анализа производительности постов.")

# Add error logging
if st.button('Show Error Log'):
    with open('streamlit_app.log', 'r') as log_file:
        st.text(log_file.read())

