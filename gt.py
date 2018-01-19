# -*- coding:utf-8 -*-  
import requests
import sys
import message
import json
import time
import re
import os
from PIL import Image

trainName = ['']
player = ''
trainDate = '' #'2018-02-17'
fromStationName = ''
toStationName = ''
#硬座 : '1', 一等 : 'M', 二等 : 'O',  硬卧 : '3', 软卧 : '4'         
chooseSeat = ['M','O']

seatChange = {'O':30, 'M':31, '1':29, '3':28, '4':23}
headers = {
    'Host': 'kyfw.12306.cn',
    'Origin' : 'https://kyfw.12306.cn',
    'X-Requested-With' : 'XMLHttpRequest',
    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer' : 'https://kyfw.12306.cn/otn/login/init',
    'Accept': '*/*',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-Language' : 'zh-CN,zh;q=0.8',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
}

def whileTrue(fn):
    def whileTruefun(*args):
        msg = args[1]
        errorTimes = args[2]
        err = 0
        while True:
            if err > errorTimes:
                print('%s' % msg)
                sys.exit()
            try:
                fn(*args)
                break
            except:
                #print(msg, err)
                time.sleep(0.1+errorTimes/10)
                err += 1
    return whileTruefun

@whileTrue
def downloadStations(*args):
    print('正在下载城市代码...')
    stationUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
    response = requests.get(stationUrl, headers = headers)
    pattern = re.compile('\'(.*?)\'')
    with open('stationCode.txt', 'w', encoding="utf-8") as f:
        f.write(pattern.findall(response.text)[0].lstrip('@'))
    print('城市代码下载完毕')

