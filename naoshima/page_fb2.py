import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import plugins
from geopy.distance import geodesic

def main():
    st.title('直島とっておきMAP')
    st.text('みなさまの「とっておきの推し場所」をマッピングしています。クリックしてコメントを見てみましょう')

    # 地図の中心となる座標
    latitude = 34.454573
    longitude = 133.989435

    # 地図を作成
    m = folium.Map(location=[latitude, longitude], zoom_start=14)
    
    df = pd.read_csv('./line_chat_history.csv')
    marker_info = []

    for idx, row in df.iterrows():
        if row['latitude'] == 'lati':
            continue
        lati = float(row['latitude'])
        longi = float(row['longitude'])
        timestamp = row['timestamp']
        comment = row['comment']
        tpl = (lati, longi, timestamp, comment)
        marker_info.append(tpl)

    # 地図をフルスクリーンに切り替えボタン設置
    plugins.Fullscreen(
        position="topright",
        title="拡大する",
        title_cancel="元に戻す",
        force_separate_button=True,
    ).add_to(m)

    # ピンを地図に追加
    for lat, lon, _, popup_text in marker_info:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 地図を表示
    st_data = st_folium(m, width=700, height=500)

    # コメントの表を表示するための場所を予約
    if st_data and st_data["last_object_clicked"]:
        clicked_lat = st_data["last_object_clicked"]["lat"]
        clicked_lon = st_data["last_object_clicked"]["lng"]
        
        # クリックされたピンの近くにあるコメントを表示
        nearby_comments = []
        for lat2, lon2, timestamp, comment in marker_info:
            if geodesic((clicked_lat, clicked_lon), (lat2, lon2)).meters < 500:  # 500m以内
                nearby_comments.append({'Timestamp': timestamp, 'Comment': comment})

        st.markdown("### 近くのコメント")
        if nearby_comments:
            # 表形式で表示
            nearby_comments_df = pd.DataFrame(nearby_comments)
            st.dataframe(nearby_comments_df)
        else:
            st.markdown("### 近くにコメントはありません")

if __name__ == '__main__':
    main()
