from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def get_ads():

    url = 'https://ikman.lk/en/ads?by_paying_member=0&sort=relevance&buy_now=0&query=bmw&page=1'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        adEntries = []

        for li_tag in html.find_all('li', {'class':['gtm-normal-ad','gtm-top-ad']}):
            adEntry = dict() 
            adDetail = dict()
            for a_tag in li_tag.find_all('a', {'class':'gtm-ad-item'}):
                detailUrl = 'https://ikman.lk' + a_tag['href']
                # print(detailUrl)
                adEntry['url'] = detailUrl
                # value = span_tag.find('span', {'class':'pull-right'}).text
                adDetailsFetched = get_ad_details(detailUrl)    
                adEntry['contact']=adDetailsFetched['contact']
                adDetail['full_description'] = adDetailsFetched['description']
                adDetail['image_urls'] = adDetailsFetched['images']
                adEntry['details'] = adDetail
                adEntry['date']=adDetailsFetched['date']
                	
                for h_div in a_tag.find_all('div', {'class':'content--3JNQz'}):
                	h_name = h_div.find('span', {'class':'title--3yncE'}).text
                	adEntry['title']=h_name
                	# print(h_name)
                	div_list = h_div.findAll('div')
                	milage = div_list[1].text
                	# print(milage)
                	price = h_div.find('div', {'class':'price--3SnqI'}).find('span').text
                	adEntry['price']=price
                	# print(price)
                	describtion = h_div.find('div', {'class':'description--2-ez3'}).text
                	adEntry['category']=describtion
                	# print(describtion)
            adEntries.append(adEntry)    	

        
        return adEntries

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url))

def get_ad_details(url):
    
    response = simple_get(url)

    if response is not None:
        detailsHtml = BeautifulSoup(response, 'html.parser')
        images = []
        contact=""
        date=""

        for img_dev in detailsHtml.find_all('div', {'class':'gallery-nav'}):
            for a_tag in img_dev.find_all('a', {'class':'gallery-nav-item'}):
                imgTag = a_tag.find('img')
                if imgTag is not None :
                    detailImageUrl = imgTag['src']
                    images.append(detailImageUrl)
                    # print(detailImageUrl)

        des=""
        for des_dev in detailsHtml.find_all('div', {'class':'item-description'}):
            for p in des_dev.select('p'):
                des = des + p.text + ","

        des = des.rstrip(',')
        # print(des) 
        for contact_dev in detailsHtml.find_all('div', {'class':'item-contact-more'}):
            contact = contact_dev.find('span').text
            # print(contact)
        for date_p in detailsHtml.find_all('p', {'class':'item-intro'}):
            date = date_p.find('span',{'class':'date'}).text  
            # print(date)  
        adDetails = {}    
        adDetails['contact'] = contact
        adDetails['description'] = des
        adDetails['images'] = images
        adDetails['date'] = date
    return adDetails

if __name__ == '__main__':

    ikmanAds = get_ads()
    adJsonString= json.dumps(ikmanAds, indent=2)
    print(adJsonString)

    with open('ikman_ads.json', 'w', encoding='utf-8') as f:
        json.dump(ikmanAds, f, ensure_ascii=False, indent=2)
    print('... done.\n')

 


