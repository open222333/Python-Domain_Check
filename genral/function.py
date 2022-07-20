import os
import cv2
import time
import base64
import hashlib
import requests
from datetime import datetime
from fake_useragent import UserAgent


class ICP():

    ua = UserAgent()
    
    def __init__(self) -> None:
        pass
    
    def get_icp_check_result(self, domain_name):
        cookie = self.get_cookies()
        info = {'pageNum': '', 'pageSize': '', 'unitName': domain_name}
        try:
            global base_header
            base_header = {
                # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32',
                'User-Agent': self.ua.random,
                'Origin': 'https://beian.miit.gov.cn',
                'Referer': 'https://beian.miit.gov.cn/',
                'Cookie': f'__jsluid_s={cookie}'
            }
            # -1代表失敗
            if cookie != -1:
                token = self.get_token()
                # print(token)
                if token != -1:
                    check_data = self.get_check_pic(token)
                    # print(check_data)
                    if check_data != -1:
                        sign = self.get_sign(check_data, token)
                        p_uuid = check_data['key']
                        if sign != -1:
                            domain_list = self.get_beian_info(info, p_uuid, token, sign)
                            return domain_list
                        else:
                            raise ValueError("取得sign錯誤")
                    else:
                        raise ValueError("計算圖片缺口位置錯誤")
                else:
                    raise ValueError("讀取token失敗")
            else:
                cookie = self.get_cookies()
                raise ValueError("取得cookie失敗")
        except Exception as e:
            print(f'{e}\n')

    def get_cookies(self):
        cookie_headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32'
            'User-Agent': self.ua.random
        }
        err_num = 0
        while err_num < 3:
            try:
                cookie = requests.utils.dict_from_cookiejar(requests.get('https://beian.miit.gov.cn/', headers=cookie_headers).cookies)['__jsluid_s']
                return cookie
            except:
                err_num += 1
                time.sleep(3)
        return -1

    def get_token(self):
        '''使用md5加密字符串"testtest"+timeStamp(當前時間戳)，獲取authKey'''
        timeStamp = round(time.time()*1000)
        authSecret = 'testtest' + str(timeStamp)
        authKey = hashlib.md5(authSecret.encode(encoding='UTF-8')).hexdigest()
        auth_data = {'authKey': authKey, 'timeStamp': timeStamp}
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/auth'
        try:
            t_response = requests.post(url=url, data=auth_data, headers=base_header).json()
            token = t_response['params']['bussiness']
        except:
            print(t_response)
            return -1
        return token

    def get_check_pic(self, token):
        '''取得驗證圖片'''
        url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/getCheckImage'
        base_header['Accept'] = 'application/json, text/plain, */*'
        base_header.update({'Content-Length': '0', 'token': token})
        try:
            p_request = requests.post(url=url, data='', headers=base_header).json()
            p_uuid = p_request['params']['uuid']
            big_image = p_request['params']['bigImage']
            small_image = p_request['params']['smallImage']
        except:
            return -1
        with open('bigImage.jpg', 'wb') as f:
            f.write(base64.b64decode(big_image))
        with open('smallImage.jpg', 'wb') as f:
            f.write(base64.b64decode(small_image))
        background_image = cv2.imread('bigImage.jpg', cv2.COLOR_GRAY2RGB)
        fill_image = cv2.imread('smallImage.jpg', cv2.COLOR_GRAY2RGB)
        position_match = cv2.matchTemplate(background_image, fill_image, cv2.TM_CCOEFF_NORMED)
        max_loc = cv2.minMaxLoc(position_match)[3][0]
        mouse_length = max_loc + 1
        os.remove('bigImage.jpg')
        os.remove('smallImage.jpg')
        check_data = {'key': p_uuid, 'value': mouse_length}
        return check_data

    def get_sign(self, check_data, token):
        check_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/image/checkImage'
        base_header.update({'Content-Length': '60', 'token': token, 'Content-Type': 'application/json'})
        try:
            pic_sign = requests.post(check_url, json=check_data, headers=base_header).json()
            sign = pic_sign['params']
        except:
            return -1
        return sign

    def get_beian_info(self, info_data, p_uuid, token, sign):
        '''取得備案資訊'''
        info_url = 'https://hlwicpfwc.miit.gov.cn/icpproject_query/api/icpAbbreviateInfo/queryByCondition'
        base_header.update({'Content-Length': '78', 'uuid': p_uuid, 'token': token, 'sign': sign})
        try:
            beian_info = requests.post(url=info_url, json=info_data, headers=base_header).json()
            # print(beian_info)
            info_list = beian_info['params']['list']
            if len(info_list) == 0:
                return None
        except:
            return info_list
        return info_list


def create_result(result):
    date = datetime.now().__format__('%Y-%M-%d')
    with open(f'icp_result_{date}', 'a') as f:
        f.write(f'{result}\n')
