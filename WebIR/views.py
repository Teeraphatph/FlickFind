import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator


API_KEY = "5cea14cdbac22f4e9e58bfea3ac53437"
BASE_URL = "https://api.themoviedb.org/3"

GENRES_MOVIE = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

GENRES_TV = {
    10759: "Action & Adventure", 16: "Animation", 35: "Comedy", 80: "Crime", 99: "Documentary",
    18: "Drama", 10751: "Family", 10762: "Kids", 9648: "Mystery", 10763: "News",
    10764: "Reality", 10765: "Sci-Fi & Fantasy", 10766: "Soap", 10767: "Talk",
    10768: "War & Politics", 37: "Western"
}

def search_movies(request):
    query = request.GET.get("q")
    filter_type = request.GET.get("type", "all")  # ค่า default = all
    page_number = request.GET.get("page", 1)
    results = []

    if query:   # ✅ ถ้ามีการค้นหา
        endpoints = []
        if filter_type == "movie":
            endpoints = ["movie"]
        elif filter_type == "tv":
            endpoints = ["tv"]
        else:
            endpoints = ["movie", "tv"]

        for endpoint in endpoints:
            url = f"{BASE_URL}/search/{endpoint}?api_key={API_KEY}&query={query}&language=th-TH"
            response = requests.get(url)
            if response.status_code == 200:
                results += response.json().get("results", [])
    else:       # ✅ ถ้ายังไม่ค้นหา → โชว์หนังใหม่/ยอดนิยม
        url = f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&language=th-TH"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])

    # ✅ จัดการชื่อ, วันที่, ประเภท, genres (ใช้ได้ทั้งตอนค้นหาและไม่ค้นหา)
    for item in results:
        item["display_title"] = (
            item.get("title") 
            or item.get("name") 
            or item.get("original_title") 
            or item.get("original_name") 
            or "(No Title)"
        )
        item["display_date"] = item.get("release_date") or item.get("first_air_date") or "-"

        if "title" in item or "original_title" in item:
            item["media_type"] = "Movie"
        elif "name" in item or "original_name" in item:
            item["media_type"] = "TV Show"
        else:
            item["media_type"] = "Unknown"

        if item["media_type"] == "Movie":
            item["genres"] = [GENRES_MOVIE.get(gid, "Unknown") for gid in item.get("genre_ids", [])]
        else:
            item["genres"] = [GENRES_TV.get(gid, "Unknown") for gid in item.get("genre_ids", [])]

        if not item["genres"]:
            item["genres"] = ["No genres available"]

        if not item.get("overview"):
        # ดึงข้อมูลรายละเอียดเรื่องนั้นแบบ language=en-US
            fallback_url = f"{BASE_URL}/{ 'movie' if item['media_type']=='Movie' else 'tv' }/{item['id']}?api_key={API_KEY}&language=en-US"
            res_fallback = requests.get(fallback_url)
            if res_fallback.status_code == 200:
                item["overview"] = res_fallback.json().get("overview", "")
            else:
                item["overview"] = "(No overview available)"

    # ✅ เรียงคะแนนมาก → น้อย
    results = sorted(results, key=lambda x: x.get("vote_average", 0), reverse=True)

    paginator = Paginator(results, 20)  
    page_obj = paginator.get_page(page_number)

    return render(request, "search/search.html", {
        "results": page_obj,   # ส่ง page object ไปแทน results
        "query": query,
        "type": filter_type,
        "page_obj": page_obj
    })







""" def search_movies(request):
    query = request.GET.get("q")
    filter_type = request.GET.get("type", "all")  # ค่า default = all
    page_number = request.GET.get("page", 1)
    results = []

    if query:   # ✅ ถ้ามีการค้นหา
        endpoints = []
        if filter_type == "movie":
            endpoints = ["movie"]
        elif filter_type == "tv":
            endpoints = ["tv"]
        else:
            endpoints = ["movie", "tv"]

        for endpoint in endpoints:
            url = f"{BASE_URL}/search/{endpoint}?api_key={API_KEY}&query={query}"
            response = requests.get(url)
            if response.status_code == 200:
                results += response.json().get("results", [])
    else:       # ✅ ถ้ายังไม่ค้นหา → โชว์หนังใหม่/ยอดนิยม
        url = f"{BASE_URL}/movie/now_playing?api_key={API_KEY}&language=en-US"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json().get("results", [])


        for item in results:
            item["display_title"] = (
                item.get("title") 
                or item.get("name") 
                or item.get("original_title") 
                or item.get("original_name") 
                or "(No Title)"
            )
            item["display_date"] = item.get("release_date") or item.get("first_air_date") or "-"
    
        if "title" in item or "original_title" in item:
            item["media_type"] = "Movie"
        elif "name" in item or "original_name" in item:
            item["media_type"] = "TV Show"
        else:
            item["media_type"] = "Unknown"
            
            if item["media_type"] == "Movie":
                item["genres"] = [GENRES_MOVIE.get(gid, "Unknown") for gid in item.get("genre_ids", [])]
            else:
                item["genres"] = [GENRES_TV.get(gid, "Unknown") for gid in item.get("genre_ids", [])]
            if not item["genres"]:
                item["genres"] = ["No genres available"]
        # เรียงคะแนนมาก → น้อย

        
        results = sorted(results, key=lambda x: x.get("vote_average", 0), reverse=True)
    
    paginator = Paginator(results, 20)  
    page_obj = paginator.get_page(page_number)

    return render(request, "search/search.html", {
        "results": page_obj,   # ส่ง page object ไปแทน results
        "query": query,
        "type": filter_type,
        "page_obj": page_obj
    })   
 """


