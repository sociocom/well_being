# -*- coding: utf-8 -*-

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


happy_score = ['選択して下さい（0〜10点）',0,1,2,3,4,5,6,7,8,9,10]
today = datetime.date.today()
day_list=[]
diary_list=[]

def main():
    day = st.date_input('対象の日付を入力して下さい',today)
    diary = st.text_area(label='A：3行程度で日記をご記入ください（仕事に無関係でも構いません）',height=12)
    with st.expander("クリックで日記の入力例を表示します"):
        st.caption('入力例1：今日仕事忙しすぎて朝しか食べてなくてさっき帰ってきたけど、こんな時間だし食べなくていっか。食べて太るよりは我慢して痩せた方が絶対いいし。いい方法ではないかもしれないけど痩せたい！')
        st.caption('入力例2：珍しく上司から褒められた。あんまり褒めるところ見たことがない上司だから嬉しいけどヘンな感じ（笑）。たまにこういうことがあると頑張ろうって気になります。')
        st.caption('入力例3：リモートワークの日だったけど、自分の空間でひたすら仕事できるっていうのは私には向いてる気がする。もう毎日リモートワークにしてほしい。')
        st.caption('入力例4：今日は忙しすぎて死んだなー。これからやっと事務仕事。忙しくさせてもらってることに感謝。だけどさすがに堪えてる。たまには癒しがほしいっす。')
        st.caption('入力例5：会社から帰る途中の場所にめちゃめちゃお気に入りのご飯屋さんを見つけた。なんてことない定食屋さんだけど、雰囲気含めて全部がツボ。そのうち誰か連れていきたい')
        st.caption('入力例6：旦那は気楽に1人で外出出来ていいなー。決して娘と一緒に居るのが嫌な訳じゃないけど…たまには1人で買い物行きたいなー')
        st.caption('入力例7：最近毎日雨降ってる気がする。洗濯物干せないとかはまだいいけど、何より傘持ったまま朝から満員電車に乗るのが辛すぎる。')

    #my_happy = st.radio("B：あなたは今日一日幸せでしたか？（0点:とても不幸／10点：とても幸せ）",options=happy_score,horizontal=True)
    my_happy = st.selectbox("B：あなたは今日一日幸せでしたか？（0点:とても不幸／10点：とても幸せ）",options=happy_score)
    group_happy = st.selectbox('C：チーム全体としては，今日一日幸せだったと思いますか？（0点:とても不幸／10点：とても幸せ）',options=happy_score)
    location = st.selectbox(
        'D：業務中，主に滞在した場所をお選び下さい',
        options=('選択して下さい','関西支社','自宅','得意先','協力会社（制作会社など）','媒体社','出張先（撮影現場、編集スタジオ等）', 'その他')
        )
    location_other = st.text_input('E：Dでその他を選択した方は，差し支えない範囲で場所をご記入ください')

    if st.button('登録') == True:
        data_post = {
                    'user':name,
                    'contents':{
                    'day':str(day),
                    'diary':diary,
                    'my_happy':my_happy,
                    'group_happy':group_happy,
                    'location':location,
                    'location_other':location_other,
                    'timestamp':str(datetime.datetime.now())}
                    }
    
        url = 'http://aoi.naist.jp/wellbeing'
        requests.post(url + '/post',json=data_post)
        st.write('入力完了しました！')

        r_diary = requests.get(url + '/get_diary', params={'user':name})
        r_diary_DB = r_diary.json()
        df_diary=pd.DataFrame.from_dict(r_diary_DB,orient='index')
        df_diary.columns=['日記テキスト']
        df_diary = df_diary.sort_index(ascending=False)

        with st.expander("クリックであなたの過去の日記を表示します"):
            st.table(data=df_diary)

        r_fb = requests.get(url + '/get_fb', params={'user':name})
        r_fb_DB = r_fb.json()
        df_fb=pd.DataFrame.from_dict(r_fb_DB,orient='index').T

        st.subheader('週間Well-beingスコア')
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

        
# ユーザ情報。引数
names = ['admin','001','002','003','004','005'] 
usernames = ['admin','001','002','003','004','005']  # 入力フォームに入力された値と合致するか確認される
passwords = ['admin','001','002','003','004','005']  # 入力フォームに入力された値と合致するか確認される

# パスワードをハッシュ化。 リスト等、イテラブルなオブジェクトである必要がある
hashed_passwords = stauth.Hasher(passwords).generate()

# cookie_expiry_daysでクッキーの有効期限を設定可能。
#認証情報の保持期間を設定でき値を0とするとアクセス毎に認証を要求する
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)

# ログインメソッドで入力フォームを配置
st.title('個と場のWell-being日記')
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
