import os
import re
import random
import uncurl
import requests
from bs4 import BeautifulSoup
from notify import send



SEHUATANG_HOST = 'www.sehuatang.net'
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
user_cookie = os.getenv("CK_98TANG")

def daysign(cookies: dict) -> bool:
    with requests.Session() as session:
        def _request(method, url, *args, **kwargs):
            with session.request(method=method, url=url, cookies=cookies,
                                 headers={
                                     'user-agent': DEFAULT_USER_AGENT,
                                     'x-requested-with': 'XMLHttpRequest',
                                     'dnt': '1',
                                     'accept': '*/*',
                                     'sec-ch-ua-mobile': '?0',
                                     'sec-ch-ua-platform': 'Windows',
                                     'sec-fetch-site': 'same-origin',
                                     'sec-fetch-mode': 'cors',
                                     'sec-fetch-dest': 'empty',
                                     'referer': f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign',
                                     'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                                 }, *args, **kwargs) as r:
                r.raise_for_status()
                return r
        with _request(method='get', url=f'https://{SEHUATANG_HOST}/plugin.php?id=dd_sign&mod=sign') as r:
            id_hash_rsl = re.findall(
                r"updatesecqaa\('(.*?)'", r.text, re.MULTILINE | re.IGNORECASE)
            id_hash = id_hash_rsl[0] if id_hash_rsl else 'qS0'  # default value

            soup = BeautifulSoup(r.text, 'html.parser')
            formhash = soup.find('input', {'name': 'formhash'})['value']
            signtoken = soup.find('input', {'name': 'signtoken'})['value']
            action = soup.find('form', {'name': 'login'})['action']
        with _request(method='get', url=f'https://{SEHUATANG_HOST}/misc.php?mod=secqaa&action=update&idhash={id_hash}&{round(random.random(), 16)}') as r:
            qes_rsl = re.findall(r"'(.*?) = \?'", r.text,
                                 re.MULTILINE | re.IGNORECASE)
            if not qes_rsl or not qes_rsl[0]:
                raise Exception('invalid or empty question!')
            qes = qes_rsl[0]
            ans = eval(qes)
            assert type(ans) == int
        with _request(method='post', url=f'https://{SEHUATANG_HOST}/{action.lstrip("/")}&inajax=1',
                      data={'formhash': formhash,
                            'signtoken': signtoken,
                            'secqaahash': id_hash,
                            'secanswer': ans}) as r:
            return r.text

def retrieve_cookies_from_string(cookie_str: str) -> dict:
    cookies = {}
    for cookie in cookie_str.split(';'):
        name, value = cookie.strip().split('=', maxsplit=1)
        cookies[name] = value
    return cookies
  

def main(cookie):
    cookies = retrieve_cookies_from_string(cookie)
    try:
        raw_html = daysign(cookies=cookies)
        if raw_html is not None:
            if '签到成功' in raw_html:
                title, message_text = '98堂 每日签到', re.findall(
                    r"'(签到成功.+?)'", raw_html, re.MULTILINE)[0]
            elif '已经签到' in raw_html:
                title, message_text = '98堂 每日签到', re.findall(
                    r"'(已经签到.+?)'", raw_html, re.MULTILINE)[0]
            else:
                title, message_text = '98堂 签到异常', raw_html
        else:
            title, message_text = '98堂 签到异常', f'未获取到有效的 HTML 响应'
    except IndexError:
        title, message_text = '98堂 签到异常', f'正则匹配错误'
    except Exception as e:
        title, message_text = '98堂 签到异常', f'错误原因：{e}'
    
    return title, message_text


if __name__ == '__main__':
    cookies = user_cookie.split("&")
    msg = f"98堂签到共获取到{len(cookies)}个账号"
    print(msg)

    results = []  # 存储每个账号的签到结果

    for i, cookie in enumerate(cookies, start=1):
        title, message = main(cookie)
        results.append((title, message))

    # 汇总所有账号的签到结果并推送通知
    title = "98堂签到汇总"
    message = "\n".join([f"第 {i+1} 个账号. {title}: {message}" for i, (title, message) in enumerate(results)])
    print(message)
    send(title, message)
