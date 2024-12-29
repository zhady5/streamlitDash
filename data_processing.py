import pandas as pd
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math

def load_data():
    folder_path = os.getcwd()
    file_list = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    
    channels = pd.read_csv(os.path.join(folder_path, file_list[0]))
    posts = pd.read_csv(os.path.join(folder_path, file_list[1]))
    reactions = pd.read_csv(os.path.join(folder_path, file_list[2]))
    subscribers = pd.read_csv(os.path.join(folder_path, file_list[3]))
    views = pd.read_csv(os.path.join(folder_path, file_list[4]))
    
    return channels, posts, reactions, subscribers, views

def process_data(channels, posts, reactions, subscribers, views):
    # Process posts
    posts = process_posts(posts, channels)
    
    # Process views
    views = process_views(views)
    
    # Process subscribers
    subs = process_subscribers(subscribers, channels)
    
    # Process reactions
    reacts = process_reactions(reactions)
    
    # Combine post and view data
    post_view = combine_post_view_data(posts, views)
    
    # Combine post, view, and reaction data
    gr_pvr = combine_post_view_reaction_data(post_view, reacts)
    
    return {
        'channels': channels,
        'posts': posts,
        'views': views,
        'subs': subs,
        'reacts': reacts,
        'post_view': post_view,
        'gr_pvr': gr_pvr
    }

def process_posts(posts, channels):
    posts.rename(columns={'date': 'datetime'}, inplace=True)
    posts = posts.merge(channels[['id', 'channel_name']].rename(columns={'id':'channel_id'}), on='channel_id', how='left')
    posts['date'] = pd.to_datetime(posts.datetime).dt.date
    posts['time'] = posts.datetime.str[10:]
    posts['cnt'] = posts.groupby(['channel_id', 'date'])['message_id'].transform('count')
    posts['hour'] = pd.to_datetime(posts.datetime).dt.hour
    return posts[~posts.text.isnull() & (posts.text != 'Нет текста')].copy()

def process_views(views):
    views = views.rename(columns={'timestamp': 'datetime', 'views': 'view_cnt'})
    views['date'] = pd.to_datetime(views.datetime).dt.date
    view_change = views.sort_values(by=['post_id', 'datetime']).groupby('post_id')['view_cnt'].diff().rename('view_change')
    views = views.merge(view_change, left_index=True, right_index=True)
    views['view_change'] = views['view_change'].fillna(views['view_cnt'])
    return views

def process_subscribers(subscribers, channels):
    subs = subscribers.rename(columns={'timestamp': 'datetime', 'subscriber_count': 'subs_cnt'})
    subs['date'] = pd.to_datetime(subs.datetime).dt.date
    subs = subs.merge(channels[['id', 'channel_name']].rename(columns={'id':'channel_id'}), on='channel_id', how='left')
    subs = subs.sort_values(by=['channel_id', 'datetime'])
    subs['subs_change'] = subs.groupby('channel_id')['subs_cnt'].diff().fillna(0)
    subs['subs_change_pos'] = subs['subs_change'].clip(lower=0)
    subs['subs_change_neg'] = subs['subs_change'].clip(upper=0)
    subs['day_change_pos'] = subs.groupby(['channel_id', 'date'])['subs_change_pos'].transform('sum')
    subs['day_change_neg'] = subs.groupby(['channel_id', 'date'])['subs_change_neg'].transform('sum')
    return subs

def process_reactions(reactions):
    reacts = reactions.rename(columns={'timestamp': 'datetime', 'count': 'react_cnt'})
    reacts['date'] = pd.to_datetime(reacts.datetime).dt.date
    return reacts

def combine_post_view_data(posts, views):
    post_view = views[['post_id', 'view_cnt', 'view_change', 'datetime']].merge(
        posts[['id', 'channel_name', 'date', 'datetime']].rename(columns={'id': 'post_id', 'datetime': 'post_datetime'}),
        on='post_id'
    )[['channel_name', 'post_id', 'post_datetime', 'datetime', 'view_cnt', 'view_change']]
    post_view = post_view.sort_values(by=['channel_name', 'post_id', 'datetime']).reset_index(drop=True)
    post_view['hours_diff'] = (pd.to_datetime(post_view.datetime) - pd.to_datetime(post_view.post_datetime)).dt.total_seconds() / 3600
    post_view['days_diff'] = post_view['hours_diff'] / 24
    post_view['hours_diff'] = post_view['hours_diff'].apply(lambda x: math.ceil(x))
    post_view['days_diff'] = post_view['days_diff'].apply(lambda x: math.ceil(x))
    post_view['hours_group'] = pd.cut(post_view['hours_diff'], bins=list(range(0, 74)), labels=list(range(1, 74))).fillna(73)
    post_view['current_views'] = post_view.groupby('post_id')['view_cnt'].transform('last')
    post_view['percent_new_views'] = (post_view['view_change'] / post_view['current_views']) * 100
    return post_view.sort_values(by=['channel_name', 'post_datetime'], ascending=False)

def combine_post_view_reaction_data(post_view, reacts):
    group_reacts = reacts.groupby(['post_id', 'reaction_type'])[['datetime', 'react_cnt']].last().reset_index()
    group_post_view = post_view.groupby(['channel_name', 'post_datetime', 'post_id', 'current_views'])[['datetime']].last().reset_index()
    group_reacts['datetime_format'] = pd.to_datetime(group_reacts.datetime).dt.strftime('%Y-%m-%d %H:%M:%S')
    group_post_view['datetime_format'] = pd.to_datetime(group_post_view.datetime).dt.strftime('%Y-%m-%d %H:%M:%S')
    group_reacts.drop('datetime', axis=1, inplace=True)
    group_post_view.drop('datetime', axis=1, inplace=True)
    gr_pvr = group_post_view.merge(group_reacts, on=['post_id', 'datetime_format'], how='left').drop_duplicates()
    gr_pvr = gr_pvr[~gr_pvr.react_cnt.isnull()].copy()
    gr_pvr['react_cnt_sum'] = gr_pvr.groupby('post_id')['react_cnt'].transform('sum')
    gr_pvr['idx_active'] = round(gr_pvr.react_cnt_sum / gr_pvr.current_views * 100, 2)
    return gr_pvr

