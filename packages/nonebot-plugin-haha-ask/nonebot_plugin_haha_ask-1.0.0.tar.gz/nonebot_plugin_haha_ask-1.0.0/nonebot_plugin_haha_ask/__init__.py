# 敬启:今天也要好好的哦
# 来自:我的可爱们，刻晴，可莉等
# 时间:2022/1/19 23:38
import json
import os
import re
import datetime
import time
from selenium import webdriver
from os.path import dirname
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, MessageSegment, GroupMessageEvent
from typing import List, Union
from .geo_distance import geo_distance


askhh = on_command('askhh', aliases={'查询'})
askdis1 = on_command('dis1', aliases={'距离1'})
askdis2 = on_command('dis2', aliases={'距离2'})
old_time = datetime.datetime.now()
geo_distance=geo_distance()
site0='郑州'

@askdis1.handle()
async def _(bot: Bot, event: MessageEvent):
    global old_time # -2 自定义排除，此时site为排除地点 设想中
    await askdis1.send(f'返回距离默认地址距离，例子：北京  若不精确则可能返回其他地方的距离')
    site1=event.get_plaintext().replace('/距离1','').replace('/dis1','').replace(' ','')
    try:
        distance=geo_distance.get_distance(site1,site0)
        site1,site2=geo_distance.get_address_double()
        await bot.send(
            event=event,
            message=MessageSegment.text(site1+'与'+site2+'相距'+distance)
        )
    except Exception as res:
        print(res)
        await bot.send(
            event=event,
            message=MessageSegment.text("地理错误")
        )

@askdis2.handle()
async def _(bot: Bot, event: MessageEvent):
    global old_time # -2 自定义排除，此时site为排除地点 设想中
    await askdis2.send(f'前后两地距离地，例子：郑州。北京 若不精确则可能返回其他地方的距离')
    text=event.get_plaintext().replace('/距离2','').replace('/dis2','').replace(' ','')
    site=text.split('。')
    if len(site)==2:
        distance=geo_distance.get_distance(site[0],site[1])
        site[0],site[1]=geo_distance.get_address_double()
        await bot.send(
            event=event,
            message=MessageSegment.text(site[0]+'与'+site[1]+'两地距离'+distance)
        )
    else:
        await bot.send(
            event=event,
            message=MessageSegment.text("格式错误或地理错误")
        )

def get_page_source(url, browser, path, flag2):
    browser.get(url)
    time.sleep(2)
    if not flag2:
        with open(path + '.html', 'w', encoding='utf-8') as fp:
            fp.write(browser.page_source)

    return browser.page_source


def parse_page_source(page_source, path):
    page_source = re.findall(r'<li id=".*?class="car-list-item">(.*?)</li>', page_source, re.S)
    haha_list = []
    for source in page_source:
        text = ''
        text_list = re.findall(r'>(.*?)<', source, re.S)
        for x in text_list:
            text += x
        text = text.replace(' ', '').replace('\n', '').replace('【', '\n【')
        if '紫荆山' in text:
            continue
        l0 = [text]
        haha_list.extend(l0)

    if not os.path.exists(path + '.json'):
        with open(path + '.json', 'w', encoding='utf-8') as fp:
            json.dump(haha_list, fp)

    return haha_list


def browser_setting():
    print('正在唤起火狐浏览器,不显示，稍等即可...')
    # 进入浏览器设置
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    # 设置中文
    options.add_argument('lang=zh_CN.UTF-8')
    # 更换头部
    options.add_argument(
        'User-Agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"')
    options.add_argument('--headless')
    # 创建浏览器对象
    browser = webdriver.Chrome(options=options)
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    return browser



browser0 = browser_setting()
@askhh.handle()
async def _(bot: Bot, event: MessageEvent):
    global old_time # -2 自定义排除，此时site为排除地点 设想中
    await askhh.send(f'指令，0旧数据块但不保证时效，1时时新数据慢但保证时效,已默认排除紫荆山。\n查询地点，为0时查询排除紫荆山后所有信息。出发地。目的地\n请稍等2s到8s...')
    text=event.get_plaintext().replace('/查询','').replace('/askhh','').replace(' ','')
    text=text.split('。')
    flag0 = text[0]
    site = text[1]
    startCity = text[2]
    endCity = text[3]
    # https://hh.hnxzkj.cn/WebApp/home/AssList?startCity=%E5%B9%B3%E9%A1%B6%E5%B1%B1%E5%B8%82&endCity=%E9%83%91%E5%B7%9E%E5%B8%82&pageNum=1&numPerPage=20&seatNum=1&goTime=null&lastId=null&ordertype&isOnlinePay=null&showCarType=null
    url = 'https://hh.hnxzkj.cn/WebApp/Home/AssList?startCity=' + startCity
    url += '&endCity=' + endCity + '&_p=hot'
    path=dirname(__file__)+"/res/"
    if not os.path.exists(path):
        os.mkdir(path)
    path +=startCity + endCity
    now_time = datetime.datetime.now()
    print(str(now_time))
    
    flag2 = os.path.exists(path + '.html') and old_time.year - now_time.year == 0 and old_time.day - now_time.day == 0 and old_time.hour - now_time.hour == 0
    if flag0 == '0' and flag2:
        with open(path + '.html', 'r', encoding='utf-8') as fp:
            page_source = fp.read()
    else:
        page_source = get_page_source(url, browser0, path, flag2)
        old_time = now_time

    haha_list = parse_page_source(page_source,path)

    if site not in str(haha_list) and site!='0':
        await bot.send(
            event=event,
            message=MessageSegment.text('暂时没有直接说路经此地点的车主')
        )
        
    else:
        time_now = datetime.datetime.now()
        msgs=[str(time_now)+'\n暂时有直接说路经此地点的车主']
        for haha_driver_info in haha_list:
            if site in haha_driver_info or site=='0':              
                msgs.extend(['【时间】' + haha_driver_info])
        await send_forward_msg(bot, event, '王小小', bot.self_id, msgs)


async def send_forward_msg(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        uin: str,
        msgs: List[Union[str, MessageSegment]]
):
    def to_json(msg):
        return {
            'type': 'node',
            'data': {
                'name': name,
                'uin': uin,
                'content': msg
            }
        }

    msgs = [to_json(msg) for msg in msgs]
    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)