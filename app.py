import folium
import geopandas
import pandas as pd
import streamlit as st
from shapely.geometry import Point
from streamlit_folium import st_folium

def init_map(center=[50.1087456, 14.4403392], zoom_start=7, map_type="OpenStreetMap"):
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
        icon = folium.Icon(color="blue", icon="info-sign")
        popup = folium.Popup(row.ID, parse_html=True)
        folium.Marker(
            [row.Latitude, row.Longitude],
            popup=popup,
            icon=icon,
            opacity=row.Opacity
        ).add_to(folium_map)
    return folium_map

def load_df():
    GITHUB_CSV_URL = "https://raw.githubusercontent.com/VeronikaMatejkova/maps/main/DataProApp.csv"
    df = pd.read_csv(GITHUB_CSV_URL)
    df = df.dropna(subset=['ID', 'Icon_ID', 'Latitude', 'Longitude'])
    df['ID'] = df['ID'].astype(str).str.strip()
    df['Icon_ID'] = df['Icon_ID'].astype(float).fillna(99).astype(int)
    df['Icon_Size'] = df['Icon_Size'].astype(float).fillna(50).astype(int)
    df['Opacity'] = df['Opacity'].astype(float).fillna(1.0)
    df['Latitude'] = df['Latitude'].astype(str).str.replace(",", ".").astype(float)
    df['Longitude'] = df['Longitude'].astype(str).str.replace(",", ".").astype(float)
    return df

@st.cache_data
def load_extra_info():
    INFO_CSV_URL = "https://raw.githubusercontent.com/VeronikaMatejkova/maps/main/Zakladni_info.csv"
    df_info = pd.read_csv(INFO_CSV_URL, sep=";", encoding="utf-8")
    df_info["name"] = df_info["name"].astype(str).str.strip()
    return df_info

TITLE = 'Hrady a zámky ČR'

@st.cache_resource
def load_map():
    df = load_df()
    m = init_map()
    m = plot_from_df(df, m)
    return m, df

def main():
    st.set_page_config(TITLE, page_icon=None, layout='wide')
    st.title(TITLE)

    m, df = load_map()
    df_info = load_extra_info()

    # výběr objektu
    all_ids = df["ID"].unique().tolist()
    selected_id = st.selectbox("Vyber hrad nebo zámek:", all_ids)

    _, col1, col2, _ = st.columns([0.5, 4, 6, 0.5])

    with col1:
        st.markdown('## Legenda')
        st.markdown("- Modrá ikonka = objekt na mapě")
        st.markdown("- Výběr objektu z dropdownu zobrazí podrobnosti")

    with col2:
        st_folium(m, height=520, width=700)

    # zobrazení detailních informací
    st.markdown("---")
    st.markdown("### 🏰 Informace o vybraném místě")

    selected_row = df[df["ID"] == selected_id].iloc[0]
    matched_info = df_info[df_info["name"] == selected_id]

    st.markdown(f"**Název:** {selected_row['ID']}")
    st.markdown(f"**Souřadnice:** {selected_row['Latitude']:.4f}, {selected_row['Longitude']:.4f}")

    if not matched_info.empty:
        info = matched_info.iloc[0]
        st.markdown(f"**Bezbariérovost:** {info['clean_accessibilityNote']}")
        st.markdown(f"**Zvířata:** {info['clean_animalsNote']}")
        st.markdown(f"**Cyklisté:** {info['clean_cyclistsNote']}")
        st.markdown(f"**Děti:** {info['clean_forKidsNote']}")
    else:
        st.info("Žádné doplňkové informace nenalezeny.")

if __name__ == "__main__":
    main()
