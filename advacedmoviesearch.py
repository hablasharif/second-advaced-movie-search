import streamlit as st
import pandas as pd
from imdb import IMDb
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import random
import base64
from datetime import datetime

# Internal sound function
def play_internal_sound():
    # You can customize the sound frequency (Hz) and duration (milliseconds)
    winsound.Beep(frequency=1000, duration=1000)

# Function to search movie on IMDb
def search_movie_imdb(movie_name, release_year):
    ia = IMDb()
    movies = ia.search_movie(movie_name)
    filtered_movies = [movie for movie in movies if "year" in movie and movie["year"] == release_year]
    if filtered_movies:
        movie = filtered_movies[0]
        imdb_id = movie.getID()
        return imdb_id
    else:
        return None

# Function to generate IMDb hyperlink
def generate_imdb_hyperlink(imdb_id):
    if imdb_id:
        return f"https://www.imdb.com/title/tt{imdb_id}"
    else:
        return None

# Function to generate URLs with IMDb IDs
def generate_urls_with_imdb_ids(imdb_id):
    urls = {
        "vidsrc.to": f"https://vidsrc.to/embed/movie/tt{imdb_id}",
        "vidsrc.me": f"https://vidsrc.me/embed/tt{imdb_id}",
        "smashystream.com": f"https://embed.smashystream.com/playere.php?imdb=tt{imdb_id}",
        "2embed.me": f"https://2embed.me/movie/tt{imdb_id}",
        "2embed.cc": f"https://www.2embed.cc/embed/tt{imdb_id}",
        "databasegdriveplayer.xyz": f"https://databasegdriveplayer.xyz/player.php?imdb=tt{imdb_id}"
    }
    return urls

# Function to get title from IMDb URL
def get_title_from_imdb_url(url, execute):
    try:
        if execute:
            user_agent = random.choice(user_agents)
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title').text
            return title
        else:
            return "Not Executed"
    except Exception as e:
        return "Not Found"

# Function to create a download link for CSV
def create_download_link_csv(df, title="Download CSV", filename_prefix="data"):
    now = datetime.now()
    timestamp = now.strftime("%d %B, %A %Y, %I:%M %p")
    filename = f"{filename_prefix}_{timestamp}.csv"
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{title}</a>'
    return href

# Function to create a download link for HTML
def create_download_link_html(df, title="Download HTML", filename_prefix="data"):
    now = datetime.now()
    timestamp = now.strftime("%d %B, %A %Y, %I:%M %p")
    filename = f"{filename_prefix}_{timestamp}.html"
    
    # Define row colors
    row_colors = ["#FFB6C1", "#B0E0E6", "#D3D3D3"]
    
    # Add CSS styles and row colors to the HTML content
    css_styles = f"""
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 20px;
        }}
        table.dataframe {{
            font-size: 14px;
            background-color: #f7f7f7;
        }}
        th {{
            background-color: #333;
            color: white;
        }}
        tr:nth-child(odd) {{
            background-color: {row_colors[0]};
        }}
        tr:nth-child(even) {{
            background-color: {row_colors[1]};
        }}
        th, td {{
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }}
        th {{
            background-color: {row_colors[2]};
        }}
    </style>
    """
    
    html_content = df.to_html(escape=False, index=False)
    full_html = f"<!DOCTYPE html><html><head>{css_styles}</head><body>{html_content}</body></html>"
    
    b64 = base64.b64encode(full_html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">{title}</a>'
    return href

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
]

st.title("Movie Search App")

st.sidebar.header("Movie Details")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file with movie details", type=["csv"])

url_options = {
    "vidsrc.to": st.sidebar.checkbox("vidsrc.to", value=True),
    "vidsrc.me": st.sidebar.checkbox("vidsrc.me", value=True),
    "smashystream.com": st.sidebar.checkbox("smashystream.com", value=True),
    "2embed.me": st.sidebar.checkbox("2embed.me", value=True),
    "2embed.cc": st.sidebar.checkbox("2embed.cc", value=True),
    "databasegdriveplayer.xyz": st.sidebar.checkbox("databasegdriveplayer.xyz", value=True),
}

if uploaded_file is not None:
    movie_data = pd.read_csv(uploaded_file)
    results = []
    
    progress_bar = st.progress(0)
    with tqdm(total=len(movie_data)) as pbar:
        for index, row in movie_data.iterrows():
            movie_name = row['Movie Name']
            release_year = row['Release Year']
            imdb_id = search_movie_imdb(movie_name, release_year)
            imdb_hyperlink = generate_imdb_hyperlink(imdb_id)
            urls_with_imdb_ids = generate_urls_with_imdb_ids(imdb_id)
            imdb_titles = {}
            for site, url in urls_with_imdb_ids.items():
                execute = url_options.get(site, False)
                title = get_title_from_imdb_url(url, execute)
                imdb_titles[site] = title
            result_dict = {
                'Movie Name': movie_name,
                'Release Year': release_year,
                'IMDb': imdb_hyperlink,
                'IMDb ID': imdb_id,
            }
            for site, execute in url_options.items():
                if execute:
                    result_dict[site] = urls_with_imdb_ids.get(site, 'Not Found')
                    result_dict[f"{site} Title"] = imdb_titles.get(site, 'Not Found')
            results.append(result_dict)
            pbar.update(1)
            st.text(f"Processed: {index + 1}/{len(movie_data)}")
    progress_bar.empty()
    
    selected_columns = ['Movie Name', 'Release Year', 'IMDb', 'IMDb ID'] + \
                       [site for site, execute in url_options.items() if execute] + \
                       [f"{site} Title" for site, execute in url_options.items() if execute]
    results_df = pd.DataFrame(results)[selected_columns]
    
    st.subheader("Search Results")

    # Add CSS to style the DataFrame
    st.markdown(
        """
        <style>
        table.dataframe {
            font-size: 14px;
        }
        th {
            background-color: #333;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(results_df)

    st.subheader("Download Results")
    csv_filename_prefix = "movie_search_results"
    csv_link = create_download_link_csv(results_df, "Download CSV", csv_filename_prefix)
    st.markdown(csv_link, unsafe_allow_html=True)
    
    html_filename_prefix = "movie_search_results"
    html_link = create_download_link_html(results_df, "Download HTML", html_filename_prefix)
    st.markdown(html_link, unsafe_allow_html=True)
