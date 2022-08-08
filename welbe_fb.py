#from asyncio.windows_events import NULL
#from turtle import width
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import altair as alt
import datetime
import copy
import plotly.figure_factory as ff
import plotly.express as px
import requests

import json
import streamlit_authenticator as stauth

mood=["幸せではない","やや幸せではない","ふつう","やや幸せ","幸せ"]
happy_score = ['選択して下さい（0〜10点）',0,1,2,3,4,5,6,7,8,9,10]
today = datetime.date.today()
day_list=[]
diary_list=[]
url = 'http://aoi.naist.jp/wellbeing'

def main():
    r_fb = requests.get(url + '/get_fb_all')
    r_fb_DB = r_fb.json()
    df_fb=pd.DataFrame.from_dict(r_fb_DB,orient='index').T
    df_fb['date']=pd.to_datetime(df_fb['date'])

    day_list=[]
    for days in df_fb['date']:
        day_list.append(days + datetime.timedelta(hours=-9))
    df_fb['date'] = day_list

    st.subheader('2週間 Well-beingスコア')                
    ty = today.year
    tm = today.month
    td = today.day

    past_day= today-datetime.timedelta(days=13)
    past_y = past_day.year
    past_m = past_day.month
    past_d = past_day.day

    st.caption('水色の線：チームの平均スコア／水色の丸：チームの個別スコア')
    st.caption('※水色の丸の大きさはスコアごとの人数を表しています')
    line = alt.Chart(df_fb).mark_line(
        color='lightskyblue'
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(my_happy):Q',
                axis=alt.Axis(titleFontSize=18, title='Well-beingスコア'),
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


    r_emo = requests.get(url + '/get_emo')
    r_emo_DB = r_emo.json()
    df_emo=pd.DataFrame.from_dict(r_emo_DB,orient='index').T
    
    df_emo['date']=pd.to_datetime(df_emo['date'])
    day_list=[]
    for days in df_emo['date']:
        day_list.append(days + datetime.timedelta(hours=-9))
    df_emo['date'] = day_list

    df_emo=pd.melt(
        df_emo,
        id_vars=['date'],
        value_vars=['anger','anxiety','dislike','fan','sad','surprise','trust'],
        var_name='emotion',
        value_name='score')    

    st.subheader('2週間 感情スコア')
    line_emo = alt.Chart(df_emo).mark_line(
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m月%d日",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(score):Q',axis=alt.Axis(titleFontSize=18)),
        color='emotion:N'
    ).properties(
        width=650,
        height=400,
        )

    st.write(alt.layer(line_emo).configure_axis(grid=False))


    r_gch = requests.get(url + '/get_gch')
    r_gch_DB = r_gch.json()
    df_gch=pd.DataFrame.from_dict(r_gch_DB,orient='index').T
    #st.table(df_gch)

    st.subheader('2週間 愚痴スコア')
    line_gch = alt.Chart(df_gch).mark_line(
        color='olive'
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m月%d日",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(pred):Q',axis=alt.Axis(titleFontSize=18))
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


    r_lang = requests.get(url + '/get_lang')
    r_lang_DB = r_lang.json()
    df_lang=pd.DataFrame.from_dict(r_lang_DB,orient='index').T

    df_lang['date']=pd.to_datetime(df_lang['date'])
    day_list=[]
    for days in df_lang['date']:
        day_list.append(days + datetime.timedelta(hours=-9))
    df_lang['date'] = day_list
    
    #write(df_lang)

    st.subheader('2週間 日記文字数')
    line_lang = alt.Chart(df_lang).mark_line(
        color='olive'
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m月%d日",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(len):Q',axis=alt.Axis(titleFontSize=18))
    ).properties(
        width=650,
        height=400,
        )

    st.write(alt.layer(line_lang).configure_axis(grid=False))

    st.subheader('2週間 日記語彙数')
    line_lang = alt.Chart(df_lang).mark_line(
        color='olive'
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m月%d日",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(voc_count):Q',axis=alt.Axis(titleFontSize=18))
    ).properties(
        width=650,
        height=400,
        )

    st.write(alt.layer(line_lang).configure_axis(grid=False))


    r_pos = requests.get(url + '/get_pos')
    r_pos_DB = r_pos.json()
    df_pos=pd.DataFrame.from_dict(r_pos_DB,orient='index').T
    #st.write(df_pos)

    #品詞数
    df_pos['date']=pd.to_datetime(df_pos['date'])
    day_list=[]
    for days in df_pos['date']:
        day_list.append(days + datetime.timedelta(hours=-9))
    df_pos['date'] = day_list

    df_pos=pd.melt(
        df_pos,
        id_vars=['date'],
        value_vars=['noun','verb','adjective'],
        var_name='品詞',
        value_name='出現数')    

    st.subheader('2週間 品詞出現数')
    line_pos = alt.Chart(df_pos).mark_line(
    ).encode(
        x=alt.X('date:T',
                axis=alt.Axis(format="%m月%d日",labelFontSize=14, titleFontSize=18,title='日付'),
                scale=alt.Scale(domainMax={"year": ty, "month": tm, "date": td},
                                domainMin={"year": past_y, "month": past_m, "date": past_d})
                ),
        y=alt.Y('mean(出現数):Q',axis=alt.Axis(titleFontSize=18)),
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
st.title('チームのWell-being（計測ダッシュボード）')
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

