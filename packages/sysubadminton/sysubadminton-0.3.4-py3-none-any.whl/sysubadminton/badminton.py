#!/usr/bin/env python

import json
import configparser
import sys
import argparse
from json.decoder import JSONDecodeError
from itertools import groupby
from time import sleep
from datetime import datetime, timedelta, date, time
import requests
from bs4 import BeautifulSoup
from .version import __version__


class Badminton():
    """珠海校区羽毛球场预定脚本
    """

    def __init__(self, configpath, begin_time='00:01', max_times=10, token=''):
        self.session = requests.Session()
        self.headers = {
            "Origin": "https://gym.sysu.edu.cn",
            "Referer": "https://gym.sysu.edu.cn/order/show.html?id=161",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        }
        self.stocks, self.selects, self.results = [], [], []
        self.capt, self.imbyte = None, None
        self.max_times = max_times
        self.token = token

        try:
            conf_par = configparser.ConfigParser()
            conf_par.read(configpath, encoding='utf-8')
            conf = dict(conf_par['badminton'])
            self.first, self.stock_number = conf['first'], conf['stock_number']
            self.netid, self.password = conf['netid'], conf['password']
        except KeyError:
            print('检查配置文件是否存在且正确填写')
            sys.exit()
        if (self.netid == '') or (self.password == ''):
            print('填写 netid 和密码')
            sys.exit()

        try:
            self.stock_name = [int(i) for i in conf['stock_name'].split(',')]
            self.stock_time = [int(i) for i in conf['stock_time'].split(',')]
            self.stock_number = int(conf['stock_number'])
            if conf['stock_date'] == '':
                self.stock_date = date.today() + timedelta(days=2)
            else:
                self.stock_date = datetime.strptime(
                    conf['stock_date'], "%Y-%m-%d").date()
            # 预定日期前一天 00:00 可以预定，当天 22:00 后无法预定
            self.begin_time = datetime.strptime(begin_time, "%H:%M").time()
            self.begin_datetime = datetime.combine(self.stock_date,
                                                   self.begin_time) - timedelta(days=1)
            self.end_datetime = datetime.combine(self.stock_date, time(22, 0))
        except ValueError:
            print('检查配置文件填写是否正确')
            sys.exit()

        print(f'预定日期: {self.stock_date}')
        print(f"预定场次: {conf['stock_name']}\n预定时间: {conf['stock_time']}")
        print(f'每个时间段最大预定场地数: {self.stock_number}')


    def get_stocks(self):
        """获取指定日期可预定的场次列表
        """
        gym_url = 'https://gym.sysu.edu.cn/product/findOkArea.html'
        try_times = 0
        while try_times < self.max_times:
            try_times += 1
            r = requests.post(
                f'{gym_url}?s_date={self.stock_date}&serviceid=161')
            try:
                json_data = json.loads(r.text)
            except JSONDecodeError:
                print(f'获取场地信息失败，第 {try_times} 次重试')
                if r.status_code != 200:
                    print(f'状态码: {r.status_code}，服务器可能崩溃了，等待一分钟后重试')
                    sleep(60)
                    continue
                sleep(3)
                continue
            stocks = json_data['object']

            for stock in stocks:
                dic = {}
                if stock['status'] == 1:
                    for keys in ['id', 'stockid']:
                        dic[keys] = stock[keys]
                    for keys in ['price', 's_date']:
                        dic[keys] = stock['stock'][keys]
                    dic['sname'] = int(stock['sname'][2:])
                    dic['time_full'] = stock['stock']['time_no']
                    dic['time_no'] = int(dic['time_full'][:2])
                    self.stocks.append(dic)
            if len(self.stocks) == 0:
                print("凉了，没场地了，告辞")
                sys.exit()
            print(f'{self.stock_date} 共计 {len(self.stocks)} 个场地可以预订，开始按条件筛选')
            break
        print('获取场地信息失败，重试次数达到上限')
        sys.exit()


    def _select(self):
        """根据条件筛选场次
        """
        select = []
        for stock in self.stocks:
            if stock['sname'] in self.stock_name and stock['time_no'] in self.stock_time:
                select.append(stock)
        if len(select) == 0:
            print('没有满足条件的场地了')
            sys.exit()
        select.sort(key=lambda elem: (self.stock_time.index(elem['time_no']),
                                      self.stock_name.index(elem['sname'])))
        reselect = []
        for _, items in groupby(select,
                                key=lambda elem: self.stock_time.index(elem['time_no'])):
            i = 0
            for stock in items:
                reselect.append(stock)
                i += 1
                if i >= self.stock_number:
                    break
        self.selects = reselect
        if self.first == 'name':
            self.selects.sort(key=lambda elem: (self.stock_name.index(elem['sname']),
                                                self.stock_time.index(elem['time_no'])))
        print(f"共筛选出 {len(self.selects)} 个场地")
        for stock in self.selects:
            print(f"{stock['id']}  场地{stock['sname']}  {stock['time_full']}")


    def _recognize(self):
        """调用 http://fast.95man.com 在线识别验证码
        """
        headers = {'Connection': 'Keep-Alive',
                   'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)'}
        files = {'imgfile': ('captcha.jpg', self.imbyte)}
        recg_times = 0
        try:
            while recg_times < self.max_times:
                r = requests.post(f'http://api.95man.com:8888/api/Http/Recog?Taken={self.token}&imgtype=1&len=4',
                                files=files, headers=headers)
                arrstr = r.text.split('|')
                # 返回格式: 识别ID|识别结果|用户余额
                if int(arrstr[0]) > 0:
                    print(f'验证码识别成功: {arrstr[1]}')
                    self.capt = arrstr[1]
                    return True
                recg_times += 1
                print(f'识别失败: {arrstr[1]}，第 {recg_times} 次重试')
                sleep(1)
            raise Exception('识别失败，重试次数达到上限')

        except Exception as e:
            with open('capt.jpg', 'wb') as f:
                f.write(self.imbyte)
            self.capt = input('验证码识别失败，请手动打开 capt.jpg 识别后输入\n')


    def login(self):
        """登录
        """
        headers = {"User-Agent": self.headers['User-Agent']}
        login_url = "https://cas.sysu.edu.cn/cas/login"
        captcha_url = "https://cas.sysu.edu.cn/cas/captcha.jsp"
        self_url = "https://gym.sysu.edu.cn/yyuser/personal.html"
        login_form = {"username": "",
                      "password": "",
                      "captcha": "",
                      "_eventId": "submit",
                      "geolocation": "",
                      }
        login_times = 0

        while login_times < self.max_times:
            login_times += 1
            r = self.session.get(self_url, headers=headers)
            if '欢迎' in r.text:
                print('登录成功')
                return True

            self.imbyte = self.session.get(captcha_url).content
            self._recognize()
            login_form['captcha'] = self.capt

            r = self.session.get(login_url)
            soup = BeautifulSoup(r.text, features="html.parser")
            login_form['execution'] = soup.select(
                "input[name='execution']")[0]['value']
            login_form["username"] = self.netid
            login_form["password"] = self.password

            r = self.session.post(login_url, headers=headers, data=login_form)
            if 'success' in r.text:
                print('登录成功')
                r = self.session.get(self_url, headers=headers)
                return True
            if 'credential' in r.text:
                print('用户名或密码错误')
                sys.exit()

            print(f'验证码错误，第 {login_times} 次重试')
            sleep(1)

        print('登录重试次数太多，终止')
        sys.exit()


    def wait(self):
        """系统正常开启时间为 00:00-22:00，选择合适等待策略
        """
        now_time = datetime.now()

        if now_time > self.end_datetime:
            print(f'预订日期已经过去，你可以穿越回 {self.end_datetime} 之前，再见')
            sys.exit()

        if now_time > self.begin_datetime:
            if now_time.hour < 22:
                print(f'当前时间 {datetime.now()}，开始预订')
                return
            self.begin_datetime += timedelta(days=1)
            print('预订系统关闭，等到明天开始预定')

        print(f'未到可预订时间，等到 {self.begin_datetime} 开始预定')
        if (self.begin_datetime - datetime.now()).days > 0:
            print('!!!警告!!!')
            print('等待时间超过一天，建议等到明天再来预定!!!')
        print(f'{self.begin_datetime - datetime.now()} 后开始预订')
        sleep((self.begin_datetime - datetime.now()).seconds - 120)
        print('检查登录状态')
        if self.login():
            print(f'{self.begin_datetime - datetime.now()} 后开始预订')
            sleep((self.begin_datetime - datetime.now()).seconds - 3)
            return


    def book(self):
        """预订场地
        """
        stock_index = 0
        book_times = 0
        while len(self.results) < 2 and book_times < 10:
            book_times += 1
            try:
                stock = self.selects[stock_index]
            except IndexError:
                print('可以预定的都试过了')
                break
            param = ('{"activityPrice":0,"activityStr":null,"address":null,"dates":null,'
                     '"extend":null,"flag":"0","isbookall":"0","isfreeman":"0","istimes":"1",'
                     '"merccode":null,"order":null,"orderfrom":null,"remark":null,"serviceid":'
                     'null,"shoppingcart":"0","sno":null,"stock":{"%s":"1"},"stockdetail":'
                     '{"%s":"%s"},"stockdetailids":"%s","subscriber":"0",'
                     '"time_detailnames":null,"userBean":null}') \
                % (stock['stockid'], stock['stockid'], stock['id'], stock['id'])
            data = {"param": param, "json": "true"}
            r = self.session.post("https://gym.sysu.edu.cn/order/book.html",
                                  headers=self.headers, data=data)
            try:
                return_data = json.loads(r.text)
            except JSONDecodeError:
                print(f'预定失败，第 {book_times} 次重试')
                sleep(10)
                continue

            if return_data['result'] == '2':
                print(
                    f'场地{stock["sname"]} {stock["s_date"]} {stock["time_full"]} 预订成功，待支付')
                stock_index += 1
                self.results.append([return_data['object']['orderid'],
                                    stock["sname"], stock["s_date"], stock["time_no"]])

            elif return_data['message'] == 'USERNOTLOGINYET':
                print('JSESSIONID 过期了')
                self.login()
                continue

            elif '已被预定' in return_data['message']:
                stock_index += 1
                print('座位已被预定，尝试下一个')
                continue

            else:
                print(f'预定失败，第 {book_times} 次重试')
                sleep(10)
                continue

        if len(self.results) == 0:
            print('预定失败，重试次数过多，退出')
            sys.exit()
        print(f'预订成功 {len(self.results)} 个场地，1 分钟后自动支付订单')
        sleep(60)


    def pay(self):
        """支付订单
        """
        pay_times = 0
        while pay_times < self.max_times and len(self.results) != 0:
            pay_times += 1
            result = self.results[0]
            print('支付订单  ' + str(result[0]))
            data1 = {"orderid": result[0], "payid": 2}
            headers = self.headers
            headers['Referer'] = f'https://gym.sysu.edu.cn/pay/show.html?id={result[0]}'
            data2 = {'param': json.dumps(
                {"payid": 2, "orderid": str(result[0]), "ctypeindex": 0})}

            r = self.session.get("https://gym.sysu.edu.cn/pay/account/showpay.html",
                                 headers=headers, data=data1)
            r = self.session.post("https://gym.sysu.edu.cn/pay/account/topay.html",
                                  headers=headers, data=data2)
            try:
                return_data = json.loads(r.text)
            except JSONDecodeError:
                print(f'支付失败，第 {pay_times} 次重试')
                sleep(5)
                self.login()
                continue
            if return_data["result"] == "1":
                print(f'{str(result[0])} 支付成功')
                self.results.remove(result)
            else:
                print(f'支付结果: {return_data["message"]}，重试')
                sleep(5)

        if len(self.results) != 0:
            print('可能有未成功支付的订单，请手动支付')


    def run(self):
        self.login()
        self.wait()
        self.get_stocks()
        self._select()
        self.book()
        self.pay()
        sys.exit()


def main():
    parser = argparse.ArgumentParser(description='预定中山大学珠海校区羽毛球场地')
    parser.add_argument('config', type=str, help='配置文件路径')
    parser.add_argument('-b', '--begin', metavar='BEGIN TIME', type=str,
                        help='预定开始时间，如 00:05，默认 00:01', default='00:01')
    parser.add_argument('-m', '--maxtimes', type=int,
                        help='最大重试次数', default=10)
    parser.add_argument('-t', '--token', type=str,
                        help='验证码识别平台token', default='Hvfn8AbwxNTySxrnmTknA06onCdb')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}')
    par = parser.parse_args()
    badminton = Badminton(par.config, par.begin, par.maxtimes, par.token)
    badminton.run()
