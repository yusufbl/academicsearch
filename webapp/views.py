from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tzz
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from datetime import datetime


from zemberek import TurkishSpellChecker, TurkishMorphology

morphology = TurkishMorphology.create_with_defaults()
sc = TurkishSpellChecker(morphology)

password = "..."
myclient = MongoClient("mongodb+srv://....:" + password + ".....mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["database"]
col = mydb["collection"]


es = Elasticsearch(
    ['http://localhost:9200'],  # Elasticsearch sunucusunun URL'si ve portu
    http_auth=('elastic', 'K-iTHsaHC8JCzfvsKkt9'),  # Opsiyonel: Kimlik doğrulama bilgileri
)

def home(request):
    return redirect('homePage')

def homePage(request):
    return render(request, "index.html")


def get_yayin_detay(request, yayin_adi):
    
    yayin = col.find_one({'yayin_adi': yayin_adi})

    if yayin:
        context = {'yayin': yayin} 
        return render(request, 'yayin_detay.html', context)
    else:
        
        return render(request, 'yayin_detay.html', {'error_message': 'Yayın bulunamadı.'})

def search_and_save(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        if keyword:

            liste = keyword.split(' ')
            sonSekil=""

            for kelime in liste:
                bado=sc.suggest_for_word(kelime)
                if kelime in bado:
                    sonSekil+=" "+kelime
                else:
                    sonSekil+=" "+ bado[0]

            
            url = f'https://dergipark.org.tr/tr/search?q={keyword}&section=articles'
            
            
            response = requests.get(url)
            
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            
            articles = soup.select('.card.article-card.dp-card-outline .card-body .card-title a:not(.article-meta a)')
            
            
            counter = 1
    
            
            for article in articles[:10]:
                title = article.text.strip()
                href = article['href']
                
                
                article_response = requests.get(href)
                article_soup = BeautifulSoup(article_response.content, 'html.parser')

                
                turkish_to_english_month = {
                    'Ocak': 'January',
                    'Şubat': 'February',
                    'Mart': 'March',
                    'Nisan': 'April',
                    'Mayıs': 'May',
                    'Haziran': 'June',
                    'Temmuz': 'July',
                    'Ağustos': 'August',
                    'Eylül': 'September',
                    'Ekim': 'October',
                    'Kasım': 'November',
                    'Aralık': 'December'
                }

                
                publication_date = article_soup.find('th', text='Yayımlanma Tarihi')
                if publication_date:
                    publication_date_value_str = publication_date.find_next('td').text.strip()

                    
                    for turkish_month, english_month in turkish_to_english_month.items():
                        publication_date_value_str = publication_date_value_str.replace(turkish_month, english_month)

                    
                    publication_date_value_str = publication_date_value_str.replace(", midnight", "")
                    publication_date_value = datetime.strptime(publication_date_value_str, '%d %B %Y')

                else:
                    publication_date_value=None
                
                
                keywords = article_soup.select('.article-keywords.data-section a')
                keyword_texts = [keyword.text.strip() for keyword in keywords]
                
                
                abstracts = article_soup.select('.article-abstract.data-section p')
                abstract_texts = [abstract.text.strip() for abstract in abstracts]
                
                
                publisher = article_soup.select_one('.row')['aria-label']
                
                
                authors = article_soup.select('.article-authors a')
                author_names = [author.text.strip() for author in authors]
                
                
                publication_type = article_soup.select_one('.kt-portlet__head-title').text.strip()
                
                
                doi_element = article_soup.select_one('.article-doi.data-section a')
                doi = doi_element.text.strip() if doi_element else None
                
                
                citation_count_element = article_soup.find('div', class_='kt-badge kt-badge--dot kt-badge--lg kt-badge--primary separator')
                citation_count = None
                if citation_count_element:
                    a_element = citation_count_element.find_next_sibling('a')
                    if a_element:
                        citation_count = a_element.text.strip()
                
                
                references = article_soup.select('.article-citations.data-section ul li i.fa-li.fa.fa-quote-left[aria-hidden=true]')
                reference_texts = [ref.parent.text.strip() for ref in references]

                
                article_toolbar_link = article_soup.select_one('.kt-portlet__body #article-toolbar a')['href']

               
                inserted_doc = col.insert_one({
                    'yayin_id': counter,
                    'yayin_adi': title,
                    'yayin_hrefi': href,
                    'anahtar_kelimeler_makale': keyword_texts,
                    'ozet': abstract_texts,
                    'yayinci_adi': publisher,
                    'yazarlarin_isimleri': author_names,
                    'anahtar_kelime_arama': keyword,
                    'yayimlanma_tarihi': publication_date_value,
                    'yayin_turu': publication_type,
                    'doi': doi,
                    'alinti_sayisi': citation_count,
                    'referanslar': reference_texts,
                    'article_toolbar_link': article_toolbar_link,
                    'created_at': tzz.now()
                })

                
                es.index(index='yayinlar', body={
                    'yayin_id': counter,
                    'yayin_adi': title,
                    'yayin_hrefi': href,
                    'anahtar_kelimeler_makale': keyword_texts,
                    'ozet': abstract_texts,
                    'yayinci_adi': publisher,
                    'yazarlarin_isimleri': author_names,
                    'anahtar_kelime_arama': keyword,
                    'yayimlanma_tarihi': publication_date_value,
                    'yayin_turu': publication_type,
                    'doi': doi,
                    'alinti_sayisi': citation_count,
                    'referanslar': reference_texts,
                    'article_toolbar_link': article_toolbar_link,
                    'created_at': tzz.now()
                })
                
                
                counter += 1
                
                
                alinti1_yayinlar = col.find(
                    {'anahtar_kelime_arama': keyword, 
                    'alinti_sayisi': {'$ne': None},
                    
                    },
                    {'yayin_adi': 1}
                )
                yayin_adi_list_alinti = [yayin['yayin_adi'] for yayin in  alinti1_yayinlar]


                
                doi_yayinlar = col.find(
                    {'anahtar_kelime_arama': keyword, 
                    
                    'doi': {'$ne': None}
                    },
                    {'yayin_adi': 1}
                )
                yayin_doi_list = [yayin['yayin_adi'] for yayin in doi_yayinlar]

                
                filtered_yayinlar = col.find(
                    {'anahtar_kelime_arama': keyword, 
                    'alinti_sayisi': {'$ne': None},
                    'doi': {'$ne': None}
                    },
                    {'yayin_adi': 1}
                )
                filtered_yayin_list = [yayin['yayin_adi'] for yayin in filtered_yayinlar]


                
                result2 = col.find({'anahtar_kelime_arama': keyword}, {'yayin_adi': 1}).limit(10).sort([('yayimlanma_tarihi', -1)])
                yayin_adi_list_kb = [data['yayin_adi'] for data in result2]

                
                result3 = col.find({'anahtar_kelime_arama': keyword}, {'yayin_adi': 1}).limit(10).sort([('yayimlanma_tarihi', 1)])
                yayin_adi_list_bk = [data['yayin_adi'] for data in result3]   
            
           
            search_results = es.search(index='yayinlar', body={'query': {'match': {'anahtar_kelime_arama': keyword}}}, size=10)
            hits = search_results['hits']['hits']
            print("Elasticsearch'ten dönen belge sayısı:", len(hits))

            
            unique_yayin_adi_set = set()

            
            yayin_adi_list = []
            for hit in hits:
                yayin_adi = hit['_source']['yayin_adi']
                
                if yayin_adi not in unique_yayin_adi_set:
                    unique_yayin_adi_set.add(yayin_adi)
                    yayin_adi_list.append(yayin_adi)

                    
            return render(request, 'result.html', {'yayin_adi_list': yayin_adi_list,'sonSekil': sonSekil, 'yayin_adi_list_bk':  yayin_adi_list_bk, 'yayin_adi_list_kb':  yayin_adi_list_kb, 'yayin_adi_list_alinti': yayin_adi_list_alinti, 'yayin_doi_list':  yayin_doi_list, 'filtered_yayin_list': filtered_yayin_list})


    return render(request, 'search.html')
