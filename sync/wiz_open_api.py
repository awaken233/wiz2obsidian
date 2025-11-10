from log import log
import requests
import json
import ssl
import certifi
from websocket import create_connection

from sync.config import Config


class WizOpenApi:
    # account server
    AS_URL = 'https://as.wiz.cn'

    def __init__(self, config: Config):
        self.user_id = config.user_id
        self.password = config.password
        self.group_name = config.group_name
        self.token = ''
        # 知识库服务(knowledge base)
        self.kb_server = ''
        self.kb_guid = ''

        self.auth()

    def _login(self):
        login_url = f'{WizOpenApi.AS_URL}/as/user/login'
        response = requests.post(login_url, data={'userId': self.user_id, 'password': self.password})
        # 先判断http 状态码
        if response.status_code != 200:
            raise Exception(f'登录失败: http状态码为:{response.status_code}')

        # 判断业务状态码
        data = response.json()
        log.info(f'login 为知响应报文为:{json.dumps(data)}')
        if data['returnCode'] != 200:
            raise Exception(f'登录失败: 为知响应报文为:{data}')
        return data

    def get_group_list(self):
        """
        获取群组知识库列表
        """
        group_list_url = f'{WizOpenApi.AS_URL}/as/user/groups'
        response = requests.get(group_list_url, headers={'X-Wiz-Token': self.token})
        # 先判断http 状态码
        if response.status_code != 200:
            raise Exception(f'获取群组列表失败: http状态码为:{response.status_code}')

        # 判断业务状态码
        data = response.json()
        log.info(f'get_group_list 为知响应报文为:{json.dumps(data)}')
        if data['returnCode'] != 200:
            raise Exception(f'获取群组列表失败: 为知响应报文为:{data}')
        return data

    def auth(self):
        data = self._login()
        self.token = data['result']['token']
        self.kb_server = data['result']['kbServer']
        self.kb_guid = data['result']['kbGuid']
        self.user_guid = data['result']['userGuid']
        # 去除协议的域名 eg vipkshttps10.wiz.cn
        self.domain = self.kb_server.replace('https://', '')
        # 设置群组笔记配置
        self.set_group_config()


    def set_group_config(self):
        """
        如果配置文件中配置了 group_name & 不为空, 开始默认导出群组笔记
        """
        # 如果 self.group_name 直接return
        if self.group_name is None or self.group_name == '':
            return
        # 获取 get_group_list, 遍历列表是否等于配置的群组名称
        group_list_data = self.get_group_list()

        matching_group = next((group for group in group_list_data['result'] if group['name'] == self.group_name), None)

        if not matching_group:
            raise Exception(f'配置的群组名称:{self.group_name} 不存在, 请检查配置文件')

        # 存在, 重设相关参数
        self.kb_guid = matching_group['kbGuid']
        self.kb_server = matching_group['kbServer']
        self.domain = self.kb_server.replace('https://', '')


    def get_note_list(self, version, count):
        note_list_url = f'{self.kb_server}/ks/note/list/version/{self.kb_guid}'
        response = requests.get(note_list_url, params={'version': version, 'count': count}, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'获取笔记列表失败: http状态码为:{response.status_code}')
        data = response.json()
        if data['returnCode'] != 200:
            raise Exception(f'获取笔记列表失败: 为知响应报文为:{response.json()}')
        return data['result']

    def get_note_detail(self, doc_guid):
        note_download_url = f'{self.kb_server}/ks/note/download/{self.kb_guid}/{doc_guid}?downloadInfo=0&downloadData=1'
        response = requests.get(note_download_url, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'下载笔记失败: http状态码为:{response.status_code}')
        data = response.json()
        if data['returnCode'] != 200:
            raise Exception(f'下载笔记失败: 为知响应报文为:{response.json()}')
        return data

    def get_note_count(self):
        url = f'{self.kb_server}/ks/kb/info/{self.kb_guid}'
        response = requests.get(url, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'获取笔记总数失败: http状态码为:{response.status_code}')
        data = response.json()
        log.info(f'获取笔记总数 response: {json.dumps(data)}')

        if data['returnCode'] != 200:
            raise Exception(f'获取笔记总数失败: 为知响应报文为:{response.json()}')
        return data['result']['noteCount']

    # 获取协作笔记token
    def get_collaboration_token(self, doc_guid):
        url = f'{self.kb_server}/ks/note/{self.kb_guid}/{doc_guid}/tokens'
        response = requests.post(url, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'获取协作笔记token失败: http状态码为:{response.status_code}')
        data = response.json()
        if data['returnCode'] != 200:
            raise Exception(f'获取协作笔记token: 为知响应报文为:{response.json()}')
        return data['result']['editorToken']

    # 获取协作笔记图片
    def get_collaboration_image_byte(self, editor_token, doc_guid, image_name):
        url = f'{self.kb_server}/editor/{self.kb_guid}/{doc_guid}/resources/{image_name}'
        response = requests.get(url, headers={'cookie': f'x-live-editor-token={editor_token}', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        if response.status_code != 200:
            raise Exception(f'下载协作笔记图片失败: http状态码为:{response.status_code}')
        return response.content

    # 升级笔记
    def upgrade_note(self, doc_guid):
        detail_resp = self.get_note_detail(doc_guid)
        url = f'{self.kb_server}/ks/note/upload/{self.kb_guid}/{doc_guid}'
        payload = detail_resp['info']
        payload['collaborationStatus'] = 'normal'
        payload['status'] = 'localDataModified'
        payload['type'] = 'lite/markdown'
        log.info(f'升级笔记 payload: {json.dumps(payload)}')
        response = requests.post(url, headers={'X-Wiz-Token': self.token}, json=payload)
        if response.status_code != 200:
            raise Exception(f'升级笔记失败: http状态码为:{response.status_code}')
        data = response.json()
        log.info(f'升级笔记 response: {json.dumps(data)}')
        if data['returnCode'] != 200:
            raise Exception(f'升级笔记失败: 为知响应报文为:{response.json()}')
        return data

    # 获取协作笔记内容
    def get_collaboration_content(self, editor_token, doc_guid):
        wss_url = f"wss://{self.domain}/editor/{self.kb_guid}/{doc_guid}"

        hs_request = {
            "a": "hs",
            "id": None,
            "auth": {
                "appId": self.kb_guid,
                "docId": doc_guid,
                "userId": self.user_guid,
                "permission": "w",
                "token": editor_token
            }
        }

        f_request = {
            "a": "f",
            "c": self.kb_guid,
            "d": doc_guid,
            "v": None
        }

        s_request = {
            "a":"s",
            "c": self.kb_guid,
            "d": doc_guid,
            "v": None
        }


        """
        获取文档的data
        三次hs,一次f, 才可以获取data
        """
        ws = create_connection(
            wss_url,
            sslopt={
                'cert_reqs': ssl.CERT_REQUIRED,
                'ca_certs': certifi.where(),
            },
        )
        hs = json.dumps(hs_request)
        f = json.dumps(f_request)
        s = json.dumps(s_request)

        ws.send(hs)
        log.info(ws.recv())

        ws.send(hs)
        log.info(ws.recv())

        ws.send(hs)
        log.info(ws.recv())

        ws.send(f)
        log.info(ws.recv())
        content = ws.recv()
        log.info(content)

        ws.send(s)
        ws.recv()

        ws.close()
        return content

    def get_note_attachments(self, doc_guid):
        """
        获取笔记附件列表
        :param doc_guid: 笔记GUID
        :return: 附件列表数据
        """
        url = f'{self.kb_server}/ks/note/attachments/{self.kb_guid}/{doc_guid}'
        params = {
            'extra': '1',
            'clientType': 'web',
            'clientVersion': '4.0',
            'lang': 'zh-cn'
        }
        response = requests.get(url, params=params, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'获取笔记附件列表失败: http状态码为:{response.status_code}')
        data = response.json()
        if data['returnCode'] != 200:
            raise Exception(f'获取笔记附件列表失败: 为知响应报文为:{response.json()}')
        return data['result']

    def download_attachment(self, doc_guid, att_guid):
        """
        下载笔记附件
        :param doc_guid: 笔记GUID
        :param att_guid: 附件GUID
        :return: 附件的二进制内容
        """
        url = f'{self.kb_server}/ks/attachment/download/{self.kb_guid}/{doc_guid}/{att_guid}'
        params = {
            'clientType': 'web',
            'clientVersion': '4.0',
            'lang': 'zh-cn'
        }
        response = requests.get(url, params=params, headers={'X-Wiz-Token': self.token})
        if response.status_code != 200:
            raise Exception(f'下载附件失败: http状态码为:{response.status_code}')
        return response.content


