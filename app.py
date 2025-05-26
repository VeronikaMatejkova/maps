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
    for _, row in df.iterrows():
        icon = folium.features.CustomIcon(IM_CONSTANTS[row.Icon_ID], icon_size=(row.Icon_Size, row.Icon_Size))
        folium.Marker(
            [row.Latitude, row.Longitude],
            tooltip=row.ID,  # Tooltip = ID
            opacity=row.Opacity,
            icon=icon
        ).add_to(folium_map)
    return folium_map

def load_df():
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/VeronikaMatejkova/maps/main/DataProApp.csv"
    df = pd.read_csv(GITHUB_CSV_URL)
    required_cols = ['ID', 'Icon_ID', 'Icon_Size', 'Opacity', 'Latitude', 'Longitude']
    df = df.dropna(subset=['ID', 'Icon_ID', 'Latitude', 'Longitude'])
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Icon_ID'] = df['Icon_ID'].astype(float).fillna(99).astype(int)
    df['Icon_Size'] = df['Icon_Size'].astype(float).fillna(50).astype(int)
    df['Opacity'] = df['Opacity'].astype(float).fillna(1.0)
    df['Latitude'] = df['Latitude'].astype(str).str.replace(",", ".").astype(float)
    df['Longitude'] = df['Longitude'].astype(str).str.replace(",", ".").astype(float)
    return df[required_cols]

@st.cache_data
def load_extra_info():
    INFO_CSV_URL = "https://raw.githubusercontent.com/VeronikaMatejkova/maps/main/Zakladni_info.csv"
    df_info = pd.read_csv(INFO_CSV_URL, sep=";", encoding="utf-8")
    df_info["name"] = df_info["name"].astype(str).str.strip()
    return df_info

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
    df["name"] = df["ID"]  # Předpokládáme, že ID obsahuje jméno objektu
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

    m, df = load_map()
    df_info = load_extra_info()

    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None

    _, r2_col1, r2_col2, r2_col3, _ = st.columns([1, 4.5, 1, 6, 1])

    with r2_col1:
        st.markdown('## Legenda k ikonám')
        st.markdown(FACT_BACKGROUND.format("Hrady", IM_CONSTANTS[0], 24, "Ikona 0"), unsafe_allow_html=True)
        st.markdown("""<div style="padding-top: 15px"></div>""", unsafe_allow_html=True)
        st.markdown(FACT_BACKGROUND.format("Zámky", IM_CONSTANTS[1], 30, "Ikona 1"), unsafe_allow_html=True)

    with r2_col3:
        level1_map_data = st_folium(m, height=520, width=600)

        clicked_id = level1_map_data.get('last_object_clicked_tooltip')
        if clicked_id and clicked_id != st.session_state.selected_id:
            st.session_state.selected_id = clicked_id

        if st.session_state.selected_id is not None:
            selected_row = df[df["ID"] == st.session_state.selected_id]
            if not selected_row.empty:
                row = selected_row.iloc[0]
                icon_id = row["Icon_ID"]
                matched_info = df_info[df_info["name"] == row["ID"]]
        
                st.markdown("### 🏰 Informace o vybraném místě")
                st.markdown(FACT_BACKGROUND.format(
                    row["ID"],
                    IM_CONSTANTS[icon_id],
                    40,
                    f"Souřadnice: {row['Latitude']:.4f}, {row['Longitude']:.4f}"
                ), unsafe_allow_html=True)
        
                if not matched_info.empty:
                    info = matched_info.iloc[0]
                    st.markdown(f"**Bezbariérovost:** {info['clean_accessibilityNote']}")
                    st.markdown(f"**Zvířata:** {info['clean_animalsNote']}")
                    st.markdown(f"**Cyklisté:** {info['clean_cyclistsNote']}")
                    st.markdown(f"**Děti:** {info['clean_forKidsNote']}")
                else:
                    st.info("Žádné doplňkové informace nenalezeny.")
            else:
                st.warning("Vybraný bod nebyl nalezen v datech.")

if __name__ == "__main__":
    main()
