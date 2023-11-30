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
url = st.secrets['URL']
query_params = st.experimental_get_query_params()
team_url=query_params['team'][0]

dic_team = {
    'A':'（大P）連続蒸留部門',
    'B':'（大P）中味部門',
    'C':'（大P）包装部門',
    'D':'（大P）間接部門',
    'E':'（梓P）中味部門',
    'F':'（梓P）包装部門',
    'Z':'開発用',
}


def main():
    st.write('チーム「' + dic_team[team_url] + '」の入力画面です')
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

        with st.expander("クリックで過去のあなたの日記入力状況を表示します"):
            r_diary = requests.get(url + '/get_diary', params={'user':name})
            r_diary_DB = r_diary.json()
            df_diary=pd.DataFrame.from_dict(r_diary_DB,orient='index')
            df_diary.columns=['日記の入力状況']
            df_diary = df_diary.sort_index(ascending=False)
            st.table(data=df_diary)
            
        with st.expander("クリックで日記の入力例を表示します"):
            st.caption('入力例1：今日仕事忙しすぎて朝しか食べてなくてさっき帰ってきたけど、こんな時間だし食べなくていっか。食べて太るよりは我慢して痩せた方が絶対いいし。いい方法ではないかもしれないけど痩せたい！')
            st.caption('入力例2：珍しく上司から褒められた。あんまり褒めるところ見たことがない上司だから嬉しいけどヘンな感じ（笑）。たまにこういうことがあると頑張ろうって気になります。')
            st.caption('入力例3：リモートワークの日だったけど、自分の空間でひたすら仕事できるっていうのは私には向いてる気がする。もう毎日リモートワークにしてほしい。')
            st.caption('入力例4：今日は忙しすぎて死んだなー。これからやっと事務仕事。忙しくさせてもらってることに感謝。だけどさすがに堪えてる。たまには癒しがほしいっす。')
            st.caption('入力例5：会社から帰る途中の場所にめちゃめちゃお気に入りのご飯屋さんを見つけた。なんてことない定食屋さんだけど、雰囲気含めて全部がツボ。そのうち誰か連れていきたい')
            st.caption('入力例6：旦那は気楽に1人で外出出来ていいなー。決して娘と一緒に居るのが嫌な訳じゃないけど…たまには1人で買い物行きたいなー')
            st.caption('入力例7：最近毎日雨降ってる気がする。洗濯物干せないとかはまだいいけど、何より傘持ったまま朝から満員電車に乗るのが辛すぎる。')

        diary_team = st.text_area(label='B：職場の所属チームについて感じたことをご記入ください（任意）',height=12)
        my_happy = st.selectbox("C：あなたは一日幸せでしたか？（0点: とても不幸／10点: とても幸せ）",options=happy_score)
        group_happy = st.selectbox('D：チーム全体としては，一日幸せだったと思いますか？（0点: とても不幸／10点: とても幸せ）',options=group_happy_score)
        real_communication = st.selectbox(
            'E：一日の中での、チームメンバーとの対面でのコミュニケーションの有無を教えて下さい（0点: 全くなかった／5点: 多くあった）',
            options=communication_score
            )
        online_communication = st.selectbox(
            'F：一日の中での、チームメンバーとのオンライン（WEBミーティング・電話・メールなど）でのコミュニケーションの有無を教えて下さい（0点: 全くなかった／5点: 多くあった）',
            options=communication_score
            )
        location = st.selectbox(
            'G：業務中，主に滞在した場所をお選び下さい',
            options=('選択して下さい','工場内の自フロア','自宅','得意先', 'その他')
            )
        location_other = st.text_input('H：Gでその他を選択した方は，差し支えない範囲で場所をご記入ください')

        submitted=st.form_submit_button('登録')
        st.markdown('#### 一度「登録」を押しても反応がない場合、再度クリックをお試し下さい。')
        st.markdown('#### 登録が問題なく行われた場合、ボタン押下後に風船が出てきた後、下部にグラフが表示されます。')
        
    if submitted:
        if name != 'demo':
            if len(str(my_happy)) > 3:
                my_happy = ''
            if len(str(group_happy)) > 3:
                group_happy = ''

            data_post = {
                        'user':name,
                        'contents':{
                        'day':str(day),
                        'diary':diary,
                        'diary_team':diary_team,
                        'my_happy':my_happy,
                        'group_happy':group_happy,
                        'communication_real':real_communication,
                        'communication_online':online_communication,
                        'location':location,
                        'location_other':location_other,
                        'timestamp':str(datetime.datetime.now()),
                        'team_url':team_url}
                        }

            post_result_return = requests.post(url + '/post',json=data_post)
            post_result = post_result_return.json()['response']
            
            if post_result == 'success':
                st.balloons()
                st.success('入力完了しました！')
            else:
                st.error('データ登録中にエラーが発生しました…。お問合せのメールアドレス宛にお声がけ頂けますと幸いです。')

            r_fb = requests.get(url + '/get_fb', params={'user':name, 'team_url':team_url})
            r_fb_DB = r_fb.json()
            df_fb=pd.DataFrame.from_dict(r_fb_DB,orient='index').T
            df_fb['date']=pd.to_datetime(df_fb['date'])

            day_list=[]
            for days in df_fb['date']:
                day_list.append(days + datetime.timedelta(hours=-9))

            df_fb['date'] = day_list
            df_fb_self=df_fb[df_fb['user']==name]

            st.subheader('週間Well-beingスコア')                
            ty = today.year
            tm = today.month
            td = today.day

            past_day= today-datetime.timedelta(days=6)
            past_y = past_day.year
            past_m = past_day.month
            past_d = past_day.day

            st.caption('水色の線：チームの平均スコア／水色の丸：チームの個別スコア／青色の丸：あなたのスコア')
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

            points_self = alt.Chart(df_fb_self).mark_circle(
                color='blue'
            ).encode(
                x=alt.X('date:T'),
                y=alt.Y('my_happy:Q'),
                size = 'count()'
            ).properties(
                width=650,
                height=400
                )

            layer = alt.layer(line,points,points_self
            ).configure_axis(
                grid=False
            )

            st.write(layer)

            feed = '''
            **▼アプリ改善のため、下記のリンクよりご意見・ご感想をお聞かせ下さい** 

            https://forms.gle/HKtfcQCnTzawbFYz5'''
            st.markdown(feed)

        else:
            st.balloons()
            df_fb=pd.read_excel('DB_demo.xlsx')
            df_fb['date']=pd.to_datetime(df_fb['date'])
            day_list=[]
            for days in df_fb['date']:
                day_list.append(days + datetime.timedelta(hours=-9))
            df_fb['date'] = day_list
            df_fb_self=df_fb[df_fb['user']==name]

            w = 800
            h = 400
            
            st.subheader('週間幸せスコア')                
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
                        axis=alt.Axis(titleFontSize=18, title='幸せスコア'),
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

            feed = '''
            **▼アプリ改善のため、ご意見があれば下記のリンクよりお聞かせ下さい** 

            https://forms.gle/HKtfcQCnTzawbFYz5'''
            st.markdown(feed)
              

