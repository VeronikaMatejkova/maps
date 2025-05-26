import folium
import geopandas
import pandas as pd
import streamlit as st
from shapely.geometry import Point
from streamlit_folium import st_folium

def init_map(center=[50.1087456, 14.4403392], zoom_start=10, map_type="OpenStreetMap"):
    return folium.Map(location=center, zoom_start=zoom_start, tiles=map_type)

def create_point_map(df):
    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    df['coordinates'] = df[['Latitude', 'Longitude']].values.tolist()
    df['coordinates'] = df['coordinates'].apply(Point)
    df = geopandas.GeoDataFrame(df, geometry='coordinates')
    df = df.dropna(subset=['Latitude', 'Longitude', 'coordinates'])
    return df

def plot_from_df(df, folium_map):
    df = create_point_map(df)
    for i, row in df.iterrows():
        icon = folium.features.CustomIcon(IM_CONSTANTS[row.Icon_ID], icon_size=(row.Icon_Size, row.Icon_Size))
        folium.Marker([row.Latitude, row.Longitude],
                      tooltip=f'{row.ID}',
                      opacity=row.Opacity,
                      icon=icon).add_to(folium_map)
    return folium_map

def load_df():
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/VeronikaMatejkova/maps/main/DataProApp.csv"
    try:
        df = pd.read_csv(GITHUB_CSV_URL)
        required_cols = ['ID', 'Icon_ID', 'Icon_Size', 'Opacity', 'Latitude', 'Longitude']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV soubor neobsahuje požadované sloupce: {required_cols}")
        df = df.dropna(subset=['ID', 'Icon_ID', 'Latitude', 'Longitude'])
        df['ID'] = df['ID'].astype(str).str.strip()
        df['Icon_ID'] = df['Icon_ID'].astype(float).fillna(99).astype(int)
        df['Icon_Size'] = df['Icon_Size'].astype(float).fillna(50).astype(int)
        df['Opacity'] = df['Opacity'].astype(float).fillna(1.0)
        df['Latitude'] = df['Latitude'].astype(str).str.replace(",", ".").astype(float)
        df['Longitude'] = df['Longitude'].astype(str).str.replace(",", ".").astype(float)
        return df[required_cols]
    except Exception as e:
        raise FileNotFoundError(f"Chyba při načítání CSV z GitHubu: {e}")

FACT_BACKGROUND = """
<div style="width: 100%;">
    <div style="background-color: #ECECEC; border: 1px solid #ECECEC; padding: 1.5% 1% 1.5% 3.5%; border-radius: 10px; width: 100%; color: white; white-space: nowrap;">
        <p style="font-size:20px; color: black;">{}</p>
        <p style="font-size:33px; line-height: 0.5; text-indent: 10px;"><img src="{}" alt="Example Image" style="vertical-align: middle; width:{}px;">  {} &emsp; &emsp;</p>
    </div>
</div>
"""

TITLE = 'Hrady a zámky ČR'

IM_CONSTANTS = {
    0: 'https://i.ibb.co/cS1S2T3B/Icon-hrad.png',
    1: 'https://i.ibb.co/tTSKcXpN/Icon-zamek.png',
    2: 'https://i.ibb.co/rfQxfQSk/Icon-hrad-a-zamek.png'
}

@st.cache_resource
def load_map():
    df = load_df()
    m = init_map()
    m = plot_from_df(df, m)
    return m, df

def main():
    st.set_page_config(TITLE, page_icon=None, layout='wide')
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 15rem;
                padding-right: 15rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title(TITLE)

    # načti mapu a data
    m, df = load_map()

    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None

    _, r1_col1, r1_col2, r1_col3, _ = st.columns([1, 4.5, 1, 6, 1])
    with r1_col1:
        st.markdown(f"<p style='font-size: 27px;'><i>Interactive Mapping Demonstration</i></p>", unsafe_allow_html=True)
    with r1_col3:
        st.write('')

    _, r2_col1, r2_col2, r2_col3, _ = st.columns([1, 4.5, 1, 6, 1])
    with r2_col1:
        st.markdown('## Arcane Optimization of Potassium Intake')
        st.markdown(FACT_BACKGROUND.format("Monkey's Tracked", IM_CONSTANTS[0], 24, "XX Active Monkey"), unsafe_allow_html=True)
        st.markdown("""<div style="padding-top: 15px"></div>""", unsafe_allow_html=True)
        st.markdown(FACT_BACKGROUND.format("Banana Locations", IM_CONSTANTS[1], 30, "YY Outstanding Bananas"), unsafe_allow_html=True)
        for _ in range(10):
            st.markdown("")

    with r2_col2:
        st.write("")

    with r2_col3:
        level1_map_data = st_folium(m, height=520, width=600)
        if level1_map_data and level1_map_data.get('last_object_clicked_tooltip'):
            st.session_state.selected_id = level1_map_data['last_object_clicked_tooltip']

        if st.session_state.selected_id is not None:
            try:
                selected_icon_id = df[df["ID"] == st.session_state.selected_id]["Icon_ID"].values[0]
                st.write(f'You Have Selected: {st.session_state.selected_id}')
                st.image(IM_CONSTANTS[selected_icon_id], width=110)
            except Exception as e:
                st.warning(f"Nepodařilo se najít vybraný záznam: {e}")

if __name__ == "__main__":
    main()
