import requests
from bs4 import BeautifulSoup
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import os
import sys
import argparse


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

def breaking_range(chapter_number, all_chapters):
    chapters_range = chapter_number.split(':')
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

    if splited_user_chapters:
        for chapter_number in splited_user_chapters:
            if ":" in chapter_number:
                breaking_range(chapter_number, all_chapters)
            else: 
                chapter_number = int(chapter_number)
                all_chapters.append(chapter_number)

        sorted_chapters = sorted(list(set(all_chapters)))
    else:
        print("Пожалуйста напишите правильно номера глав")
        sys.exit(1)

    return sorted_chapters

def find_manga_on_page(manga_search_url, manga_title):
    page_number = 0
    found = False

    while not found:
        page_number += 1
        print(f"Поиск манги на странице {page_number} ...", end="\r")
        params = {"page": page_number}
        response = requests.get(manga_search_url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        selector = "main div.grid-cols-2 .manga-card a h2"
        cards = soup.select(selector)
        for card in cards:
            if manga_title in card.text:  
                print(f"Поиск манги на странице {page_number} ... Найдено             ")
                a = card.parent
                manga_slug = a["href"].split("/")[-1]
                found = True  
                break  
            else:
                print(f"Поиск манги на странице {page_number} ...  Не найдено", end="\r")
                
    return manga_slug

def get_first_and_last_chapter(soup):
    first_chapter_href = soup.find_all("h2")[1].parent["href"]
    first_chapter = first_chapter_href.split("/")[-1].split("-")[-1]
    first_chapter = int(first_chapter)

    last_chapter_href = soup.find_all("h2")[2].parent["href"]
    last_chapter = last_chapter_href.split("/")[-1].split("-")[-1]
    last_chapter = int(last_chapter)

    return first_chapter, last_chapter

def get_and_download_images(chapter_number, manga_slug, image_paths):
    root_folder = "imgs"
    url = "https://mangapoisk.live/manga"
    folder = f"page{chapter_number}"
    page_number = f"1-{chapter_number}"
    os.makedirs(os.path.join(f"{root_folder}/{folder}"), exist_ok=True)

    images_url = os.path.join(f"{url}/{manga_slug}/chapter/{page_number}")
    response = requests.get(images_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    imgs = soup.find_all("img")

    for ordinal, img in enumerate(imgs):
        if "pages" in img["src"]:
            img_url = img["src"]

            response = requests.get(img_url)
            response.raise_for_status()

            filename = f"/img{ordinal}"
            file_extension = img_url.split(".")[-1]
            filepath = os.path.join(f"{root_folder}/{folder}/{filename}.{file_extension}")
            with open(filepath, 'wb') as f:
                f.write(response.content)

            image_paths.append(filepath)

def create_pdf_file(image_paths, chapter_number, manga_slug):
    os.makedirs("temporary_storage", exist_ok=True)
    os.makedirs("manga_storage", exist_ok=True)
    os.makedirs(os.path.join("manga_storage", manga_slug), exist_ok=True)

    manga_path = os.path.join("manga_storage", manga_slug, f"Глава{chapter_number}.pdf")

    c = canvas.Canvas(manga_path, pagesize=letter)
    page_width, page_height = letter
    page_width, page_height = int(page_width), int(page_height)

    ordinal = 1
    number_pictures_per_cycle = 0
    new_image_paths = []

    for image_path in image_paths:

        img = Image.open(image_path)
        img_width, img_height = img.size
        img_width, img_height = int(img_width), int(img_height)

        for i in range(0, img_height, page_height):
            number_pictures_per_cycle += 1

            box = (0, i, img_width, min(i + page_height, img_height))
            img_part = img.crop(box)
            img_num = (i//page_height) + ordinal

            temp_image_path = f'temporary_storage/temp_{img_num}.jpg'
            new_image_paths.append(temp_image_path)
            img_part.save(temp_image_path)

        ordinal += number_pictures_per_cycle
        
    for image_path in new_image_paths:
        img = Image.open(image_path)
        img_width, img_height = img.size
        img_width, img_height = int(img_width), int(img_height)

        c.drawImage(image_path, 0, 0, width=page_width, height=page_height)
        c.showPage()
        
    c.save()

def clear_storage_cut_imgs():
    folder_path = 'temporary_storage'
    image_files = [f for f in os.listdir(folder_path)]
    image_paths = [os.path.join(folder_path, f) for f in image_files]

    for image in image_paths:
        try:
            os.remove(image)
        except Exception as e:
            print(f'Ошибка при удалении {image}: {e}')

def clear_storage_imgs(image_paths, chapter_number):
    folder_path = f'imgs/page{chapter_number}'
    image_files = [f for f in os.listdir(folder_path)]
    image_paths = [os.path.join(folder_path, f) for f in image_files]

    for image in image_paths:
        try:
            os.remove(image)
        except Exception as e:
            print(f'Ошибка при удалении {image}: {e}')


def main():
    parser = argparse.ArgumentParser(description="Скачивает манги и преобразует их в pdf файлы.")
    parser.add_argument("--chapters", type=str, help="Введите главы которые необходимо скачать. Можно указывать необходимые главы через запятую, либо же указать диапазон. Пример: 1, 2, 3:10. Если оставить это значение пустым, тогда скачаются все главы.")
    parser.add_argument("--url", type=str, help="Введите адрес страницы с мангой.")
    parser.add_argument("--name", type=str, help="Введите название манги которую нужно скачать(этот способ будет выполняться медленнее, чем если указать адрес).")
    args = parser.parse_args()

    user_chapters = args.chapters
    manga_page_url = args.url
    manga_title = args.name
    download_all_chapters = False
    all_chapters = []

    if user_chapters:
        numbers_sorted_chapters = get_correct_sorted_chapters(user_chapters, all_chapters)
    else:
        print("Будут скачаны все главы.")
        download_all_chapters = True

    if manga_page_url:
        manga_slug = manga_page_url.split("/")[-1]
    elif manga_title: 
        manga_search_url = "https://mangapoisk.live/manga"
        manga_slug = find_manga_on_page(manga_search_url, manga_title)  
        manga_page_url = f"https://mangapoisk.live/manga/{manga_slug}"
    else:
        print("Введите или название манги или ссылку на нее")
        sys.exit(1)

    try:
        response = requests.get(manga_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        first_chapter, last_chapter = get_first_and_last_chapter(soup)

    except requests.exceptions.ConnectionError:
        print("Введена неправильная ссылка.")
        sys.exit(1)
    except requests.exceptions.HTTPError as err:
        print(f"Ошибка HTTP: {err}")
        sys.exit(1)

    numbers_relevant_chapters = []
    if download_all_chapters:
        for chapter_number in range(first_chapter, last_chapter):
            numbers_relevant_chapters.append(chapter_number)
    else:
        for chapter_number in numbers_sorted_chapters:
            if chapter_number <= last_chapter and chapter_number >= first_chapter:
                numbers_relevant_chapters.append(chapter_number)

    image_paths = []
    for chapter_number in numbers_relevant_chapters:
        get_and_download_images(chapter_number, manga_slug, image_paths)
        create_pdf_file(image_paths, chapter_number, manga_slug)

        clear_storage_cut_imgs()
        clear_storage_imgs(image_paths, chapter_number)
        image_paths = []
        print(f"Глава{chapter_number} скачалась")



if __name__ == "__main__":
    main()
