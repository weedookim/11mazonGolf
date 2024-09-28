# %%
from bs4 import BeautifulSoup
import time
import os
import requests
import json
from datetime import datetime 

# %%
url = "https://www.fmkorea.com/index.php?mid=other_sports&category=4657164507"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# %%
# Function to fetch data from a URL
def fetch_bbs_data(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        print(f"Failed to fetch data from {url}, Status Code: {response.status_code}")
        return None

# %%
response = fetch_bbs_data(url)

if response != None:


    # 응답의 내용을 UTF-8로 디코딩하여 BeautifulSoup으로 파싱합니다.
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    # %%
    # 키워드 리스트
    keywords = ["딜", "핫딜", "deal", "hot deal", "iron", "아이언"]

    # 오늘 날짜
    today_date = datetime.today().strftime('%Y.%m.%d')


    # 결과 저장 리스트
    results = []

    # 모든 <tr> 태그를 찾고 반복
    for row in soup.find_all('tr'):
        
        title_td = row.find('td', class_='title hotdeal_var8')

        if title_td :
            # 'a' 태그가 있는지 확인
            title_tag = title_td.find('a', class_='hx')
            if title_tag:
                title = title_tag.text.strip()
                # print(title)
                link = title_tag['href']
                # print(link)

                date_tag = row.find('td', class_='time')

                if date_tag:
                    # print(date_tag.text.strip())
                    date = date_tag.text.strip()

                # print('date : ' + date)
                # print('today_date' + today_date)

                # 오늘 날짜 확인 및 키워드 포함 여부 확인 (오늘 날짜의 항목은 시간으로 표기됨)
                if date != today_date and any(keyword in title.lower() for keyword in keywords):
                    results.append({'title': title, 'link': 'https://www.fmkorea.com/' + link})
                    # print(title)
                    # print(link)

    #결과 출력
    # for result in results:
    #     print(f"Title: {result['title']}, Link: {result['link']}")            



    # %%

    # 웹훅 URL
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')



    # results 리스트의 각 항목을 슬랙에 전송
    for result in results:
        # 메시지를 전송할 데이터 구성
        # print(result)
        slack_data = {'text': result['title'] + '||' + '<' + result['link'] +'|Click here!>'}

        print(slack_data)

        # 웹훅에 POST 요청 보내기
        response = requests.post(
            slack_webhook_url, 
            #data=json.dumps(slack_data),
            json=slack_data,  # json 파라미터 사용
            #headers={'Content-Type': 'application/json'}
        )

        # 응답 확인 (성공 여부 확인)
        if response.status_code != 200:
            raise ValueError(f"Request to Slack returned an error {response.status_code}, the response is:\n{response.text}")

    # %%



