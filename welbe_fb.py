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
url = 'http://127.0.0.1:5000/'

def main():
    r_fb = requests.get(url + '/get_fb', params={'user':name})
    r_fb_DB = r_fb.json()
    df_fb=pd.DataFrame.from_dict(r_fb_DB,orient='index').T

    st.subheader('週間 Well-beingスコア')
    line = alt.Chart(df_fb).mark_line(
        color='blue'
    ).encode(
        x=alt.X('date:T',axis=alt.Axis(format="%m月%d日",labelFontSize=14, ticks=False, titleFontSize=18,title='日付')),
        y=alt.Y('mean(my_happy):Q',axis=alt.Axis(titleFontSize=18, title='Well-beingスコア'))
    ).properties(
        width=650,
        height=400,
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

    st.write(points+line)

    df_emotion=pd.read_excel('welbe_emotion.xlsx')
    #df_emotion=pd.melt(df_emotion,id_vars=df_emotion.columns.values[:1],var_name="emotion",value_name="score")
    #df_emotion=pd.to_datetime(df_emotion['date'],format='%m月%d日')

    st.subheader('週間 感情スコア')
    line_bad = alt.Chart(df_emotion).mark_line(
        color='purple'
    ).encode(
        x=alt.X('date:T',axis=alt.Axis(format="%m月%d日",labelFontSize=14, ticks=False, titleFontSize=18,title='日付')),
        y=alt.Y('sum(Bad):Q',axis=alt.Axis(titleFontSize=18))
    ).properties(
        width=650,
        height=400,
        )

    line_good = alt.Chart(df_emotion).mark_line(
        color='red'
    ).encode(
        x=alt.X('date:T',axis=alt.Axis(format="%m月%d日",labelFontSize=14, ticks=False, titleFontSize=18,title='日付')),
        y=alt.Y('sum(Good):Q',axis=alt.Axis(titleFontSize=18, title='感情スコア'))
    ).properties(
        width=650,
        height=400,
        )

    line_surprise = alt.Chart(df_emotion).mark_line(
        color='green'
    ).encode(
        x=alt.X('date:T',axis=alt.Axis(format="%m月%d日",labelFontSize=14, ticks=False, titleFontSize=18,title='日付')),
        y=alt.Y('sum(Surprise):Q',axis=alt.Axis(titleFontSize=18))
    ).properties(
        width=650,
        height=400,
        )

    st.write(line_bad + line_good + line_surprise)


    df_gch=pd.read_excel('welbe_gch.xlsx')

    st.subheader('週間 愚痴スコア')
    line_gch = alt.Chart(df_gch).mark_line(
        color='olive'
    ).encode(
        x=alt.X('date:T',axis=alt.Axis(format="%m月%d日",labelFontSize=14, ticks=False, titleFontSize=18,title='日付')),
        y=alt.Y('mean(愚痴スコア):Q',axis=alt.Axis(titleFontSize=18, title='愚痴スコア'))
    ).properties(
        width=650,
        height=400,
        )

    points_gch = alt.Chart(df_gch).mark_circle(
        color='lightgreen'
    ).encode(
        x=alt.X('date:T'),
        y=alt.Y('愚痴スコア:Q'),
        size = 'count()'
    ).properties(
        width=650,
        height=400
        )

    st.write(points_gch+line_gch)


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

