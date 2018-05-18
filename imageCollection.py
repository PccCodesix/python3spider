import os
import urllib
import urllib3
import json
import re
import base64
from bs4 import BeautifulSoup

#python 3
HTTP=urllib3.PoolManager()
urllib3.disable_warnings()
# 需要手动自定义
questionId=34243513# 知乎问题id
oauthString='c3cef7c66a1843f8b3a9e6a1e3160e20'# 请求知乎时的oath(浏览器请求header里)
client_id='Qwe7NIZyoQLjeBZawKEKcjag'# 百度人脸识别 应用ID
client_secret='eraO3x5cfioGh04yYQvUxmwX7tVxp4ry' #百度人脸识别 密钥
Url='https://www.zhihu.com/question/'+str(questionId)


def Getimage():
    header={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
        'Host':'www.zhihu.com',
        'Referer':'https://www.zhihu.com/question/'+str(questionId),  
        'authorization': 'oauth '+oauthString,
        'accept':'application/json, text/plain, */*'
    }
    headerimg={
        'Host':'',
        'accept':'image/png, image/svg+xml, image/*; q=0.8, */*; q=0.5',
        'Referer':'https://www.zhihu.com/question/'+str(questionId),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }
    offset=0 # 返回的 json 数据偏移量
    imageindex=0 # 生成的照片 id 自增 让每次照片名字不同
    while offset<100:
        urllist='https://www.zhihu.com/api/v4/questions/'+str(questionId)+'/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit=20&offset='+str(offset)
        content=HTTP.request('GET',url=urllist,headers=header)
        #print(content.data)
        contetJosn=json.loads(content.data)
        datapage=0
        while datapage<20: #返回的json 数组的 大小
            contenJosnHTML=contetJosn.get('data')[datapage].get('content')
            soup=BeautifulSoup(contenJosnHTML,'html.parser')
            listitem=soup.findAll(name = 'img', attrs = 
					{'data-rawwidth':re.compile(r'\d{0,4}'), 'src':re.compile(r'https://')})
            for imgitem in listitem:
                imgurl=imgitem.get('src')# 图片的url 地址
                hostactual=imgurl[8:22]# 得到每张图片的host
                #print(hostactual) #暂时用字符串 处理方式 得到图片链接，实际返回的数据是json数据，可用json处理
                headerimg['Host']=hostactual# 设置没每张图片的 host
                IMGcontent= HTTP.request('GET',imgurl,headers=headerimg)
                with open('./images'+str(questionId)+'/'+str(imageindex)+'.jpg','wb') as f:
                    f.write(IMGcontent.data)
                imageindex+=1
            datapage+=1      
        offset+=20 

def CreatFloder():
    if not  os.path.exists('imagesNew'+str(questionId)):
        os.mkdir('imagesNew'+str(questionId))


def identificationImge():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+client_id+'&client_secret='+client_secret
    # 获取百度人脸识别的api
    heraderIdentity={
        'Content-Type':'application/json; charset=UTF-8'
    }
    accessTokenContent=HTTP.request('GET',url=host,headers=heraderIdentity)
    accessToken=accessTokenContent.data.decode()
    key=json.loads(accessToken)['access_token']# 获取请求人脸识别的 accesstoken
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    request_url = request_url + "?access_token=" + key   
    list=os.listdir('images'+str(questionId))
    for i in list:
        #print(i)
        with open('./images'+str(questionId)+'/'+i,'rb') as f:
            bytedata=f.read()
            ls_f=base64.b64encode(bytedata)
            params ={
               'image':str(ls_f,'utf-8'), 
               'image_type':'BASE64',
               'face_field':'faceshape,facetype,gender',
               'max_face_num':5
            }
            jsonparas=json.dumps(params).encode('utf-8')
            response=HTTP.request('Post',url=request_url,body=jsonparas,headers=heraderIdentity)
            responsedata=response.data.decode()# 人脸识别 结果
            #转为python对象
            if not responsedata is None:# 结果判断规则
                obj=json.loads(responsedata)
                if not obj is None:
                    isHaveFace=obj.get('result')
                    if not isHaveFace is None:
                        isHaveFace=isHaveFace.get('face_num')
                        isfemale=obj.get('result').get('face_list')[0]['gender']['type']
                        if(int(isHaveFace)>0 and isfemale=='female' ):# 有人脸且 被识别为女
                            with open('./imagesNew'+str(questionId)+'/'+i+'.jpg','wb') as t:
                                t.write(bytedata)


CreatFloder()# 以问题ID为后缀创建 图片的文件夹
Getimage()# 下载图片
CreatFloder() #创建人脸识别后的 图片保存位置
identificationImge()# 识别图片（人脸识别）

