#！/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2018-03-09 22:42:05
@author: wangzheng
Sys_Env : Windows_AMD64 Python3.5.2
Email:yaoyao12348@126.com
Filename: xxx.py
Description : 
"""
import json
import os
import sqlite3
import datetime as dt
import requests

def get_current_ip():
    '''获取当前IP'''
    url='http://httpbin.org/ip'
    r=requests.get(url)
    if r.status_code==200:
        r.encoding='utf-8'
        ip=r.json()['origin']
        print('当前IP:',ip)
        return ip
    return ''
    
def AddIP(appid='5a5c8912',ip_str=''):
    '''添加ip到白名单'''
    if ip_str=="":
        ip_str=get_current_ip()
    ip_lst=get_AppWebAPIWhiteIPs(appid=appid)
    if ip_str not in ip_lst:
        if len(ip_lst)==20:
            print("目前白名单已满20，需移除后才能添加新的IP")
            print('移除最后一个IP',ip_lst.pop(-1))
        ip_lst.append(ip_str)
        wl=','.join(ip_lst)
        if ModifyAppWebAPIWhiteIPs(appid=appid,whiteList=wl) :
            print(ip_str,"成功加入白名单！")
    else:
        print(ip_str,"本来就在白名单中！")
        
    pass
def get_AppWebAPIWhiteIPs(appid='5a5c8912'):
    '''查询应用程序当前的IP白名单'''
    url='http://aiui.xfyun.cn/apps/getAppWebAPIWhiteIPs'
    headers={
            'Accept':'application/json, text/plain, */*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Cookie':get_cookie(),#'pgv_pvi=119840768; hibext_instdsigdip=1; hibext_instdsigdipv2=1; token=0091d977-a2cd-4a03-baba-df928c1aec32; account_id=3589679469; trdipcktrffcext=1',
            'Host':'aiui.xfyun.cn',
            'Referer':'http://aiui.xfyun.cn/myApp/whiteList/'+appid,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            }
    params= {
            'timestamp':get_timestamp(),#'1520601702462'
            'appid':appid,#'5a5c8912'
            }
    r=requests.get(url,headers=headers,params=params)
    if r.status_code==200:
        r.encoding='utf-8'
        j=r.json()
        if j['code']=='0':
            t=j['data']
            lst=t.split(sep=',')
            print('当前IP白名单:',lst)
            return lst

    pass
def ModifyAppWebAPIWhiteIPs(appid='5a5c8912',whiteList=''):
    '''修改ip白名单'''
    if whiteList=='':
        whiteList='101.132.139.80,119.39.91.175,106.224.6.53'
    url='http://aiui.xfyun.cn/apps/doWebAPIWhiteIPEdit'
    headers={
            'Accept':'application/json, text/plain, */*',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Content-Length':'76',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie':get_cookie(),#'pgv_pvi=119840768; hibext_instdsigdip=1; hibext_instdsigdipv2=1; token=0091d977-a2cd-4a03-baba-df928c1aec32; account_id=3589679469; trdipcktrffcext=1',
            'Host':'aiui.xfyun.cn',
            'Origin':'http://aiui.xfyun.cn',
            'Referer':'http://aiui.xfyun.cn/myApp/whiteList/'+appid,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            }
    params= {
            'timestamp':get_timestamp(),#'1520601702462'
            }
    datas=  {
            'appid':appid,#'5a5c8912'
            'ips':whiteList,#'101.132.139.80,119.39.91.175,106.224.6.53'
            }
    #r=requests.post(url,headers=headers,params=params)
    r=requests.post(url,headers=headers,params=params,data=datas)
    #r=requests.post(url,headers=headers,params=params,data=datas,cookies=cookie)
    if r.status_code==200:
        r.encoding='utf-8'
        j=r.json()
        if j['code']=='0':
            print(j['desc'])
        return True
def get_cookie():
    cookie=get_cookies_xfyun()
    #dict格式 转换成 cookie str
    s=[]
    for key in cookie.keys():
        s.append('{}={}'.format(key,cookie[key]))
    t=';'.join(s)
    return t

def get_cookies_xfyun(fpath='xfyun.cookies'):
    '''首先查看当前目录下有无xfyun.cookiees文件，如有则从文件中读取数据；
    如无，则读取本地浏览器中保存的xfyun.cn网站cookies数据，并保存成xfyun.cookiees文件'''
    if os.path.exists(fpath):
        with open(fpath,'r',encoding='utf-8') as f:
            cookie_str=f.read()
        cookie=json.loads(cookie_str,encoding='utf-8')
        return cookie
    else:
        cookie1=get_cookie_from_chrome(host='.xfyun.cn')
        cookie2=get_cookie_from_chrome(host='aiui.xfyun.cn')
        cookie=dict_merge(cookie1,cookie2)
        if 'trdipcktrffcext' not in cookie:
            cookie['trdipcktrffcext']=1
        with open(fpath,'w',encoding='utf-8') as f:
            cookie_str=json.dumps(cookie)
            f.write(cookie_str)    
    return cookie

def get_cookie_from_chrome(host='.eastmoney.com',debug=False):
    '''从本地chrome浏览器cookies中读取数据，返回dict类型'''
    from win32.win32crypt import CryptUnprotectData
    cookiepath=os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
    sql="select host_key,name,encrypted_value from cookies where host_key='%s'" % host
    #sql="select host_key,name,encrypted_value from cookies "
    with sqlite3.connect(cookiepath) as conn:
        cu=conn.cursor()    
        cookies={name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
        if debug:print(cookies.keys())#输出键名列表
        return cookies

def dict_merge(dic1,dic2,debug=False):
    '''合并两个字典,有重复键名的以dic1为准'''
    dic0={}
    for key in dic2.keys():
        dic0[key]=dic2[key]
    for key in dic1.keys():
        dic0[key]=dic1[key]
    if debug:print('%d keys + %d keys >>> %d keys'%(len(dic1),len(dic2),len(dic0)))
    return dic0  
 
def get_timestamp(n=13,d=0):
    '''获取当前时间的时间戳  n总长度，d小数位'''
    now=dt.datetime.now()
    timestamp=now.timestamp()*1000#13位ms级
    strfmt='%%%d.%df'%(n,d)#'%13.0f'
    return strfmt%timestamp

if __name__=="__mian__":
    AddIP()
    pass
