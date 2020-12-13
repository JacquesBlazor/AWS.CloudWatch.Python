# --- The MIT License (MIT) Copyright (c) alvinconstantine(alvin.constantine@outlook.com), Tue Dec 12 14:15pm 2020 ---

from datetime import datetime, timezone
import boto3
import json
import logging
import ast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s') #
region_name = 'ap-east-1'  # 香港 region
client = boto3.client('logs', region_name=region_name)
logGroupName = '/aws/lambda/Python-Quant-Invest-Slack'  # 該 log group 的名稱
log_streams_response = client.describe_log_streams(logGroupName=logGroupName, orderBy='LogStreamName', descending=True, limit=2) # 只蒐集最近幾(5)次的 Log Stream
filenameprefix = logGroupName.split('/')[-1]  # 最後要存檔的檔名

listOfLogStreamName = {}  # 暫時存放在字典裡
request_id = None  # 這是 aws 的 log 裡的 lambda 裡的每次的 RequestId 的編碼
target = None  # 這是目前要存放資料的目標

for index, content in enumerate(log_streams_response['logStreams']):
    logStreamName = content['logStreamName']
    log_events_response = client.get_log_events(
        logGroupName=logGroupName,
        logStreamName=logStreamName,
        startFromHead=True
    )

    stream = logStreamName.split(']')[-1]  # 這是純脆的 log stream 名稱

    if stream not in listOfLogStreamName:  # 用 log stream 名稱做為字典鍵值
        listOfLogStreamName[stream] = {}

    for i_item in log_events_response['events']:  # 這是每個 log stream 裡的不同階段的 aws events
        message = i_item['message'].strip()  # 這是每個 aws events 裡的訊息本身
        splited_msg = message.split('\t')  # 每個 aws events 裡預設會用 tab 分隔不同的資訊
        meta = {}  # 暫時把每次的 aws event 存放在字典裡

        if len(splited_msg) == 1:  #  如果這個 aws event 裡沒有用 tab 分隔不同的資訊則...
            splited_msg = message.split(' ')  #  將該 aws event 裡用 space 分隔的資訊拆開
            if splited_msg[0]=='START':  # 如果這個 aws event 是 START 開頭, 代表這是 aws lambda 被 trigger 的開頭
                if len(splited_msg)>3 and splited_msg[1]=='RequestId:' and len(splited_msg[2])==36 and splited_msg[2][8] == '-' and splited_msg[2][13] == '-' and splited_msg[2][18] == '-' and splited_msg[2][23] == '-': # 這個 START 開頭的事件, 接著會有一個 36 個字元的字串代表 RequestId 並且中間有 - 符號分隔
                    request_id = splited_msg[2]  # 把目前的 request_id 記錄為現在最近的 RequestId
                    if request_id not in listOfLogStreamName[stream]:  # 如果目前還沒有這筆 RequestId 的資料
                        listOfLogStreamName[stream][request_id] = {}  # 建立一個新的字典用來存放這個 RequestId 的資料裡的相關記錄
                        listOfLogStreamName[stream][request_id]['start_timestamp'] = datetime.fromtimestamp(i_item['timestamp'] //1000).strftime('%Y-%m-%d, %H:%M:%S')
                        listOfLogStreamName[stream][request_id]['start_ingestionTime'] = datetime.fromtimestamp(i_item['ingestionTime'] //1000).strftime('%Y-%m-%d, %H:%M:%S')
                        listOfLogStreamName[stream][request_id]['lambda_events'] = []  # 同時用建立一個新的串列用來存放這個 RequestId 的資料裡的所有事件 event 記錄
                        if len(splited_msg)==5 and request_id and splited_msg[3]=='Version:' and listOfLogStreamName[stream][request_id]:
                            listOfLogStreamName[stream][request_id]['version'] = splited_msg[4]
                        target = listOfLogStreamName[stream][request_id]['lambda_events'] # 然後 target 會指向接下來同一筆 RequestId 的所有事件 event 記錄的目標位置
                        continue
                    else:
                        logging.error('same request_id start again!')
                else:
                    logging.error('START but does not match the contition!')
            if splited_msg[0]=='END':  # 如果這個 aws event 是 END 開頭, 代表這是 aws lambda 被 trigger 的結尾
                if len(splited_msg)==3 and splited_msg[1]=='RequestId:' and len(splited_msg[2])==36 and splited_msg[2][8] == '-' and splited_msg[2][13] == '-' and splited_msg[2][18] == '-' and splited_msg[2][23] == '-':
                    if request_id:
                        if splited_msg[2] == request_id:
                            if request_id not in listOfLogStreamName[stream]:
                                logging.error('same request_id but does not have a list item!')
                                listOfLogStreamName[stream][request_id] = {}
                            listOfLogStreamName[stream][request_id]['end_timestamp'] = datetime.fromtimestamp(i_item['timestamp'] //1000).strftime('%Y-%m-%d, %H:%M:%S')
                            listOfLogStreamName[stream][request_id]['end_ingestionTime'] = datetime.fromtimestamp(i_item['ingestionTime'] //1000).strftime('%Y-%m-%d, %H:%M:%S')
                            continue
                else:
                    logging.error('END but does not match the contition!')
        if splited_msg[0].startswith('REPORT'):  # 如果這個 aws event 是 REPORT 開頭, 代表這是 aws lambda 被 trigger 完後的摘要報告
            splited_msg = splited_msg[0].split(' ') + splited_msg[1:]
            if splited_msg[1]=='RequestId:' and len(splited_msg[2])==36 and splited_msg[2][8] == '-' and splited_msg[2][13] == '-' and splited_msg[2][18] == '-' and splited_msg[2][23] == '-':
                if request_id:
                    if splited_msg[2] == request_id:
                        if request_id not in listOfLogStreamName[stream]:
                            logging.error('same request_id but does not have a list item!')
                            listOfLogStreamName[stream][request_id] = {}
                        listOfLogStreamName[stream][request_id]['Report'] = splited_msg[3:]
                        continue
        # 如果不是前述的 3 種類型那就不是 aws lambda 的事件而是程式本身的事件, 這段 for 的內容是依照 slack 的 event 特別客製的可能不適用於其他類型的程式
        for element in splited_msg:
            if element:
                msgElement = element.strip()
                if msgElement.startswith('[') and msgElement.endswith(']'):
                    meta['log_type'] = msgElement.lstrip('[').rstrip(']')
                elif msgElement[-1] == 'Z' and msgElement[10] == 'T':
                    getDateTime = datetime.strptime(msgElement, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
                    meta['datetime'] = getDateTime.strftime('%Y-%m-%d, %H:%M:%S')
                elif msgElement.startswith('event:'):
                    meta['request_event'] = ast.literal_eval(msgElement.lstrip('event: '))
                elif len(msgElement) ==36 and msgElement[8] == '-' and msgElement[13] == '-' and msgElement[18] == '-' and msgElement[23] == '-':
                    if request_id != msgElement:
                        logging.error('request_id mishmatch!')
                else:
                    if not 'msg_content' in meta:
                        meta['msg_content'] = []
                    meta['msg_content'].append(msgElement)
        if meta:
            if isinstance(target, list):
                target.append(meta)
            else:
                logging.error('non_categroized found!')
                if 'non_categroized' not in listOfLogStreamName:
                    listOfLogStreamName['non_categroized'] = []
                listOfLogStreamName['non_categroized'].append(meta)

with open('%s_%d.json' % (filenameprefix, abs(datetime.now().timestamp()*1000*1000)), 'w', encoding='utf-8-sig') as f:
    json.dump(listOfLogStreamName, f, ensure_ascii=False, indent=2)


