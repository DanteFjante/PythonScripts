
import json 
import os
import sys
from typing import List
from typing import Dict

import asyncio
import aiohttp

import pathlib
import shutil

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from bs4 import BeautifulSoup
from PIL import Image

from lib.LoggingSetup import setup_logging, log, Info, Warning, Error



class ComicData:
    def __init__(
        self, 
        name: str, 
        max_chapter: int, 
        partial_chapter_url: str, 
        chapter_exceptions: List[str], 
        skip_chapters: Dict[str, str],
        start_chapter: int):
        self.name = name
        self.max_chapter = max_chapter
        self.partial_chapter_url = partial_chapter_url
        self.chapter_exceptions = chapter_exceptions
        self.skip_chapters = skip_chapters
        self.start_chapter = start_chapter

class Config:
    def __init__(
        self, 
        save_path: str, 
        comics_data_path: str,
        wkhtmltopdf_path: str):
        self.save_path = save_path
        self.comics_data_path = comics_data_path
        self.wkhtmltopdf_path = wkhtmltopdf_path

CONFIG: Config = None
COMIC_DATAS: List[ComicData] = []


def get_comic_chapters_to_download(comic_data: ComicData) -> List[str]:
    chapters_to_download: List[str] = []
    chapter_range = range(comic_data.start_chapter, comic_data.start_chapter + comic_data.max_chapter)
    for chapter in chapter_range:
        if(chapter in comic_data.skip_chapters):
            continue
        except_dict: Dict[str, str] = {}
        for ch, exc in comic_data.skip_chapters:
            except_dict[chapter] = exc
        val = except_dict.get(str(chapter))
        if(val is not None):
            chapters_to_download.append(f"{comic_data.partial_chapter_url}{comic_data.chapter_exceptions[chapter]}")
            continue
        chapters_to_download.append(f"{comic_data.partial_chapter_url}{chapter}")
    return chapters_to_download

def get_chapter_images_save_dir(comic_name: str, chapter: int) -> str:
    return f"./temp/{comic_name}_chapter_{chapter}/"

def get_chapter_pdf_save_file_name(comic_name: str, chapter: int) -> str:
    return f"./output/{comic_name}_chapter_{chapter}.pdf"

def get_session() -> aiohttp.ClientSession:
    return aiohttp.ClientSession()

async def verify_chapter_exists(chapter_url: str) -> bool:
    async with get_session() as session:
        async with session.get(chapter_url) as response:
            # Check for successful response
            if response.status != 200:
                return False

            if not chapter_url.endswith("/"):
                chapter_url += "/"
            current_session_url = str(response.url)
            if not current_session_url.endswith("/"):
                current_session_url += "/"
            
            # Check if any redirection occurred
            if current_session_url != chapter_url:
                return False
            
            return True

async def get_page_content(chapter_url: str) -> str:
    # Verify url
    if not await verify_chapter_exists(chapter_url):
        log(f"Chapter {chapter_url} does not exist.", Warning)
        return None
    
    # Get the content
    content = None
    async with get_session() as session:
        async with session.get(chapter_url) as response:
            content = await response.text()
    # Return the content
    if content is not None:
        return content
    else:
        return None
    
async def get_page_image_urls(page_content: str) -> List[str]:
    
    # Extract the image urls from the html content.
    entry_content = BeautifulSoup(page_content, 'html.parser').find('div', class_='entry-content')
    image_urls = [str((img['src'])).replace("\t", "").replace("\n", "") for img in entry_content.find_all('img') if img['src'].endswith(".jpg")]
    return image_urls

async def save_image_to_file(image_url: str, folder_path: str, index: int) -> bool:
    async with get_session() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                content = await response.read()
                file_path = os.path.join(folder_path, f"image_{str(index).zfill(3)}.jpg")
                try:
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                    with open(file_path, "wb") as file:
                        file.write(content)
                        log(f"Image {index} downloaded successfully to path {os.path.abspath(file_path)}.")
                        return True
                except Exception as e:
                    log(f"Failed to save image {index} to path {os.path.abspath(file_path)}.", Warning, e)
                    return False
            else:
                log(f"Failed to download image {index}.", Warning)
                return False