# ユーザ情報
login_info = requests.get(url + '/check_login').json()
names = login_info['user']
usernames = login_info['username']
hashed_passwords = login_info['password']

message='''
    ※IDが正しいのにログインできない場合は、登録されていない可能性があるのでこちら（下記URL）から登録してください。登録には数日かかる場合があります。

    https://survey.ifohs.kyoto-u.ac.jp/kigyo/300.html'''

# cookie_expiry_daysでクッキーの有効期限を設定可能。
# 認証情報の保持期間を設定でき値を0とするとアクセス毎に認証を要求する
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=1)

# ログインメソッドで入力フォームを配置
st.title(':hatching_chick: 個と場のWell-being日記')
name, authentication_status, username = authenticator.login('Login', 'main')
st.caption("不具合等はこちらまでお願いします→sociocom-exp-contact[at]is.naist.jp")

detail_paper = '''
    **参加者の権利**\n
    &emsp;この研究への同意は、回答者の自由意思で決められるべきものです。調査は 回答者の同意が得られない限り行われることはありません。この調査を受けることに同意しなくても、なんら不利益を被ることはありません。また、調査終了後においても測定結果の破棄をご希望された場合には、ただちに破棄します(ただし、研究成果の公表後は破棄できません)。また、調査中において気分が悪くなった場合や中断したい場合には、ご自分の意志で測定の中断を希望することができます。その場合には、ただちに測定を中止します。\n
    **研究の目的**\n
    &emsp;本研究の目的は、職場における幸福感、やりがい、生きがいを支える組織の社会・文化的基盤を検証することです。その際、特に職場における動機づけ（個人達成志向と関係志向）が幸福感や生産性に与える影響についてのメカニズムを心理学の知見から解明し、実社会にフィードバックすることを目的とします。\n
    
    **研究の流れと所要時間、調査参加者が行うことについて**\n
    &emsp;今回設定された一定期間、一日の出来事を想起し、日記をご記入いただきます。また、ご自身やチーム全体が幸福を感じている度合いについて、感じたままに回答していただきます。\n
    
    &emsp;- 調査の回答はあなた自身の個別的・直接的な評価や能力査定に関わるものではありませんので、感じておられる通りのことを率直にお答えください。\n
    &emsp;- 本研究への参加は完全に個人の自由に基づくものです。参加しても、しなくても、なんら不利益を被ることはありません。また、参加していただける場合も、質問にはなるべくすべてご回答いただきたいとは思いますが、答えにくい質問や、答えたくない質問があれば飛ばしてもらってもかまいません。\n
    &emsp;- 回答時間は人により異なりますが、１日約５分程度かかります。
    
    **データの紐づけについて**\n
    &emsp;今回ご回答頂いたデータは、別機会にお答え頂いている「企業・組織風土と幸福度に関する調査」のアンケート調査データと統合して分析を致します。このことに同意されず、研究参加を途中撤回されても、研究参加者が不利益を被ることはありません。\n
    
    **プライバシーの保護について**\n
    &emsp;あなたのプライバシーは厳重に守られ、調査に関することであなたの名前が公表されることは決してありませんし、あなたの所属する会社や部署も個人のデータをお渡しすることは一切ありません。あなたの個人情報および測定結果は、京都大学人と社会の未来研究院内の、施錠された保管庫にて管理されます。また、調査後のデータ処理はセキュリティーを保ったコンピュータ環境の中で実施されます。\n
    &emsp;調査で取得した同意書・アンケート・データは採取したデータに関わる論文の公表後最低 10年間保管されます。10年を過ぎたものについては完全消去可能なソフトウェアを用いて消去するとともに、紙や DVDなどの媒体についてはシュレッダー処理などの物理的破壊によりデータの完全消去を行います。\n
    
    **参加御礼としての会社へのフィードバック**\n
    &emsp;ご参加人数が統計的に一定水準以上に達した場合には、ご協力会社様へのフィードバックを行います。その際には個人が特定されるような情報は廃され、会社全体の傾向から読み取れること、これからの職場環境のより一層の向上や強みに関するデータを提供いたします。\n
    
    **本研究に関する連絡先**\n
    ご質問や連絡事項、何らかのご意見がある場合は、下記にご連絡ください。\n
    \n
    研究責任者:\n
    内田&emsp;由紀子 (うちだ&emsp;ゆきこ)\n
    京都大学 人と社会の未来研究院・教授\n
    TEL: 075-753-9679\n
    E-mail: uchida.yukiko.6m[at]kyoto-u.ac.jp\n
    '''


