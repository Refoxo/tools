# Please install google-api-python-client
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Auth:
    """
    将验证过程封装成对象，储存授权相关信息，并提供授权相应的功能
    """

    def __init__(self, scopes, name='sheet', client_secret_file="secret.json",
                 application_name="YoutubeUploader", app_version="v3",
                 service='sheets'):
        """
        参数：
        CLIENT_SECRETS_FILE 为 Google 后台下载的 Json 文件，默认为“secret.json”
        SCOPES 为授权范围，可在 Google 查询，默认为spreadsheets
        APPLICATIONS_NAME 是 Google 后台对应的 App 名称，默认为"YoutubeUploader"
        *YOUTUBE API_VERSION 用于建立 Flow，相对固定，目前是v3
        *SPREADSHEET API_VERSION 同上，目前是v4
        """

        self.NAME = name
        self.CLIENT_SECRETS_FILE = client_secret_file
        self.SCOPES = scopes
        self.APPLICATION_NAME = application_name
        self.SERVICE_NAME = service
        self.API_VERSION = app_version
        self.cwd = os.getcwd()
        self.credentials = self.get_saved_credentials()
        if not self.credentials:
            self.credentials = self.get_credential_via_oauth()

    def get_saved_credentials(self, filename="credentials.json"):
        """
            读取已有的 oatuh credential
        """
        file_data = {}
        filename = self.NAME + '_' + filename
        try:
            with open(filename, 'r') as file:
                file_data: dict = json.load(file)
        except FileNotFoundError:
            return None
        if (
                file_data
                and 'refresh_token' in file_data
                and 'client_id' in file_data
                and 'client_secret' in file_data):
            self.credentials = Credentials(**file_data)
            return Credentials(**file_data)
        return None

    def store_creds(self, credentials, filename="credentials.json"):
        """
        储存获取到的Credentials
        """
        filename = self.NAME + '_' + filename
        if not isinstance(credentials, Credentials):
            return
        file_data = {'refresh_token': credentials.refresh_token,
                     'token': credentials.token,
                     'client_id': credentials.client_id,
                     'client_secret': credentials.client_secret,
                     'token_uri': credentials.token_uri}
        with open(filename, 'w') as file:
            json.dump(file_data, file)
        print(f'Credentials serialized to {filename}.')

    def get_credential_via_oauth(self, filename='secret.json',
                                 save_data=True) -> Credentials:
        """本地没有Token的时候，去远程获取Token"""
        scopes = self.SCOPES
        iaflow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(
            filename, scopes)
        iaflow.run_local_server()
        if save_data:
            self.store_creds(iaflow.credentials)
        self.credentials = iaflow.credentials
        return iaflow.credentials

    def get_service(self, credentials=None, service='sheets', version='v4'):
        """
        :param credentials: 传入取到的Credentials obejct
        :param service: 服务名字，可以在 OAuth2 这个 Class 的变量里面找到
        :param version: 服务版本，可以在 OAuth2 这个 Class 的变量里面找到
        :return: 返回service，作用相当于API的session了。
        """
        if credentials is None:
            credentials = self.credentials
        service = build(service, version, credentials=credentials)
        return service
