import requests
import json
import time
import re
import PdfToOCR

#ユーザー情報、URL
user='user'
pass_='pass'
url='url'

#対象年、OCR処理数
year = 1983
max_ocr = 0

#トグル追加用テキスト
text_st= '<div class="toggle-wrap"><input id="toggle-checkbox-20230331140231" class="toggle-checkbox" type="checkbox" /><label class="toggle-button" for="toggle-checkbox-20230331140231">OCR結果</label><span class="toggle-content">'
text_en= '</span></div>'



params = {
    'status': 'publish',
    'order' : 'desc',
    #'search': '',
    'page': '1',
    'per_page' : '10',
    'after': str(year-1)+'-12-31T23:59:59',
    'before': str(year)+'-12-31T23:59:59',
}

page=1
count = 0
end = 0

while True:
    params['page'] = str(page)
    req = requests.get(
        url,
        params=params,
        auth=(user, pass_),
        )
    
    if str(req) == '<Response [200]>':
        data = json.loads(req.content)
        time.sleep(1)
        for d in data:
            if count > max_ocr-1:
                end = 1
                break

            try:
                cheack = re.search(r'OCR結果', d['content']['rendered']).group()
                
            except:
                count += 1
                text_to_add = '読み取り未完了'
                updata_post_content = d['content']['rendered']
                
                print('ID', d['id'], count)
                print('タイトル',d['title']['rendered'])
                print('投稿日時',d['date'])
                print('リンク', 'url/?p='+str(d['id']))

                #OCR処理する
                pdf_url = re.search(r'.{1,25}pdf', d['content']['rendered']).group()
                text_to_add = PdfToOCR.ocr(pdf_url)
                #print('追加テキスト', text_to_add)

                #結果を追加
                updata_post_content += text_st + text_to_add + text_en
                
                #投稿をアップデート]
                end_point_url = url + str(d['id'])
                payload = {
                    'content' : updata_post_content ,
                    }
                headers = {'content-type': "Application/json"}
                
                r = requests.post( end_point_url, data=json.dumps(payload) , headers=headers, auth=(user, pass_) )

                print('update done.')
                print('-----------------------------------')

        if end > 0:
            break
        
        page += 1
        print('sleeping...')
        time.sleep(5)
    else:
        break

input('終了するにはなにかキーを押してください')