class Train(object):
    def __init__(self):
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        self.session = requests.session()
        self.session.headers = headers
        self.session.verify = False
        self.fromStationCode = ''
        self.toStationCode = ''
        self.fromStationTelecode = ''
        self.toStationTelecode = ''
        self.trainSecretStr = ''
        self.trainNo = ''
        self.trainCode = ''
        self.leftTicket = ''
        self.seatType = ''
        self.trainLocation = ''
        self.submitToken = ''
        self.passengerTicketStr = ''
        self.oldPassengerStr = ''
        self.orderId = ''
        self.getjsonurl = ''
        self.getjsonback = ''
        self.postdata = ''

    def getCoordinate(self):
        num = input('请输入图片序号:')
        coordinates = ['8,44','108,46','186,43','249,44','26,120','107,120','185,125','253,119']
        cList = list(map(lambda x : coordinates[int(x)-1] , num))
        return '|'.join(cList)

    @whileTrue
    def captchaCheck(self, *args):                  
        captchaRes = self.session.get(
            'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.46630622142659206')
        captcha = captchaRes.content
        with open('captcha.png', 'wb') as f:
            f.write(captcha)
        img=Image.open('captcha.png')
        img2=Image.open('1.png')
        img.paste(img2,(0,0),img2) 
        img.show()
        captchaStr = self.getCoordinate()
        print(captchaStr) 
        if os.path.exists('./captcha.png'): 
            os.remove('captcha.png')
        captchaStr = captchaStr.replace('|', ',')
        captchaStr = requests.utils.requote_uri(captchaStr)
        data = {
            'answer': captchaStr,
            'login_site' :'E',
            'rand': 'sjrand'
        }
        #验证验证码
        response = self.session.post('https://kyfw.12306.cn/passport/captcha/captcha-check', data = data)
        result = response.json()
        if result['result_code'] == '4':
            print('识别验证码成功')
        else:
            1/0

    @whileTrue
    def login(self, *args):
        # 1 伪装cookie++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        url = 'https://kyfw.12306.cn/otn/HttpZF/logdevice?algID=WYEdoc45yu&hashCode=EhTtj7Znzyie6I21jpgekYReLAnA8fyGEB4VlIGbF0g&FMQw=0&q4f3=zh-CN&VPIf=1&custID=133&VEek=unknown&dzuS=20.0%20r0&yD16=0&EOQP=895f3bf3ddaec0d22b6f7baca85603c4&lEnu=3232235778&jp76=e8eea307be405778bd87bbc8fa97b889&hAqN=Win32&platform=WEB&ks0Q=2955119c83077df58dd8bb7832898892&TeRS=728x1366&tOHY=24xx768x1366&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew={}&E3gR=abfdbb80598e02f8aa71b2b330daa098&timestamp={}'.format(
            self.session.headers['User-Agent'], str(round(time.time() * 1000)))
        response = self.session.get(requests.utils.requote_uri(url))
        pattern = re.compile('\(\'(.*?)\'\)')
        userVerify3 = eval(pattern.findall(response.text)[0])
        railExpiration = userVerify3['exp']
        railDeviceId = userVerify3['dfp']
        self.session.cookies['RAIL_EXPIRATION'] = railExpiration
        self.session.cookies['RAIL_DEVICEID'] = railDeviceId
        #2 做验证码验证++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.captchaCheck('验证码验证出错', 10)
        #3 用户名密码登陆++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        print('用户名密码登录')
        loginUrl = 'https://kyfw.12306.cn/passport/web/login'
        data = {
            'username': message.userName,
            'password': message.password,
            'appid' : 'otn'
        }

        self.postjson('登录出现错误，退出程序', 30, loginUrl, data)
        loginResult = self.getjsonback

        #response = self.session.post(loginUrl, data = data)
        #loginResult = response.json()
        if loginResult['result_code'] != 0:
            print('用户名密码错误(loginCheck) {}'.format(loginResult['result_code']))
            sys.exit()
        self.session.cookies['uamtk'] = loginResult['uamtk']
        #4 用户登录第一次验证+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        print('第一次验证')
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        data = {
            'appid': 'otn'
        }

        self.postjson('第一次验证出现错误，退出程序', 30, url, data)
        userVerify = self.getjsonback

        #response = self.session.post(url, data=data,)
        #userVerify = response.json()
        if userVerify['result_code'] != 0:
            print('验证失败(uamtk) code:{}'.format(userVerify['result_code']))
        #5 用户登录第二次验证++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        print('第二次验证')
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        newapptk = userVerify['newapptk']
        data = {
            'tk': newapptk
        }

        self.postjson('第二次验证出现错误，退出程序', 30, url, data)
        userVerify2 = self.getjsonback

        #response = self.session.post(url, data = data)    
        #userVerify2 = response.json()
        print('验证通过，用户为:{}'.format(userVerify2['username']))    

    @whileTrue
    def postjson(self, *args):
        url = args[2]
        data = args[3]
        response = self.session.post(url, data = data)
        self.getjsonback = response.json()

    @whileTrue
    def getjson(self, *args):
        response = self.session.get(self.getjsonurl)
        self.getjsonback = response.json()

    @whileTrue
    def findTicket(self, *args):
        retimes = -1
        queryUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            trainDate, self.fromStationCode, self.toStationCode)
        while True:
            self.getjsonurl = queryUrl
            self.getjson('查询出现错误，退出程序', 30)
            trainList = self.getjsonback['data']['result']
            trainDetailSplit = []
            for trainTemp in trainName:
                if trainDetailSplit == []:
                    for train in trainList:
                        trainDetailSplit = train.split('|')
                        if trainTemp == trainDetailSplit[3]:
                            for seat in chooseSeat:
                                if trainDetailSplit[seatChange[seat]] != '' and trainDetailSplit[seatChange[seat]] != u'无':
                                    self.seatType = seat
                                    break 
                            if self.seatType != '':
                                break
                            else:
                                trainDetailSplit = [] 
                        else:
                            trainDetailSplit = [] 
                else:
                    break
            if trainDetailSplit != []:
                self.trainSecretStr = trainDetailSplit[0]
                self.trainNo = trainDetailSplit[2]
                self.trainCode = trainDetailSplit[3]
                self.leftTicket = trainDetailSplit[12]
                self.fromStationTelecode = trainDetailSplit[6]
                self.toStationTelecode = trainDetailSplit[7]
                self.trainLocation = trainDetailSplit[15]
                print('name:%s,xz:%s,erdeng:%s,yideng:%s' % (trainDetailSplit[3],self.seatType,trainDetailSplit[30],trainDetailSplit[31]))
                return
            else:
                retimes += 1
                if retimes%120 == 0:
                    userCheckError = 0
                    while retimes > 1:
                        if userCheckError > 10:
                            print('用户登录检测失败，退出程序')
                            sys.exit()
                        url = 'https://kyfw.12306.cn/otn/login/checkUser'
                        try:
                            result = self.session.post(url).json()
                            if not result['data']['flag'] :
                                print('用户未登录checkUser')
                                userCheckError += 1
                                self.login()
                                continue
                            break
                        except:
                            time.sleep(1)
                            userCheckError += 1
                    print('刷新次数：%d' % retimes)
                time.sleep(1)


    def choosePassenger(self,message):
        passengerList = message['data']['normal_passengers']
        pessengerName = player
        pessengerDetail = dict()
        for p in passengerList:
            if pessengerName == p['passenger_name']:
                pessengerDetail = {
                    'passenger_flag' : p['passenger_flag'],
                    'passenger_type' : p['passenger_type'],
                    'passenger_name' : p['passenger_name'],
                    'passenger_id_type_code' : p['passenger_id_type_code'],
                    'passenger_id_no' : p['passenger_id_no'],
                    'mobile_no' : p['mobile_no']
                }
                return pessengerDetail

    @whileTrue
    def bookingTicket(self, *args):
        # 1 checkUser +++++++++++++++++++++++++++++++++++++++++++++
        self.session.headers['Referer'] = 'https://kyfw.12306.cn/otn/leftTicket/init'
        url = 'https://kyfw.12306.cn/otn/login/checkUser'
        result = self.session.post(url).json()
        print('验证登录状态checkUser')
        if not result['data']['flag'] :
            print('用户未登录checkUser')
            userCheckError += 1
            self.login()
        print('验证登录状态成功checkUser')

        # 2 submitOrderRequest+++++++++++++++++++++++++++++++++++++
        print('正在提交订单...')
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr':self.trainSecretStr,
            'train_date':trainDate,
            'back_train_date':time.strftime("%Y-%m-%d", time.localtime(time.time())),
            'tour_flag':'dc',  # dc 单程
            'purpose_codes':'ADULT',  # adult 成人票
            'query_from_station_name':fromStationName,
            'query_to_station_name':toStationName
        }
        data = str(data)[1:-1].replace(':','=').replace(',','&').replace(' ','').replace('\'','')
        data = requests.utils.requote_uri(data)
        
        self.postjson('提交订单出现错误，退出程序', 100, url, data)
        result = self.getjsonback
        
        print('submitOrderRequest+++++')
        print(result)
        if not result['status']:
            print('提交订单失败 status = {}'.format(result['status']))
            sys.exit()
        print('提交订单成功')

        # 3 initDC+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        data = '_json_att='
        pattern = re.compile('globalRepeatSubmitToken = \'(.*?)\'')
        pattern2 = re.compile("key_check_isChange':'(.*?)'")
        response = self.session.post(url, data = data)
        self.submitToken = pattern.findall(response.text)[0]
        self.keyCheckIsChange = pattern2.findall(response.text)[0]


        # 4 getPassengerDTOs++++++++++++++++++++++++++++++++++++++++++++++++++++++

        print('正在获取乘客信息')
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        data = {
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }

        self.postjson('正在获取乘客信息出现错误，退出程序', 100, url, data)
        result = self.getjsonback
        print('获取信息成功')
        pd = self.choosePassenger(result)
        #self.chooseSeat()

        # 5 checkOrderInfo++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        print('正在验证订单...')
        self.passengerTicketStr = self.seatType + ',' + pd['passenger_flag'] + ',' + pd['passenger_type'] + ',' + pd['passenger_name'] + ',' + pd['passenger_id_type_code'] + ',' + pd['passenger_id_no'] + ',' + pd['mobile_no'] + ',N'

        self.oldPassengerStr =  pd['passenger_name'] + ',' + pd['passenger_id_type_code'] + ',' + pd['passenger_id_no'] + ',' + pd['passenger_type'] + '_'

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        data = 'cancel_flag=2&bed_level_order_num=000000000000000000000000000000&passengerTicketStr={}&oldPassengerStr={}_&tour_flag=dc&randCode=&whatsSelect=1&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
            self.passengerTicketStr,self.oldPassengerStr,self.submitToken
        )
        data = requests.utils.requote_uri(data)
        self.postjson('验证订单失败，退出程序', 100, url, data)
        result = self.getjsonback


        # 6 getQueueCount+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        dateGMT = time.strftime('%a %b %d %Y %H:%M:%S  GMT+0800', time.strptime(trainDate, '%Y-%m-%d'))
        # data = 'train_date={}&train_no={}&stationTrainCode={}&seatType={}&fromStationTelecode={}&toStationTelecode={}&leftTicket={}&purpose_codes=00&train_location={}&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
        #     dateGMT,self.trainNo,self.trainCode,self.seatType,self.fromStationTelecode,self.toStationTelecode,self.leftTicket,self.trainLocation,self.submitToken
        # )
        data = {
            'train_date' : dateGMT,
            'train_no' : self.trainNo,
            'stationTrainCode' : self.trainCode,
            'seatType' : self.seatType,
            'fromStationTelecode' : self.fromStationTelecode,
            'toStationTelecode' : self.toStationTelecode,
            'leftTicket' : self.leftTicket,
            'purpose_codes' : '00',
            'train_location' : self.trainLocation,
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }
        self.postjson('getQueueCount有误，退出程序', 100, url, data)
        result = self.getjsonback

        # 7 confirmSingleForQueue++++++++++++++++++++++++++++++++++++++++++++++++++

        #https://kyfw.12306.cn/otn/confirmPassenger/confirmSingle
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        data = {
            'passengerTicketStr' : self.passengerTicketStr,
            'oldPassengerStr' : self.oldPassengerStr,
            'randCode' : '',
            'purpose_codes' : '00',
            'key_check_isChange' : self.keyCheckIsChange,
            'leftTicketStr' : self.leftTicket,
            'train_location' : self.trainLocation,
            'choose_seats' : '1F',
            'seatDetailType' : '000',
            'whatsSelect' : '1',
            'roomType' : '00',
            'dwAll' : 'N',
            '_json_att' : '',
            'REPEAT_SUBMIT_TOKEN' : self.submitToken
        }

        self.postjson('订票有误，退出程序', 10, url, data)
        result = self.getjsonback
        if not result['data']['submitStatus']:
            print('订票失败，退出程序')
            sys.exit()

        # 8 queryOrderWaitTime+++++++++++++++++++++++++++++++++++++++++
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(
            str(round(time.time() * 1000)),self.submitToken)


        self.getjsonurl = url
        self.getjson('queryOrderWaitTime错误，退出程序', 10)
        result = self.getjsonback
        resultCode = result['data']['waitTime']
        if resultCode == -1:
            self.orderId = result['data']['orderId']
            print('订单提交成功')
        elif resultCode == -2:
            print('取消次数过多，今日不能继续订票')
            sys.exit()
        else:
            print('订单提交结果：%s' % result)

        # 8 resultOrderForDcQueue+++++++++++++++++++++++++++++++++++++++++

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
        data = 'orderSequence_no={}&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format(self.orderId,self.submitToken)
        
        self.postjson('8订票有误，退出程序', 10, url, data)
        result = self.getjsonback
        if result['data']['submitStatus']:
            print('订票成功，请登录12306查看')
        else:
            print('查询订单有误,请登录12306查看具体订单情况')


if __name__ == "__main__":
    if os.path.exists('./stationCode.txt'):
        pass
    else:
        downloadStations('', '下载城市数据出错', 10)   
    t = Train()
    t.login('登录出错', 10)

    with open('stationCode.txt', 'r', encoding='utf-8') as f:
        stationsStr = f.read()
    stations = stationsStr.split('@')
    for s in stations:
        tempStationSplit = s.split('|')
        if tempStationSplit[1] == fromStationName:
            t.fromStationCode = tempStationSplit[2]
        elif tempStationSplit[1] == toStationName:
            t.toStationCode = tempStationSplit[2]
        else:
            pass
    t.findTicket('查询出错', 30)
    t.bookingTicket('提交订单出错', 20)
