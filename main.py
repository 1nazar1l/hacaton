import requests
from bs4 import BeautifulSoup
import datetime

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

def breaking_range(item, chapters):
    chapters_range = item.split(':')
    min, max = chapters_range
    min, max = int(min), int(max)
    if min > max:
        min, max = max, min
    for i in range(min, max+1):
        chapters.append(i)

def get_correct_sorted_chapters(user_string, chapters):
    splited_string = user_string.split(',')
    for num, number in enumerate(splited_string):
        number = get_correct_number(number, is_range(number))
        splited_string[num] = number
        if number == "":
            splited_string.remove("")
        elif number == " ":
            splited_string.remove(" ")
     
    for item in splited_string:
        if ":" in item:
            breaking_range(item, chapters)
        else: 
            item = int(item)
            chapters.append(item)

    sorted_chapters = sorted(list(set(chapters)))
    if sorted_chapters[0] == 0:
        sorted_chapters.remove(0)

    return sorted_chapters

def find_manga_on_page(url, text_to_find, manga):
    i = 9
    found = False

    while not found:
        i += 1
        params = {"page": i}
        response = requests.get(url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        selector = "main div.grid-cols-2 .manga-card a h2"
        cards = soup.select(selector)
        
        for card in cards:
            if text_to_find in card.text:  
                a = card.parent
                href = a["href"].split("/")[-1]
                manga.append(card.text)
                manga.append(href)
                found = True  
                break  

def find_last_chapter(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    href = soup.find_all("h2")[2].parent["href"]
    last_chapter = href.split("/")[-1].split("-")[-1]
    return int(last_chapter)

def main():
    user_string = "1:12"
    # user_string = input("Введите значения: ")
    chapters = []
    sorted_chapters_counter = get_correct_sorted_chapters(user_string, chapters)
    if len(sorted_chapters_counter) == 0:
        print("Перепроверьте главы которые вы написали для скачивания.")
    # print(sorted_chapters)

    current_time1 = datetime.datetime.now().time()
    # print(current_time1) 
    manga = []
    url = "https://mangapoisk.live/manga"
    text_to_find = "Жрец порчи" 
    find_manga_on_page(url, text_to_find, manga)  
    current_time2 = datetime.datetime.now().time()
    # print(current_time2) 

    url = f"https://mangapoisk.live/manga/{manga[1]}"
    last_chapter = find_last_chapter(url)
    # print(last_chapter)

    suitable_chapters_counter = []
    for number in sorted_chapters_counter:
        if number <= last_chapter:
            suitable_chapters_counter.append(number)
    # print(suitable_chapters_counter)
    z = 1
    os.makedirs("imgs", exist_ok=True)
    for i in suitable_chapters_counter:
        if z == 3:
            break
        page = f"imgs/page{i}"
        os.makedirs(page, exist_ok=True)
        url = f"https://mangapoisk.live/manga/{manga[1]}/chapter/1-{i}"
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
                # print(i["src"])
        z +=1

if __name__ == "__main__":
    main()
