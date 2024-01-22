import json
import os
import sys
from typing import List
from typing import Dict

import aiohttp
import shutil
import asyncio
# import weasyprint as wp

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
        skip_chapters: Dict[str, str]):
        self.name = name
        self.max_chapter = max_chapter
        self.partial_chapter_url = partial_chapter_url
        self.chapter_exceptions = chapter_exceptions
        self.skip_chapters = skip_chapters

class Config:
    def __init__(
        self, 
        save_path: str, 
        comics_data_path: str):
        self.save_path = save_path
        self.comics_data_path = comics_data_path

CONFIG: Config = None
COMIC_DATAS: List[ComicData] = []

def get_comic_chapters_to_download(comic_data: ComicData) -> List[str]:
    chapters_to_download: List[str] = []
    chapter_range = range(1, comic_data.max_chapter + 1)
    for chapter in chapter_range:
        if(chapter in comic_data.skip_chapters):
            continue
        if(chapter in comic_data.chapter_exceptions):
            chapters_to_download.append(f"{comic_data.partial_chapter_url}{comic_data.chapter_exceptions[chapter]}")
            continue
        chapters_to_download.append(f"{comic_data.partial_chapter_url}{chapter}")
    return chapters_to_download

# Create a single session for the application
async def get_session():
    return aiohttp.ClientSession()

# Make sure the request is successful before proceeding.
async def handle_request_response(response):
    if response.status == 200:
        return await response.read()
    else:
        log("Failed to download chapter.", Error, response.status)
        return None

async def verify_chapter_exists(chapters: list) -> bool:
    session = await get_session()
    return BeautifulSoup()

async def begin_download(chapter: str) -> bool:
    pass

if __name__ == "__main__":
    setup_logging()
    log("Starting comic downloader.")
    config_json = None
    with open("config.json") as file:
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
    results = []
    for comic_data in COMIC_DATAS:
        chapters = get_comic_chapters_to_download(comic_data)
        log(f"Starting async downoad of {comic_data.name}.")
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(begin_download(chapters))
            results.append((comic_data.name, f"Download of {comic_data.name} was a success.", Info, None, True))
        except Exception as e:
            results.append((comic_data.name, f"There was an error downloading {comic_data.name}.", Error, e, False))
        finally:
            loop.close()
        log(f"Finished async downoad of {comic_data.name}.")    

    log("Finished comic downloader.")
    log(list(map(lambda x: f"{x[1]}", results)))









# # Extract the image urls from the html content.
# async def extract_chapter(content):
#     entry_content = BeautifulSoup(content, 'html.parser').find('div', class_='entry-content')
#     image_urls = [img['src'] for img in entry_content.find_all('img') if img['src'].endswith(".jpg")]
#     return image_urls

# # Download the image from url and save to folder path
# async def download_image(session, image_url, folder_path, index):
#     async with session.get(image_url) as response:
#         if response.status == 200:
#             content = await response.read()
#             file_path = os.path.join(folder_path, f"{index}.jpg")
#             with open(file_path, "wb") as file:
#                 file.write(content)
#                 log(f"Image {index} downloaded successfully to path {os.path.abspath(file_path)}.")
#         else:
#             log(f"Failed to download image {index}.", Warning)

# # Download the images of the chapter based on their urls, and save to folder chapter_{chapter}
# async def download_images_from_url_list(session, image_url_list, chapter):
#     folder_path = f"chapter_{chapter}"
#     if image_url_list is None or not image_url_list:
#         log("No images to download.", Warning)
#         return False

#     if not os.path.exists(folder_path):
#         os.mkdir(folder_path)

#     tasks = [download_image(session, image_url, folder_path, i) for i, image_url in enumerate(image_url_list)]
#     await asyncio.gather(*tasks)
#     return True

# # Compile the images in folder chapter_{chapter} into a pdf file. Then delete folder
# async def compile_images_to_pdf(chapter):
#     folder_path = f"chapter_{chapter}"
#     pdf_path = f"Tower_Of_God_chapter_{chapter}.pdf"

#     if not os.path.exists(folder_path):
#         log(f"Folder {folder_path} does not exist.", Warning)
#         return False

#     pdf = FPDF(unit='mm')  # Initialize without default format
#     max_width = 210  # Max width for A4 size in mm

#     try:
#         for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
#             if filename.endswith(".jpg"):
#                 image_path = os.path.join(folder_path, filename)
#                 with Image.open(image_path) as img:
#                     width, height = img.size
#                     # Convert image dimensions from pixels to millimeters
#                     width_mm, height_mm = width * 0.264583, height * 0.264583