async def save_images(page_content: str, comic_name: str, chapter:int) -> bool:
    img_urls = await get_page_image_urls(page_content)
    save_dir = get_chapter_images_save_dir(comic_name, chapter)
    save_tasks = []
    for i, url in enumerate(img_urls, 1):
        task = save_image_to_file(url, save_dir, i)
        save_tasks.append(task)
    successes = await asyncio.gather(*save_tasks)
    if(all(successes)):
        return True
    return False

async def compile_images_to_pdf(comic_data: ComicData, chapter: int) -> bool:
    try:
        image_dir = get_chapter_images_save_dir(comic_data.name, chapter)
        images = [os.path.join(image_dir, img) for img in sorted(os.listdir(image_dir)) if img.endswith('.jpg')]

        c = canvas.Canvas(get_chapter_pdf_save_file_name(comic_data.name, chapter), pagesize=letter)
        page_width, page_height = letter

        for image_path in images:
            with Image.open(image_path) as img:
                img_width, img_height = img.size

                # Calculate the scaling factor to maintain aspect ratio
                scale = min(page_width / img_width, page_height / img_height)

                # Calculate new dimensions
                new_width = img_width * scale
                new_height = img_height * scale

                # Center the image on the page
                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2

                c.drawImage(image_path, x, y, new_width, new_height)

            c.showPage()  # Creates a new page for each image

        c.save()
    except Exception as e:
        print(e)
        log(f"Failed to compile chapter {comic_data.name}: {chapter} to pdf.", Error, e)
        return False
    finally:
        shutil.rmtree(image_dir)
    return True


async def process_comic(comic_data: ComicData) -> Dict[str, bool]:
    download_results: Dict[str, bool] = {}
    # Get the chapters to download
    chapters = get_comic_chapters_to_download(comic_data)

    pages = []
    # Save every task in a list
    for chapter in chapters:
        pages.append(get_page_content(chapter))
    
    # Run all task asynchronously
    pages = await asyncio.gather(*pages)
    # Filter out the None values
    pages = list(filter(lambda x: x is not None, pages))
    # Save images
    save_tasks = []
    for chapter, page in enumerate(pages, comic_data.start_chapter):
        key = f"{comic_data.name}: {chapter}"
        save_tasks.append(save_images(page, comic_data.name, chapter))
        
        # Run all save tasks asynchronously
        save_results = await asyncio.gather(*save_tasks)
        # Check if all save tasks were successful
        download_results[key] = True
        if not all(save_results):
            log(f"Failed to download chapter {key}.", Warning)
            download_results[key] = False
            continue
        
        if not await compile_images_to_pdf(comic_data, chapter):
            log(f"Failed to compile chapter {key} to pdf.", Warning)
            download_results[key] = False
    return download_results

async def process_all_comics(tasks):
    results = await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    setup_logging()
    log("Starting comic downloader.")
    config_json = None
    with open("./ComicDownload/config.json") as file:
        config_json = json.load(file)
        CONFIG = Config(**config_json["config"])    
    comic_data_files = [file for file in os.listdir(CONFIG.comics_data_path) if file.endswith(".json")]
    for data_file in comic_data_files:
        data_json = json.load(open(f"{CONFIG.comics_data_path}/{data_file}"))
        COMIC_DATAS.append(ComicData(**data_json["comic_data"]))
    
    log(get_comic_chapters_to_download(COMIC_DATAS[0]))
    # Make sure asynio workes for system
    if sys.platform == 'win32':
        log("Setting asyncio event loop policy for Windows.", Info)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    log("Finished initiating comic downloader.")
    tasks = []
    results = []
    for comic_data in COMIC_DATAS:
        tasks.append(process_comic(comic_data))
    log("Starting async download.")
    loop = asyncio.get_event_loop()
    try:
        results = loop.run_until_complete(process_all_comics(tasks))
    except Exception as e:
        log("Failed to run script.", Error, e)
    finally:
        loop.close()

    log("Finished comic downloader.")
    log(results)

