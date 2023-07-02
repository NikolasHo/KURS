import requests
from bs4 import BeautifulSoup


def find_recipes(keyword):
    #request informations
    url = "https://www.foodwithlove.de/?s=" + keyword + "&post_type=post"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # parse all articles and store header, image and href
    article_data = []

    articles = soup.find_all('article')

    for article in articles:
        article_dict = {}

        header = article.find('h3', class_='elementor-post__title').a.text
        article_dict['header'] = header.strip()

        link = article.find('a')['href']
        article_dict['link'] = link

        image = article.find('img')['src']
        article_dict['image'] = image

        article_data.append(article_dict)

    return article_data