#                     # Scale image if it's wider than max_width
#                     if width_mm > max_width:
#                         scale_factor = max_width / width_mm
#                         width_mm *= scale_factor
#                         height_mm *= scale_factor

#                     # Set custom page size
#                     pdf.set_auto_page_break(auto=False, margin=0)
#                     pdf.add_page(orientation='P')
#                     pdf.set_fill_color(0, 0, 0)  # Black background
#                     pdf.rect(0, 0, max_width, height_mm, 'F')  # Fill the page

#                     # Calculate x position to center image
#                     x_position = max(0, (max_width - width_mm) / 2)
#                     pdf.image(image_path, x_position, 0, width_mm, height_mm)
                    
#         # for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
#         #     if filename.endswith(".jpg"):
#         #         image_path = os.path.join(folder_path, filename)
#         #         with Image.open(image_path) as img:
#         #             width, height = img.size
#         #             # Convert image dimensions from pixels to millimeters
#         #             width_mm, height_mm = width * 0.264583, height * 0.264583

#         #             # Set custom page size
#         #             pdf.add_page(orientation='P', format=(width_mm, height_mm))
#         #             pdf.image(image_path, 0, 0, width_mm, height_mm)
            
#     except Exception as e:
#         log(f"Error compiling images to PDF.", Error, e)
#         return False

#     pdf.output(pdf_path, "F")
#     shutil.rmtree(folder_path)
#     log(f"PDF {pdf_path} created successfully. Deleting folder {folder_path}.")
#     return True

# # Download the chapter and save it to a pdf file.
async def download_chapter(session, url, chapter):
    url = f"https://w42.thetowerofgod.com/manga/tower-of-god-chapter-{chapter}/"
    try:
        async with session.get(url) as response:
            content = await handle_request_response(response)
            if content:
                image_urls = await extract_chapter(content)
                if not await download_images_from_url_list(session, image_urls, chapter):
                    log(f"Failed to download chapter {chapter}.", Warning)
                    return False
                if not await compile_images_to_pdf(chapter):
                    log(f"Failed to compile chapter {chapter} to pdf.", Warning)
                    return False
                return True
        return False
    except Exception as e:
        log(f"Error downloading chapter {chapter}", Error, e)
        return False

# # Check if chapter exists by checking if the chapter's URL contains an image from blogspot.
# # This is done by making an asynchronous HTTP request to the chapter's URL.
# async def check_if_chapter_exists(session, chapter):
#     url = f"https://w42.thetowerofgod.com/manga/tower-of-god-chapter-{chapter}"
#     try:
#         async with session.get(url) as response:
#             if response.status == 200:  # Check if the response status is 200 (OK).
#                 content = await response.text()  # Read the response content asynchronously.
#                 soup = BeautifulSoup(content, 'html.parser')  # Parse the content with BeautifulSoup.
#                 images = soup.find_all('img')  # Find all image tags in the parsed content.
#                 for image in images:
#                     if 'blogspot' in image['src'] or 'blogger' in image['src']:  # Check if any image source contains 'blogspot'.
#                         log(f"Chapter {chapter} exists.")
#                         return True  # Return True if such an image is found.
#                 log(f"Chapter {chapter} does not exist.", Warning)
#                 return False  # Return False if no 'blogspot' image is found.
#             log(f"Failed to check if chapter {chapter} exists.", Warning)
#             return False  # Return False if the response status is not 200.
#     except Exception as e:
#         log(f"Error checking chapter {chapter}", Error, e)
#         return False

# # Check if there already is an existing pdf. So it only downloads the files that are not downloaded yet.
# def check_if_chapter_is_downloaded(chapter):
#     # Check if the chapter exists by checking if the pdf exists
#     file = f"Tower_Of_God_chapter_{chapter}.pdf"
#     return os.path.exists(file)
    
# # Download chapter if it exists on the web and not on the local machine.
# async def download_tower_of_god_chapter(session, chapter):
#     if check_if_chapter_is_downloaded(chapter):
#         log(f"Chapter {chapter} already downloaded.")
#         return True

#     if not await check_if_chapter_exists(session, chapter):
#         log(f"Chapter {chapter} does not exist.")
#         return False
    
#     log(f"Downloading chapter {chapter}.")
#     return await download_chapter(session, chapter)

# # Adjust the main function to use a single session
# async def main():
#     session = await get_session()  # Create a session
#     try:
#         chapters = [download_tower_of_god_chapter(session, i) for i in range(1, MAX_CHAPTERS + 1)]
#         results = await asyncio.gather(*chapters)
#         log("Finished downloading chapters.")
#         log(f"Total chapters: {sum(results)}")
#     finally:
#         await session.close()  # Close the session