# 返り値、authenticaton_statusの状態で処理を場合分け
if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write('Welcome *%s*' % (name))
    check_cons = requests.get(url + '/check_cons',params={'name':username}).json()
    if check_cons['consent']==1:
        main()
    else:
        st.info('初回ログインの前に、下記内容をご確認下さい')
        st.subheader('調査参加への同意について')
        st.markdown('私は、「企業・組織風土と幸福度に関する調査」について、' +
                    '下記事項を確認の上、調査に参加することに同意します。' +
                    '同意した場合に、調査の回答を実施します。'+
                    '(この文章は同意後は表示されません)')

        with st.expander('こちらをクリックすると調査説明書が表示されます'):
            st.subheader('企業・組織風土と幸福度に関する調査へのご参加について')
            st.markdown(detail_paper)

        with st.form('cons_form'):
            cons1 = st.checkbox('調査の目的、期間、方法等の内容。')
            st.markdown('''
                &emsp;&emsp;- 調査目的: 従業員の幸福感やモチベーション、メンタルヘルスや組織のパフォーマンスの向上\n
                &emsp;&emsp;- 期間: 2023年12月～2024年1月（期間延長の可能性あり）\n
                &emsp;&emsp;- 方法: WEB上の日記記入ページにアクセスして回答\n
                ''')
            cons2 = st.checkbox('この調査から得られた測定結果が当該学術研究の目的に利用されること。')
            cons3 = st.checkbox('参加者自らの自由意志により自発的に調査に参加すること。')
            cons4 = st.checkbox('今回回答する日記データは、既に回答した「企業・組織風土と幸福度に関する調査」のアンケートデータが統合されて分析されること。')
            cons5 = st.checkbox('参加者は、調査への参加に同意した場合でも、いつでも調査への参加を取り止めることができ、それにより何ら不利益を被らないこと。')
            cons6 = st.checkbox('回答データはすべて匿名化され、個人を特定できる状態で会社に結果がフィードバックされることはないこと。')

            consent = st.form_submit_button('同意します')
        if consent == True:
            if cons1 and cons2 and cons3 and cons4 and cons5 and cons6:
                requests.post(url + '/post_cons',params={'name':username})
                st.info('同意を確認しました')
                main()
            else:
                st.error('全てのチェックボックスをチェック後、ボタンを押して下さい')

elif authentication_status == False:
    st.error('UsernameまたはPasswordが間違っています（英数字・記号は半角にして下さい）')
    st.error('※初期パスワードはUsername（ID）と同様です')
    st.info(message)
elif authentication_status == None:
    st.warning('UsernameとPasswordをご入力下さい')
    st.info(message)
