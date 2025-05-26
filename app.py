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
        # Místo CustomIcon použijeme běžnou ikonku pro test
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

    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None

    _, r2_col1, r2_col2, r2_col3, _ = st.columns([1, 4.5, 1, 6, 1])

    with r2_col1:
        st.markdown('## Legenda')
        st.markdown("- Modrá ikonka = objekt (hrad/zámek)")
        st.markdown("- Kliknutím zobrazíte podrobnosti")

    with r2_col3:
        level1_map_data = st_folium(m, height=520, width=600)

        # LADICÍ VÝPISY
        st.write("🪵 DEBUG: level1_map_data:", level1_map_data)

        clicked_id = level1_map_data.get('last_object_clicked_popup')
        st.write("🪵 DEBUG: Kliknuto na:", clicked_id)
        st.write("🪵 DEBUG: Předchozí v session_state:", st.session_state.selected_id)

        if clicked_id and clicked_id != st.session_state.selected_id:
            st.session_state.selected_id = clicked_id

        if st.session_state.selected_id:
            selected_row = df[df["ID"] == st.session_state.selected_id]
            if not selected_row.empty:
                row = selected_row.iloc[0]
                matched_info = df_info[df_info["name"] == row["ID"]]

                st.markdown("### 🏰 Informace o vybraném místě")
                st.markdown(f"**Název:** {row['ID']}")
                st.markdown(f"**Souřadnice:** {row['Latitude']:.4f}, {row['Longitude']:.4f}")

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
