import requests
from bs4 import BeautifulSoup

import os


def get_correct_number(number, range=True):
    for el in number:
            if el in "1234567890":
                continue
            elif range and el == ":":
                 continue
            else:
                number = number.replace(el, "")
    return number

def is_range(number):
    err = -1
    for el in number:
        if el == ":":
            err += 1
        elif number[0] == ":" or number[-1] == ":":
            err += 1

    return err == 0

def breaking_range(item, all_chapters):
    chapters_range = item.split(':')
    min, max = chapters_range
    min, max = int(min), int(max)
    if min > max:
        min, max = max, min
    for chapter_number in range(min, max+1):
        all_chapters.append(chapter_number)

def get_correct_sorted_chapters(user_chapters, all_chapters):
    splited_user_chapters = user_chapters.split(',')
    for ordinal, chapter_number in enumerate(splited_user_chapters):
        chapter_number = get_correct_number(chapter_number, is_range(chapter_number))
        splited_user_chapters[ordinal] = chapter_number

    for chapter_number in splited_user_chapters:
        if chapter_number == "":
            splited_user_chapters.remove("")
        elif chapter_number == " ":
            splited_user_chapters.remove(" ")
     
    for chapter_number in splited_user_chapters:
        if ":" in chapter_number:
            breaking_range(chapter_number, all_chapters)
        else: 
            chapter_number = int(chapter_number)
            all_chapters.append(chapter_number)

    sorted_chapters = sorted(list(set(all_chapters)))
    if sorted_chapters[0] == 0:
        sorted_chapters.remove(0)

    return sorted_chapters

def find_manga_on_page(manga_search_url, text_to_find):
    i = 0
    found = False

    while not found:
        i += 1
        params = {"page": i}
        response = requests.get(manga_search_url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        selector = "main div.grid-cols-2 .manga-card a h2"
        cards = soup.select(selector)
        for card in cards:
            if text_to_find in card.text:  
                a = card.parent
                manga_slug = a["href"].split("/")[-1]
                found = True  
                break  
    
    return manga_slug

def find_last_chapter(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    href = soup.find_all("h2")[2].parent["href"]
    last_chapter = href.split("/")[-1].split("-")[-1]
    return int(last_chapter)

def download_images(numbers_relevant_chapters, manga_slug):
    os.makedirs("imgs", exist_ok=True)
    for i in numbers_relevant_chapters:
        page = f"imgs/page{i}"
        os.makedirs(page, exist_ok=True)
        url = f"https://mangapoisk.live/manga/{manga_slug}/chapter/1-{i}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        imgs = soup.find_all("img")
        o = 0
        for i in imgs:
            if "pages" in i["src"]:
                o += 1
                img_url = i["src"]
                response = requests.get(img_url)
                response.raise_for_status()
                file_extension = img_url.split(".")[-1]
                filepath = f"{page}/img{o}.{file_extension}"

                with open(filepath, 'wb') as f:
                    f.write(response.content)


def main():
    user_chapters = "3jsdfn.,1:9,0, ,:1:1ddad.,1sdf2."
    all_chapters = []
    numbers_sorted_chapters = get_correct_sorted_chapters(user_chapters, all_chapters)
    if len(numbers_sorted_chapters) == 0:
        print("Перепроверьте главы которые вы написали для скачивания.")
    print(numbers_sorted_chapters)

    # manga_page_url = input("Введите ссылку на страницу с мангой.")
    # manga_page_url = "https://mangapoisk.live/manga/the-reincarnated-assassin-is-a-genius-swordsman"
    # if manga_page_url:
    #     manga_slug = manga_page_url.split("/")[-1]
    # else:
    #     manga_search_url = "https://mangapoisk.live/manga"
    #     text_to_find = "Жрец порчи" 
    #     manga_slug = find_manga_on_page(manga_search_url, text_to_find)  
    #     manga_page_url = f"https://mangapoisk.live/manga/{manga_slug}"

    # last_chapter = find_last_chapter(manga_page_url)

    # numbers_relevant_chapters = []
    # for chapter_number in numbers_sorted_chapters:
    #     if chapter_number <= last_chapter:
    #         numbers_relevant_chapters.append(chapter_number)

    # download_images(numbers_relevant_chapters, manga_slug)

if __name__ == "__main__":
    main()
