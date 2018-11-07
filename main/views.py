from django.shortcuts import render
import base64
import sys
from django.http import HttpResponse
from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import service_account
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup as BS
import os
import operator
import json


## handle the image uploads
@csrf_exempt
def handleUpload(request):
    # print(request.body)
    if request.method == 'POST' and request.FILES['file']:
        image = request.FILES['file']
        image_read = image.read()
        project_id = "essential-haiku-218118"
        model_id = "ICN747416880257459356"
        response = get_prediction(image_read, project_id,  model_id)
        # print(response)
        context_dict = {}
        for result in response.payload:
            if result.display_name=='Shoes':
                pass
            elif result.display_name=='Blouse':
                pass
            else:
                context_dict[result.display_name] = result.classification.score
        context_dict = sorted(context_dict.items(), key=operator.itemgetter(1), reverse=True)
        keywords = ""
        i = 0
        for key, value in context_dict:
            if i == 3:
                break
            else:
                if i == 0:
                     keywords = str(key)
                else:
                    keywords = str(key)+"-"+keywords
                i = i+1
        keywords = str(keywords)
        print(keywords)
        response_data = scrapper(keywords)
        return HttpResponse(json.dumps(response_data), content_type="application/json")
 

# direct google function to get the prediction
def get_prediction(content, project_id, model_id):
    credentials = service_account.Credentials.from_service_account_file('essential-haiku-218118-d43dfbd3f752.json')
    prediction_client = automl_v1beta1.PredictionServiceClient(credentials=credentials)
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content }}
    params = {"score_threshold": '0.2'}
    request = prediction_client.predict(name, payload, params)
    return request


def test(request):
    return render(request,'main/test.html')


# to initialte the driver 
# chrome driver is used for this selenium
def setup_webdriver():
    chrome_exec_shim = "/usr/bin/google-chrome-stable"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = chrome_exec_shim
    chrome_options.add_argument('--disable-gpu');
    chrome_options.add_argument('--no-sandbox');
    chrome_options.add_argument('headless');
    chrome_options.add_argument('--disable-dev-shm-usage');
    chrome_options.add_argument("start-maximized"); 
    chrome_options.add_argument("disable-infobars");
    chrome_options.add_argument("--disable-extensions"); 
    driver = webdriver.Chrome(executable_path='/home/sukhad_anand/visually-shopit/chromedriver', chrome_options=chrome_options)
    # chrome_options = webdriver.ChromeOptions()
    # prefs = {"profile.default_content_setting_values.notifications" : 2}
    # chrome_options.add_experimental_option("prefs",prefs)
    # driver = webdriver.Chrome(executable_path='/home/sukhad_anand/visually-shopit/chromedriver', chrome_options=chrome_options)
    return driver


# scrapper for myntra 
# the results that are returned is the img url and the buy url
# top 9 results are given
def scrapper(keywords):
    driver=setup_webdriver()
    url = "https://www.myntra.com/" + keywords
    print(url)
    driver.get(url)
    data = driver.page_source
    # print(data)
    soup = BS(data,"html.parser")
    divdata = soup.find_all('ul', {"class": "results-base"})
    # print(divdata)
    arr = []
    img_meta = divdata[0].find_all("img")
    a_meta = divdata[0].find_all("a")
    name_meta = divdata[0].find_all("h4", {"class": "product-product"})
    price_meta = divdata[0].find_all("span", {"class": "product-discountedPrice"})
    for (img,href,name,price) in zip(img_meta,a_meta,name_meta,price_meta):
        item = {}
        item['img'] = img["src"]
        item['href'] = "https://www.myntra.com/" + href["href"]
        item['name'] = str(name.getText())
        item['price'] = str(price.getText())
        arr.append(item)
    driver.close()
    return arr
