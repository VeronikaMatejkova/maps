import folium
import geopandas
import pandas as pd
import streamlit as st
from shapely.geometry import Point
from streamlit_folium import st_folium


def init_map(center=[50.1087456, 14.4403392], zoom_start=10, map_type="OpenStreetMap"):
    return folium.Map(location=center, zoom_start=zoom_start, tiles=map_type)

def create_point_map(df):
    # Cleaning
    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    # Convert PandasDataFrame to GeoDataFrame
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
        df = pd.read_csv(GITHUB_CSV_URL, sep=";")

        df.columns = [col.strip().lower() for col in df.columns]
        df = df.rename(columns={
            'name': 'ID',
            'clean_type': 'Type',
            'location_lat': 'Latitude',
            'location_lng': 'Longitude'
        })

        df['ID'] = df['ID'].str.strip()
        df['Type'] = df['Type'].str.strip()

        def map_icon_id(typ):
            typ = typ.lower()
            if 'hrad' in typ and 'zámek' in typ:
                return 2
            elif 'hrad' in typ:
                return 0
            elif 'zámek' in typ:
                return 1
            else:
                return None

        df['Icon_ID'] = df['Type'].apply(map_icon_id)
        df['Latitude'] = df['Latitude'].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)
        df['Longitude'] = df['Longitude'].astype(str).str.replace(" ", "").str.replace(",", ".").astype(float)
        df['Icon_Size'] = 50
        df['Opacity'] = 1.0

        return df[['ID', 'Icon_ID', 'Icon_Size', 'Opacity', 'Latitude', 'Longitude']]

    except Exception as e:
        raise FileNotFoundError(f"Chyba při načítání CSV z GitHubu: {e}")

FACT_BACKGROUND = """
                    <div style="width: 100%;">
                        <div style="
                                    background-color: #ECECEC;
                                    border: 1px solid #ECECEC;
                                    padding: 1.5% 1% 1.5% 3.5%;
                                    border-radius: 10px;
                                    width: 100%;
                                    color: white;
                                    white-space: nowrap;
                                    ">
                          <p style="font-size:20px; color: black;">{}</p>
                          <p style="font-size:33px; line-height: 0.5; text-indent: 10px;""><img src="{}" alt="Example Image" style="vertical-align: middle;  width:{}px;">  {} &emsp; &emsp; </p>
                        </div>
                    </div>
                    """

TITLE = 'Hrady a zámky ČR'

IM_CONSTANTS = {0:'https://ibb.co/PvNv1CjL', 
                1:'https://ibb.co/mVmTt85Y',
                2:'https://ibb.co/JFcvFc4n'}


@st.cache_resource  # @st.cache_data
def load_map():
    # Load the map
    m = init_map()  # init
    df = load_df()  # load data
    m = plot_from_df(df, m)  # plot points
    return m


def main():
    # format page
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

    # load map data @st.cache_resource
    m = load_map()
    # init stored values
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = None

    # setting up the header with its own row
    _, r1_col1, r1_col2, r1_col3, _ = st.columns([1, 4.5, 1, 6, 1])
    with r1_col1:
        st.markdown(f"<p style='font-size: 27px;'><i>Interactive Mapping Demonstration</i></p>",
                    unsafe_allow_html=True)
    with r1_col3:
        st.write('')

    # main information line: includes map location
    _, r2_col1, r2_col2, r2_col3, _ = st.columns([1, 4.5, 1, 6, 1])
    with r2_col1:
        # info sidebar
        r2_col1.markdown('## Arcane Optimization of Potassium Intake')
        text1, text2 = "Monkey's Tracked", " XX Active Monkey"
        st.markdown(FACT_BACKGROUND.format(text1, IM_CONSTANTS[0], 24, text2), unsafe_allow_html=True)
        st.markdown("""<div style="padding-top: 15px"></div>""", unsafe_allow_html=True)
        text1, text2 = "Banana Locations", " YY Outstanding Bananas"
        st.markdown(FACT_BACKGROUND.format(text1, IM_CONSTANTS[1], 30, text2), unsafe_allow_html=True)

        # white space
        for _ in range(10):
            st.markdown("")

        # place for logos
        logo1, logo2, _ = st.columns([1, 1, 2])
        #logo1.image(IM_CONSTANTS['LOGO'], width=110)

    # white space
    with r2_col2:
        st.write("")

    # map container
    with r2_col3:
        level1_map_data = st_folium(m, height=520, width=600)
        st.session_state.selected_id = level1_map_data['last_object_clicked_tooltip']

        if st.session_state.selected_id is not None:
            selected_icon_id = df[df["ID"] == st.session_state.selected_id]["Icon_ID"].values[0]
            st.write(f'You Have Selected: {st.session_state.selected_id}')
            st.image(IM_CONSTANTS[selected_icon_id], width=110)


if __name__ == "__main__":
    main()


