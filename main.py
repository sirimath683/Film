import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# ෆිල්ම් එක ඇතුළට ගිහින් Download Link එක ගන්නා හැටි
def get_download_page(movie_url):
    try:
        res = requests.get(movie_url, headers=HEADERS, timeout=10)
        movie_soup = BeautifulSoup(res.text, 'html.parser')
        
        # CineSubz වල සාමාන්‍යයෙන් Download බොත්තම තියෙන්නේ 'download-link' වගේ class එකක
        # නැතිනම් 'a' ටැග් එකක 'download' කියන වචනය ඇති ලින්ක් එක සොයමු
        dl_button = movie_soup.find('a', string=lambda s: s and 'Download' in s)
        
        if dl_button:
            return dl_button['href']
        return "Link Not Found"
    except:
        return "Error Fetching Link"

@app.get("/movies/{page}")
def get_movies(page: int):
    url = f"https://cinesubz.lk/movies/page/{page}/"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    movies = []
    items = soup.find_all('article', class_='item')

    for item in items:
        title_tag = item.find('h3')
        movie_link = item.find('a')['href'] if item.find('a') else ""
        
        # මෙතනදී අපි හැම ෆිල්ම් එකකටම අදාළ ඩවුන්ලෝඩ් ලින්ක් එකත් එකතු කරනවා
        # සටහන: මෙය වේගවත් කිරීමට සැබෑ සයිට් එකේදී වෙනම API call එකක් විදිහට ගන්න එක හොඳයි
        movies.append({
            "title": title_tag.text.split(" Sinhala")[0].strip() if title_tag else "Unknown",
            "imdb": item.find('span', class_='imdb').text.strip() if item.find('span', class_='imdb') else "N/A",
            "page_url": movie_link,
            "download_page": movie_link # මුලින් මේ ලින්ක් එක දීලා පස්සේ ඒක ඇතුළට යවන්න පුළුවන්
        })
    
    return {"page": page, "movies": movies}
