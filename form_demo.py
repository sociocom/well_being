# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import altair as alt
import datetime
import plotly.figure_factory as ff
import plotly.express as px
import requests
import json
import streamlit_authenticator as stauth
import bcrypt
import mojimoji
import pytz


happy_score = ['選択して下さい（0〜10点）',0,1,2,3,4,5,6,7,8,9,10]
group_happy_score = ['選択して下さい（0〜10点）',0,1,2,3,4,5,6,7,8,9,10,'全くわからない']
communication_score = ['選択して下さい（0〜5点）',0,1,2,3,4,5]
today = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
day_list=[]
diary_list=[]
url = 'http://well-being.naist.jp/demo'
team_url='Z'


def main():
    
    with st.expander('パスワード変更はこちら'):
        new_pass = st.text_input(label='↓新しいパスワードをご入力下さい')
        new_pass_hash = bcrypt.hashpw(new_pass.encode(),bcrypt.gensalt()).decode()
        if st.button('パスワード変更') ==True:
            if name == 'demo':
                st.write('demoはパスワード変更できません…')
            else:
                requests.post(
                    url + '/chenge_pass',
                    params={
                        'name':name,
                        'pass':new_pass_hash
                        })
                st.write('パスワードを変更しました！')
    with st.form('my_form'):
        day = st.date_input('対象の日付を入力して下さい',today)
        diary = st.text_area(label='A：3行程度で日記をご記入ください（仕事に無関係でも構いません）',height=12)
        
        df_diary=pd.read_excel('data_dammy.xlsx')
        #df_diary = df_diary.sort_index(ascending=False)

        with st.expander("クリックであなたの過去の日記を表示します"):
            st.write('※同日に複数の入力があった場合、初回の入力分のみが表示されます')
            st.table(data=df_diary)
        
        with st.expander("クリックで日記の入力例を表示します"):
            st.caption('入力例1：今日仕事忙しすぎて朝しか食べてなくてさっき帰ってきたけど、こんな時間だし食べなくていっか。食べて太るよりは我慢して痩せた方が絶対いいし。いい方法ではないかもしれないけど痩せたい！')
            st.caption('入力例2：珍しく上司から褒められた。あんまり褒めるところ見たことがない上司だから嬉しいけどヘンな感じ（笑）。たまにこういうことがあると頑張ろうって気になります。')
            st.caption('入力例3：リモートワークの日だったけど、自分の空間でひたすら仕事できるっていうのは私には向いてる気がする。もう毎日リモートワークにしてほしい。')
            st.caption('入力例4：今日は忙しすぎて死んだなー。これからやっと事務仕事。忙しくさせてもらってることに感謝。だけどさすがに堪えてる。たまには癒しがほしいっす。')
            st.caption('入力例5：会社から帰る途中の場所にめちゃめちゃお気に入りのご飯屋さんを見つけた。なんてことない定食屋さんだけど、雰囲気含めて全部がツボ。そのうち誰か連れていきたい')
            st.caption('入力例6：旦那は気楽に1人で外出出来ていいなー。決して娘と一緒に居るのが嫌な訳じゃないけど…たまには1人で買い物行きたいなー')
            st.caption('入力例7：最近毎日雨降ってる気がする。洗濯物干せないとかはまだいいけど、何より傘持ったまま朝から満員電車に乗るのが辛すぎる。')

        diary = st.text_area(label='B：職場の所属チームについて感じたことをご記入ください（任意）',height=12)

        #my_happy = st.radio("B：あなたは今日一日幸せでしたか？（0点:とても不幸／10点：とても幸せ）",options=happy_score,horizontal=True)
        my_happy = st.selectbox("C：あなたは一日幸せでしたか？（0点: とても不幸／10点: とても幸せ）",options=happy_score)
        group_happy = st.selectbox('D：チーム全体としては，一日幸せだったと思いますか？（0点: とても不幸／10点: とても幸せ）',options=group_happy_score)
        real_communication = st.selectbox(
            'E：一日の中での、チームメンバーとの対面でのコミュニケーションの有無を教えて下さい（0点: 全くなかった／5点: 多くあった）',
            options=communication_score
            )
        online_communication = st.selectbox(
            'F：一日の中での、チームメンバーとのオンライン（WEBミーティング・電話など）でのコミュニケーションの有無を教えて下さい（0点: 全くなかった／5点: 多くあった）',
            options=communication_score
            )
        location = st.selectbox(
            'G：業務中，主に滞在した場所をお選び下さい',
            options=('選択して下さい','社内の自フロア','自宅','得意先', 'その他')
            )
        location_other = st.text_input('H：Gでその他を選択した方は，差し支えない範囲で場所をご記入ください')

        submitted=st.form_submit_button('登録')
        
        w = 600
        h = 350
        if submitted == True:
            st.balloons()
            
            st.write(datetime.datetime.now())
            df_fb=pd.read_excel('DB_demo.xlsx')
            df_fb=df_fb.sort_values('date')
            df_fb['date']=pd.to_datetime(df_fb['date'])
            df_fb_self=df_fb[df_fb['user']==name]

            st.subheader('週間Well-beingスコア')                
            st.caption('水色の線：チームの平均スコア／水色の丸：チームの個別スコア／青色の丸：あなたのスコア')
            st.caption('※水色の丸の大きさはスコアごとの人数を表しています')
            line = alt.Chart(df_fb).mark_line(
                color='lightskyblue'
            ).encode(
                x=alt.X('date:T',
                        axis=alt.Axis(format="%m/%d",labelFontSize=14, titleFontSize=18,title='日付'),
                        scale=alt.Scale(domainMax={"year": 2023, "month": 5, "date": 16},
                                        domainMin={"year": 2023, "month": 5, "date": 9})
                        ),
                y=alt.Y('mean(my_happy):Q',
                        axis=alt.Axis(titleFontSize=18, title='Well-beingスコア'),
                        scale=alt.Scale(domainMax=10,domainMin=0)
                       )
            ).properties(
                width=w,
                height=h
                )

            points = alt.Chart(df_fb).mark_circle(
                color='lightskyblue'
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('my_happy:Q'),
                size = 'count()'
            ).properties(
                width=w,
                height=h
                )

            points_self = alt.Chart(df_fb_self).mark_circle(
                color='blue'
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('my_happy:Q'),
                size = 'count()'
            ).properties(
                width=w,
                height=h
                )

            layer = alt.layer(line,points,points_self
            ).configure_axis(
                grid=False
            )

            st.write(layer)
              

# ユーザ情報
#login_info = requests.get(url + '/check_login').json()
#print(login_info)
#names = login_info['user']
#usernames = login_info['username']
#hashed_passwords = login_info['password']


# cookie_expiry_daysでクッキーの有効期限を設定可能。
# 認証情報の保持期間を設定でき値を0とするとアクセス毎に認証を要求する
#authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#    'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)

# ログインメソッドで入力フォームを配置
st.title(':balloon:個と場のWell-being日記')
name= "demo"
username = "demo"
main()

# 返り値、authenticaton_statusの状態で処理を場合分け
#if authentication_status:
#    authenticator.logout('Logout', 'main')
#    st.write('Welcome *%s*' % (name))
#    main()
#elif authentication_status == False:
#    st.error('UsernameまたはPasswordが間違っています（英数字・記号は半角にして下さい）')
#elif authentication_status == None:
#    st.warning('UsernameとPasswordをご入力下さい')
