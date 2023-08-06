import requests
import base64

err_code={
    1	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
    2	:'服务暂不可用,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
    3	:'调用的API不存在,请检查请求URL后重新尝试,一般为URL中有非英文字符,如“-”,可手动输入重试',
    4	:'集群超限额,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
    6	:'无权限访问该用户数据,创建应用时未勾选相关接口,请登录百度云控制台,找到对应的应用,编辑应用,勾选上相关接口,然后重试调用',
    13	:'获取token失败',
    14	:'IAM鉴权失败',
    15	:'应用不存在或者创建失败',
    17	:'每天请求量超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
    18	:'QPS超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
    19	:'请求总量超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
    100	:'无效的access_token参数,token拉取失败,可以参考“Access Token获取”重新获取',
    110	:'access_token无效,token有效期为30天,注意需要定期更换,也可以每次请求都拉取新token',
    111	:'access_token无效,token有效期为30天,注意需要定期更换,也可以每次请求都拉取新token',
    216100	:'请求中包含非法参数,请检查后重新尝试',
    216101	:'缺少必须的参数,请检查参数是否有遗漏',
    216102	:'请求了不支持的服务,请检查调用的url',
    216103	:'请求中某些参数过长,请检查后重新尝试',
    216110	:'appid不存在,请重新核对信息是否为后台应用列表中的appid',
    216200	:'图片为空,请检查后重新尝试',
    216201	:'上传的图片格式错误,现阶段我们支持的图片格式为：PNG、JPG、JPEG、BMP,请进行转码或更换图片',
    216202	:'上传的图片大小错误,现阶段我们支持的图片大小为：base64编码后小于4M,分辨率不高于4096*4096,请重新上传图片',
    216203	:'自定义菜品识别服务错误码：上传的图片中包含多个主体,请上传只包含一个主体的菜品图片入库',
    216204	:'logo识别服务错误码：后端服务超时,请工单联系技术支持团队',
    216630	:'识别错误,请再次请求,如果持续出现此类错误,请提交工单联系技术支持团队',
    216634	:'检测错误,请再次请求,如果持续出现此类错误,请提交工单联系技术支持团队',
    216681	:'添加入库的图片已经在库里,完全相同（Base64编码相同）的图片不能重复入库',
    282000	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
    282003	:'请求参数缺失',
    282005	:'处理批量任务时发生部分或全部错误,请根据具体错误码排查',
    282006	:'批量任务处理数量超出限制,请将任务数量减少到10或10以下',
    282100	:'图片压缩转码错误',
    282101	:'长图片切分数量超限',
    282102	:'未检测到图片中识别目标',
    282103	:'图片目标识别错误',
    282110	:'URL参数不存在,请核对URL后再次提交',
    282111	:'URL格式非法,请检查url格式是否符合相应接口的入参要求',
    282112	:'url下载超时,请检查url对应的图床/图片无法下载或链路状况不好,您可以重新尝试一下,如果多次尝试后仍不行,建议更换图片地址',
    282113	:'URL返回无效参数',
    282114	:'URL长度超过1024字节或为0',
    282808	:'request id 不存在',
    282809	:'返回结果请求错误（不属于excel或json）',
    282810	:'图像识别错误',
    283300	:'入参格式有误,可检查下图片编码、代码格式是否有误',
    336000	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
    336001	:'入参格式有误,比如缺少必要参数、图片base64编码错误等等,可检查下图片编码、代码格式是否有误。有疑问请提交工单联系技术支持团队',
}

