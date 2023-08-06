import requests
import json
from pprint import pprint
from math import radians, cos, sin, asin, sqrt

class geo_distance(object):
    '''地理距离对象'''
    def __init__(self):
        self.address1='1'
        self.address2='1'
        self.address='1'


    def set_address_double(self,address1,address2):
        '''写入两地点地址'''
        self.address1=address1
        self.address2=address2

    def get_address_double(self,op=0)->str:
        '''获取双地点时的地址，返回值：参数为0列表，1、2获取对应次序的地址'''
        if op==0:
            return [self.address1,self.address2]
        if op==1:
            return self.address1
        if op==2:
            return self.address2


    def set_address_single(self,address):
        '''写入单地点时的单个地点'''
        self.address=address

    def get_address_single(self)->str:
        '''获取单地点时的单个地址'''
        return self.address


    def haversine(self,lon1, lat1, lon2, lat2)->float: # 经度1，纬度1，经度2，纬度2 （十进制度数）
        """
        计算地球上两点之间的大圆距离（以十进制度数表示）
        """
        # 将十进制度数转化为弧度
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
        # haversine公式
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # 地球平均半径，单位为公里
        return c * r


    def get_location(self,address='紫荆山地铁站') ->str: 
        '''获取输入地址经纬度'''
        url = 'https://restapi.amap.com/v3/geocode/geo'       # 输入API问号前固定不变的部分
        params = {'key': 'ebd3186e4a94c201a954bcf7b3076e3e',                       # 注册高德地图，创建应用获得的key
                'address': address}                      # 将两个参数放入字典
        res = requests.get(url, params)
        # pprint(json.loads(res.text))
        results = json.loads(res.text)
        # 打印结果
        # results["geocodes"][0]["formatted_address"] + "：" + 

        self.set_address_single(results["geocodes"][0]["formatted_address"])
        return results["geocodes"][0]["location"]

        # ,results["geocodes"][0]["formatted_address"]


    def get_locationlist(self,location='113.681282,34.754929'):
        '''获取经纬度浮点型列表'''
        locationlist=location.split(',')
        locationlist[0]=float(locationlist[0])
        locationlist[1]=float(locationlist[1])
        return locationlist


    def get_distance(self,address1,address2,unit='里')->str:
        '''获取两地距离'''
        locationlist=self.get_locationlist(self.get_location(address1))
        lon1=locationlist[0]
        lat1=locationlist[1]
        self.address1=self.address
        locationlist=self.get_locationlist(self.get_location(address2))
        lon2=locationlist[0]
        lat2=locationlist[1]
        self.address2=self.address
        self.set_address_double(self.address1,self.address2)
        distance=self.haversine(lon1,lat1,lon2,lat2)
        if unit=='里':
            return str(distance*2)+'里'
        else:
            return str(distance)+'km'


if __name__=='__main__':
    dist=geo_distance()
    distance=dist.get_distance(address1='河南工业大学',address2='紫荆山地铁站',unit='里')
    print(dist.get_address_double(0))
    print(distance)