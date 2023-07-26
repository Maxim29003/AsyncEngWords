from bs4 import BeautifulSoup
from gtts import gTTS
import time
import asyncio
import motor.motor_asyncio
import sys


mutex = asyncio.Lock()

id_grupps = [
    'gruppa-1--mestoimeniya',
    'gruppa-2--vremya-proshloe-budushchee-nastoyashchee',
    'gruppa-3--chisla-i-cifry',
    'gruppa-4--predlogi-i-soyuzy',
    'gruppa-5--chelovek-semya-telo-vneshnost-odejda',
    'gruppa-6--rabota-i-uvlecheniya',
    'gruppa-7--harakteristiki-cveta-i-svoystva',
    'gruppa-8--glagoly',
    'gruppa-9--eda-produkty-i-posuda',
    'gruppa-10--dom-i-byt',
    'gruppa-11--puteshestviya-i-dvijenie',
    'gruppa-12---priroda',
    'gruppa-13--znakomstvo-beseda-i-perepiska'
]


async def speak_text(text):
    try:
        audio = gTTS(text, lang='en', slow=True)
        audio.save(f'media/{text}.mp3')
    except:
        print("Ошибка с озвучкой слова")
        sys.exit()
    return f'media/{text}.mp3'


async def get_words(html_content, id, collection):
    soup = BeautifulSoup(html_content, 'html.parser')
    target_element = soup.find('h3', id=id)
    if target_element:
        next_element = target_element.find_next_sibling('div')
        group = target_element.get_text()
        if next_element:
            i = 0
            data_word = {}
            
            for td in next_element.find_all('td'):
                data_word["group"] = group
                res = td.get_text()
                res = res.strip()
                if i == 0:
                    i+=1
                    data_word["number"] = int(res[:-1])
                elif i == 1:
                    data_word["word"] = res
                    data_word["audio_url"] = await speak_text(res.replace("/", "").replace(" ", ""))
                    i+=1
                elif i == 2:
                    data_word["translation"] = res
                    async with mutex:
                        await collection.insert_one(data_word)
                    data_word = {}
                    i=0
            
        else:
            print('нет элемента')
            sys.exit()
    else:
        print('нет элемента с id ')
        sys.exit()



async def main():
    tasks = []
    with open('data.html', "r") as file:
        html_content = file.read()

    client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)

    db = client['data_words']
    collection = db['words']

    for gruppa in id_grupps:
        task = asyncio.create_task(get_words(html_content, gruppa, collection))
        tasks.append(task)
   
    await asyncio.gather(*tasks)
    client.close()

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print('Время: ', time.time()-start)