class imageAI():
    def __init__(self,APIKey,SecretKey) -> None:
        self.apikey=APIKey
        self.secretkey=SecretKey
        self.data=''
        self.err_code={
            1	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
            2	:'服务暂不可用,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
            3	:'调用的API不存在,请检查请求URL后重新尝试,一般为URL中有非英文字符,如“-”,可手动输入重试',
            4	:'集群超限额,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
            6	:'无权限访问该用户数据,创建应用时未勾选相关接口,请登录百度云控制台,找到对应的应用,编辑应用,勾选上相关接口,然后重试调用',
            13	:'获取token失败',
            14	:'IAM鉴权失败',
            15	:'应用不存在或者创建失败',
            17	:'每天请求量超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
            18	:'QPS超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
            19	:'请求总量超限额,已上线计费的接口,请直接在控制台开通计费,调用量不受限制,按调用量阶梯计费；未上线计费的接口,请提交工单联系申请提额',
            100	:'无效的access_token参数,token拉取失败,可以参考“Access Token获取”重新获取',
            110	:'access_token无效,token有效期为30天,注意需要定期更换,也可以每次请求都拉取新token',
            111	:'access_token无效,token有效期为30天,注意需要定期更换,也可以每次请求都拉取新token',
            216100	:'请求中包含非法参数,请检查后重新尝试',
            216101	:'缺少必须的参数,请检查参数是否有遗漏',
            216102	:'请求了不支持的服务,请检查调用的url',
            216103	:'请求中某些参数过长,请检查后重新尝试',
            216110	:'appid不存在,请重新核对信息是否为后台应用列表中的appid',
            216200	:'图片为空,请检查后重新尝试',
            216201	:'上传的图片格式错误,现阶段我们支持的图片格式为：PNG、JPG、JPEG、BMP,请进行转码或更换图片',
            216202	:'上传的图片大小错误,现阶段我们支持的图片大小为：base64编码后小于4M,分辨率不高于4096*4096,请重新上传图片',
            216203	:'自定义菜品识别服务错误码：上传的图片中包含多个主体,请上传只包含一个主体的菜品图片入库',
            216204	:'logo识别服务错误码：后端服务超时,请工单联系技术支持团队',
            216630	:'识别错误,请再次请求,如果持续出现此类错误,请提交工单联系技术支持团队',
            216634	:'检测错误,请再次请求,如果持续出现此类错误,请提交工单联系技术支持团队',
            216681	:'添加入库的图片已经在库里,完全相同（Base64编码相同）的图片不能重复入库',
            282000	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
            282003	:'请求参数缺失',
            282005	:'处理批量任务时发生部分或全部错误,请根据具体错误码排查',
            282006	:'批量任务处理数量超出限制,请将任务数量减少到10或10以下',
            282100	:'图片压缩转码错误',
            282101	:'长图片切分数量超限',
            282102	:'未检测到图片中识别目标',
            282103	:'图片目标识别错误',
            282110	:'URL参数不存在,请核对URL后再次提交',
            282111	:'URL格式非法,请检查url格式是否符合相应接口的入参要求',
            282112	:'url下载超时,请检查url对应的图床/图片无法下载或链路状况不好,您可以重新尝试一下,如果多次尝试后仍不行,建议更换图片地址',
            282113	:'URL返回无效参数',
            282114	:'URL长度超过1024字节或为0',
            282808	:'request id 不存在',
            282809	:'返回结果请求错误（不属于excel或json）',
            282810	:'图像识别错误',
            283300	:'入参格式有误,可检查下图片编码、代码格式是否有误',
            336000	:'服务器内部错误,请再次请求, 如果持续出现此类错误,请提交工单联系技术支持团队',
            336001	:'入参格式有误,比如缺少必要参数、图片base64编码错误等等,可检查下图片编码、代码格式是否有误。有疑问请提交工单联系技术支持团队',
        }
    
    def access_token(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+self.apikey+'&client_secret='+self.secretkey
        response = requests.get(host)
        if response:
            return {'msg':'ok','data':response.json()['access_token']}
        else:
            return {'msg':'err','data':'Failed to get access token'}

    def result(self,pop):
        if self.data['msg']==True:
            return self.data['data'][pop]
        else:
            return self.data['data']

    def animal(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/animal"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result'][0]['name']
                    self.score=response.json()['result'][0]['score']
                    self.data={'msg':True,'data':(self.name,self.score)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}
                    
    def plant(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/plant"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result'][0]['name']
                    self.score=response.json()['result'][0]['score']
                    self.data={'msg':True,'data':(self.name,self.score)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}
            
    def ingredient(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/classify/ingredient"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result'][0]['name']
                    self.score=response.json()['result'][0]['score']
                    self.data={'msg':True,'data':(self.name,self.score)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}

    def dish(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result'][0]['name']
                    self.probability=response.json()['result'][0]['probability']
                    self.data={'msg':True,'data':(self.name,self.probability)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}

    def currency(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/currency"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result']['currencyName']
                    if response.json()['result']['hasdetail']==1:
                        self.currencyDenomination=response.json()['result']['currencyDenomination']
                    else:
                        self.currencyDenomination='无法识别'
                    self.data={'msg':True,'data':(self.name,self.currencyDenomination)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}
    
    def landmark(self,img_url,):
        self.ak=self.access_token()
        if self.ak['msg']=='err':
            return {'msg':'err','data':'Failed to get access token'}
        else:
            request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/landmark"
            f = open(img_url, 'rb')
            img = base64.b64encode(f.read())
            params = {"image":img}
            request_url = request_url + "?access_token=" + self.ak['data']
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            if response:
                print(response.json())
                try:
                    self.name=response.json()['result']['landmark']
                    self.data={'msg':True,'data':(self.name,100)}
                except:
                    code=response.json()['error_code']
                    err_msg=response.json()['error_msg']
                    self.data={'msg':False,'data':'错误码：'+str(code)+'  '+err_msg+'  '+err_code[code]}

