#from asyncio.windows_events import NULL
#from turtle import width
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import altair as alt
from datetime import datetime, date, time,timedelta
import copy
import plotly.figure_factory as ff
import plotly.express as px
import requests

import json
import streamlit_authenticator as stauth
import pytz

mood=["幸せではない","やや幸せではない","ふつう","やや幸せ","幸せ"]
happy_score = ['選択して下さい（0〜10点）',0,1,2,3,4,5,6,7,8,9,10]
today = date.today()
day_list=[]
diary_list=[]
url = st.secrets['URL']

def main():
    ty = today.year
    tm = today.month
    td = today.day

    past_day= today-timedelta(days=13)
    past_y = past_day.year
    past_m = past_day.month
    past_d = past_day.day
    
    team_list=('全てのチーム',
        'A','Y','Z'
        )

    with st.sidebar:
        st.markdown('**集計条件を指定して下さい**')
        selected_team = 'Z'
        from_day = st.date_input(
            '↓集計期間の開始日をお選び下さい',past_day
            )
        to_day = st.date_input(
            '↓集計期間の終了日をお選び下さい',today
            )
        run = st.button('集計実行')
        
    from_native = datetime.combine(from_day, time())
    from_day = pytz.timezone('Asia/Tokyo').localize(from_native)
    from_day = datetime.fromordinal(from_day.toordinal())
    to_native = datetime.combine(to_day, time())
    to_day = pytz.timezone('Asia/Tokyo').localize(to_native)
    to_day = datetime.fromordinal(to_day.toordinal())


    if run:
        #Answers

        st.subheader('チームごとの回答数（1ユーザー1カウントで集計）')                
        st.caption('※指定した期間内の合計をカウント')


        #my_happy

        st.subheader('「あなたは一日幸せでしたか？」への回答スコア')                
        st.caption('水色の線：チームの平均スコア／水色の丸：チームの個別スコア')
        st.caption('※水色の丸の大きさはスコアごとの人数を表しています')
        r_fb = requests.get(url + '/get_fb_all')
        r_fb_DB = r_fb.json()
        df_fb=pd.DataFrame.from_dict(r_fb_DB,orient='index').T

        df_fb['date']=pd.to_datetime(df_fb['date'])
        day_list=[]
        for days in df_fb['date']:
            day_list.append(days + timedelta(hours=-9))
        df_fb['date'] = day_list
        
        df_fb = df_fb.dropna(subset=['my_happy'])

        if selected_team != '全てのチーム':
            df_fb = df_fb[df_fb['team_url']==selected_team]
        df_fb = df_fb[(df_fb['date'] >= from_day) & (df_fb['date'] <= to_day)]

        line = alt.Chart(df_fb).mark_line(
            color='lightskyblue'
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(my_happy):Q',
                    axis=alt.Axis(titleFontSize=18, title='「あなたの幸せ」スコア'),
                    scale=alt.Scale(domainMax=10,domainMin=0)
                    )
        ).properties(
            width=650,
            height=400
            )

        points = alt.Chart(df_fb).mark_circle(
            color='lightskyblue'
        ).encode(
            x=alt.X('date:T'),
            y=alt.Y('my_happy:Q'),
            size = 'count()'
        ).properties(
            width=650,
            height=400
            )

        layer = alt.layer(line,points
        ).configure_axis(
            grid=False
        )

        st.write(layer)


        #group_happy

        r_group = requests.get(url + '/get_group')
        r_group_DB = r_group.json()
        df_group=pd.DataFrame.from_dict(r_group_DB,orient='index').T
        df_group['date']=pd.to_datetime(df_group['date'])

        day_list=[]
        for days in df_group['date']:
            day_list.append(days + timedelta(hours=-9))
        df_group['date'] = day_list
        
        df_group = df_group.dropna(subset=['group_happy'])

        st.subheader('「チームとしては幸せだったと思いますか？」への回答スコア')                
        st.caption('水色の線：チームの平均スコア／水色の丸：チームの個別スコア')
        st.caption('※水色の丸の大きさはスコアごとの人数を表しています')

        if selected_team != '全てのチーム':
            df_group = df_group[df_group['team_url']==selected_team]
        df_group = df_group[(df_group['date'] >= from_day) & (df_group['date'] <= to_day)]

        line_group = alt.Chart(df_group).mark_line(
            color='lightskyblue'
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(group_happy):Q',
                    axis=alt.Axis(titleFontSize=18, title='「チームの幸せ」スコア'),
                    scale=alt.Scale(domainMax=10,domainMin=0)
                    )
        ).properties(
            width=650,
            height=400
            )

        points_group = alt.Chart(df_group).mark_circle(
            color='lightskyblue'
        ).encode(
            x=alt.X('date:T'),
            y=alt.Y('group_happy:Q'),
            size = 'count()'
        ).properties(
            width=650,
            height=400
            )

        layer_group = alt.layer(line_group,points_group
        ).configure_axis(
            grid=False
        )

        st.write(layer_group)


        #emotion

        r_emo = requests.get(url + '/get_emo')
        r_emo_DB = r_emo.json()
        df_emo=pd.DataFrame.from_dict(r_emo_DB,orient='index').T

        df_emo['date']=pd.to_datetime(df_emo['date'])
        day_list=[]
        for days in df_emo['date']:
            day_list.append(days + timedelta(hours=-9))
        df_emo['date'] = day_list

        if selected_team != '全てのチーム':
            df_emo = df_emo[df_emo['team_url']==selected_team]
        df_emo = df_emo[(df_emo['date'] >= from_day) & (df_emo['date'] <= to_day)]

        df_emo=pd.melt(
            df_emo,
            id_vars=['date'],
            value_vars=['怒り','不安','嫌悪','楽しさ','悲しみ','驚き','信頼'],
            var_name='emotion',
            value_name='score')

        r_time_emo = requests.get(url + '/get_emo_time')
        time_emo_dic = r_time_emo.json()
        time_emo = time_emo_dic['update']

        st.subheader('日記の感情スコア')
        st.text('データ更新日時　＞＞　'+ time_emo)
        line_emo = alt.Chart(df_emo).mark_line(
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(score):Q',axis=alt.Axis(titleFontSize=18, title='感情スコア')),
            color='emotion:N'
        ).properties(
            width=650,
            height=400,
            )

        st.write(alt.layer(line_emo).configure_axis(grid=False))


        #愚痴スコア

        r_gch = requests.get(url + '/get_gch')
        r_gch_DB = r_gch.json()
        df_gch=pd.DataFrame.from_dict(r_gch_DB,orient='index').T

        df_gch['date']=pd.to_datetime(df_gch['date'])
        day_list=[]
        for days in df_gch['date']:
            day_list.append(days + timedelta(hours=-9))
        df_gch['date'] = day_list

        if selected_team != '全てのチーム':
            df_gch = df_gch[df_gch['team_url']==selected_team]
        df_gch = df_gch[(df_gch['date'] >= from_day) & (df_gch['date'] <= to_day)]

        r_time_gch = requests.get(url + '/get_gch_time')
        time_gch = r_time_gch.json()['update']

        st.subheader('日記の「愚痴っぽさ」スコア')
        st.caption('緑色の線：チームの平均スコア／緑色の丸：チームの個別スコア')
        st.caption('※緑色の丸の大きさはスコアごとの人数を表しています')
        st.text('データ更新日時　＞＞　'+ time_gch)
        line_gch = alt.Chart(df_gch).mark_line(
            color='olive'
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(pred):Q',axis=alt.Axis(titleFontSize=18, title='愚痴スコア'))
        ).properties(
            width=650,
            height=400,
            )

        points_gch = alt.Chart(df_gch).mark_circle(
            color='lightgreen'
        ).encode(
            x=alt.X('date:T'),
            y=alt.Y('pred:Q'),
            size = 'count()'
        ).properties(
            width=650,
            height=400
            )

        st.write(alt.layer(line_gch,points_gch).configure_axis(grid=False))


        #文字数・語彙数

        r_lang = requests.get(url + '/get_lang')
        r_lang_DB = r_lang.json()
        df_lang=pd.DataFrame.from_dict(r_lang_DB,orient='index').T

        df_lang['date']=pd.to_datetime(df_lang['date'])
        day_list=[]
        for days in df_lang['date']:
            day_list.append(days + timedelta(hours=-9))
        df_lang['date'] = day_list

        if selected_team != '全てのチーム':
            df_lang = df_lang[df_lang['team_url']==selected_team]
        df_lang = df_lang[(df_lang['date'] >= from_day) & (df_lang['date'] <= to_day)]
        #write(df_lang)

        st.subheader('日記の文字数（チーム平均）')
        line_lang = alt.Chart(df_lang).mark_line(
            color='red'
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(len):Q',axis=alt.Axis(titleFontSize=18, title='日記の文字数（チーム平均）'))
        ).properties(
            width=650,
            height=400,
            )

        st.write(alt.layer(line_lang).configure_axis(grid=False))

        st.subheader('日記の語彙数（チーム平均）')
        line_lang = alt.Chart(df_lang).mark_line(
            color='orange'
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(voc_count):Q',axis=alt.Axis(titleFontSize=18, title='日記の語彙数（チーム平均）'))
        ).properties(
            width=650,
            height=400,
            )

        st.write(alt.layer(line_lang).configure_axis(grid=False))


        #品詞数

        r_pos = requests.get(url + '/get_pos')
        r_pos_DB = r_pos.json()
        df_pos=pd.DataFrame.from_dict(r_pos_DB,orient='index').T
        #st.write(df_pos)

        df_pos['date']=pd.to_datetime(df_pos['date'])
        day_list=[]
        for days in df_pos['date']:
            day_list.append(days + timedelta(hours=-9))
        df_pos['date'] = day_list

        if selected_team != '全てのチーム':
            df_pos = df_pos[df_pos['team_url']==selected_team]
        df_pos = df_pos[(df_pos['date'] >= from_day) & (df_pos['date'] <= to_day)]

        df_pos=pd.melt(
            df_pos,
            id_vars=['date'],
            value_vars=['名詞','動詞','形容詞'],
            var_name='品詞',
            value_name='出現数')    

        st.subheader('品詞出現数（名詞・動詞・形容詞）')
        line_pos = alt.Chart(df_pos).mark_line(
        ).encode(
            x=alt.X('date:T',
                    axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                    scale=alt.Scale(domainMax={"year": to_day.year, "month": to_day.month, "date": to_day.day},
                                    domainMin={"year": from_day.year, "month": from_day.month, "date": from_day.day})
                    ),
            y=alt.Y('mean(出現数):Q',axis=alt.Axis(titleFontSize=18, title='品詞数（総数カウント）')),
            color='品詞:N'
        ).properties(
            width=650,
            height=400,
            )

        st.write(alt.layer(line_pos).configure_axis(grid=False))



#感情のばらつきスコア（各emotionごとの分散の平均？）
#主体性スコア（動詞の能動表現数/受動表現数）
#時制スコア（過去形・現在形・未来形の割合）
#（固有名詞を除いたワードクラウド？）


# ユーザ情報。引数
names = ['admin'] 
usernames = ['admin']  # 入力フォームに入力された値と合致するか確認される
passwords = ['admin']  # 入力フォームに入力された値と合致するか確認される

# パスワードをハッシュ化。 リスト等、イテラブルなオブジェクトである必要がある
hashed_passwords = stauth.Hasher(passwords).generate()

# cookie_expiry_daysでクッキーの有効期限を設定可能。
#認証情報の保持期間を設定でき値を0とするとアクセス毎に認証を要求する
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)

# ログインメソッドで入力フォームを配置
st.title(':hatching_chick: チームのWell-being（計測ダッシュボード）')
name, authentication_status, username = authenticator.login('Login', 'main')

# 返り値、authenticaton_statusの状態で処理を場合分け
if authentication_status:
    # logoutメソッドでaurhenciationの値をNoneにする
    authenticator.logout('Logout', 'main')
    st.write('Welcome *%s*' % (name))
    main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
