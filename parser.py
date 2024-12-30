import requests
from bs4 import BeautifulSoup


def no_attributes(tag):
    return tag.name == 'div' and not tag.attrs


def fetch_jobs(query, max_pages=1):  
    url = 'https://hh.ru/search/vacancy'
    
    params = {
        'area': 113,  # Россия
        'only_with_salary': True,
        'L_save_area': True,
        'search_field': 'name',
        'text': query 
    }
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    vacancies = []

    for page in range(max_pages):
        params['page'] = page

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html5lib')
        main_content = soup.find(id="a11y-main-content")
        job_cards = main_content.find_all(no_attributes)

        for card in job_cards:
            all_spans = card.find_all('span')
            if len(all_spans) > 10:
                vacancies.append({
                    'title': all_spans[2].get_text(strip=True),
                    'description': f'{all_spans[7].get_text(strip=True)} / {all_spans[6].get_text(strip=True)} / {all_spans[10].get_text(strip=True)}'
                })
    return vacancies