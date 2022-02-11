# Please run `pip install -r requirements.txt` first before you execute.
from concurrent.futures import thread
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from requests import get
from time import sleep
from PIL import Image
from io import BytesIO

ua = UserAgent()


def main(url):
    res = get(url, headers={'user-agent': ua.random})
    soup = BeautifulSoup(res.text, 'lxml')
    attr = soup.select('.tag-container')
    name = [i for i in url.split('/') if i][-1]
    info = {
        'url': url,
        'title': [i.text for i in reversed(soup.select('.title'))],
        'artist': [i.text for i in attr[3].select('.name')],
        'tag': [i.text for i in attr[2].select('.name')],
        'language': [i.text for i in attr[5].select('.name')][-1],
        'page': int(attr[7].select_one('.name').text),
    }
    images = [f'{url}{i+1}' for i in range(info['page'])]

    def download(idx, link):
        res = get(link, headers={'user-agent': ua.random})
        soup = BeautifulSoup(res.text, 'lxml')
        soup = soup.select_one('#image-container')
        link = soup.find('img')['src']
        img = Image.open(BytesIO(get(link).content))
        images[idx] = img.convert('RGB')

    with thread.ThreadPoolExecutor(max_workers=8) as pool:
        for idx, link in enumerate(images):
            pool.submit(download, idx, link)
            sleep(0.5)

    if str in [type(i) for i in images]:
        print("Download Fail!")
        return

    images.pop(0).save(f'{name}.pdf', save_all=True,
                       append_images=images)

    print("Download Success!")


if __name__ == '__main__':
    # You can change URL here to download 本本 that you want :)
    main("https://nhentai.net/g/319902/")
