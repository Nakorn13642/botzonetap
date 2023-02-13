#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
#from turtle import distance
from cgitb import handler
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import pandas as pd
from geopy import distance

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = 'dJtnbsqh9hkNLHAEmUIc66luvjc0hLu0IKHP4t1X7gxkbcJuhGWR9XTZX8/vD3ASvR7w0ufluAsmTVDkCqtLyyYS5Llknui2+1DjMJgRsUggppWc1+uM/2mi7sYbbXSOMo3qlET73lZLBak5b233AwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)
handler = WebhookHandler('e14c646a3e08f6afb5f5ccf3d7ed6c2e')

casedata = pd.read_excel('casedata.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])
        replyObj = handle_text(msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        txtresult = handle_location(lat,lng,casedata,3)
        replyObj = TextSendMessage(text=txtresult)
        line_bot_api.reply_message(rtoken, replyObj)
        
    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

def handle_location(lat,lng,cdat,topK):
    result = getdistace(lat, lng,cdat)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.3f'%(result.iloc[i]['km'])
        wordpeano = str(result.iloc[i]['pea_no'])
        trpeano = str(result.iloc[i]['FACILITYID'])
        nokva = str(result.iloc[i]['RATEKVA'])
        wordkva = str(result.iloc[i]['kva'])
        wordtapnow = str(result.iloc[i]['tap_now'])
        tapnow = str(result.iloc[i]['PRESENTTAP'])
        wordtapdig = str(result.iloc[i]['tap_dig'])
        dig = str(result.iloc[i]['Digsilent'])
        locationinstall = str(result.iloc[i]['LOCATION'])
        txtResult = txtResult + 'ห่าง %s กิโลเมตร\n%s %s\nขนาด%s %s\n%s %s\n%s %s\n%s\n\n'%(kmdistance,wordpeano,trpeano,nokva,wordkva,wordtapnow,tapnow,wordtapdig,dig,locationinstall)
    return txtResult[0:-2]


def getdistace(latitude, longitude,cdat):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = cdat[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(distance.distance(coords_1, coords_2).km)
  cdat['km'] = kmsumList
  return cdat

if __name__ == '__main__':
    app.run(debug=True)


########################################### flex ################################################

dat = pd.read_excel('addb.xlsx')
def getdata(query):
    res = dat[dat['QueryWord']==query]
    if len(res)==0:
        return 'nodata'
    else:
        productName = res['ProductName'].values[0]
        imgUrl = res['ImgUrl'].values[0]
        desc = res['Description'].values[0]
        cont = res['Contact'].values[0]
        return productName,imgUrl,desc,cont

def flexmessage(query):
    res = getdata(query)
    if res == 'nodata':
        return 'nodata'
    else:
        productName,imgUrl,desc,cont = res
    flex = '''
    {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "%s",
          "margin": "none",
          "size": "full",
          "aspectRatio": "1:1",
          "aspectMode": "cover",
          "action": {
            "type": "uri",
            "label": "Action",
            "uri": "https://linecorp.com"
          }
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "md",
          "action": {
            "type": "uri",
            "label": "Action",
            "uri": "https://linecorp.com"
          },
          "contents": [
            {
              "type": "text",
              "text": "%s",
              "size": "xl",
              "weight": "bold"
            },
            {
              "type": "text",
              "text": "%s",
              "wrap": true
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "ติดต่อคนขาย",
                "data": "%s"
              },
              "color": "#F67878",
              "style": "primary"
            }
          ]
        }
      }'''%(imgUrl,productName,desc,cont)
    return flex



from linebot.models import (TextSendMessage,FlexSendMessage)
import json

def handle_text(inpmessage):
    flex = flexmessage(inpmessage)
    if flex == 'nodata':
        replyObj = TextSendMessage(text=inpmessage)
    else:
        flex = json.loads(flex)
        replyObj = FlexSendMessage(alt_text='Flex Message', contents=flex)
    return replyObj