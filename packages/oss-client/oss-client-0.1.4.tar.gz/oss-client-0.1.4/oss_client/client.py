import os
import oss2
import requests
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qiniu import Auth, put_data

from oss_client.fileobj import FileObject


class StorageClient(object):
    """基类"""
    kind = None

    def __init__(self):
        self.conn = None
        self.kind = None

    def read(self, key, range=None):
        raise NotImplementedError

    def write(self, file_obj: FileObject):
        raise NotImplementedError

    def __getattr__(self, name):
        return getattr(self.conn, name)


class FileClient(StorageClient):
    """本地文件存储"""
    kind = "file"

    def __init__(self, dir_path):
        self.dir_path = dir_path

    def read(self, key, range=None):
        with open(key, "rb") as f:
            return f.read()

    def write(self, file_obj: FileObject):
        path = os.path.join(self.dir_path, file_obj.name)
        with open(path, "wb") as f:
            f.write(file_obj.content)
        return path


class QiniuClient(StorageClient):
    """七牛对象存储"""
    kind = "qiniu"

    def __init__(self, url, access_key, secret_key, bucket):
        self.conn = Auth(access_key, secret_key)
        self.qiniu_url = url
        self.bucket = bucket
        self.put_data = put_data

    def get_url(self, key):
        pass

    def read(self, key, range=None):
        base_url = "http://{BUCKET_URL}/{KEY}".format(
            BUCKET_URL=self.bucket,
            KEY=key,
        )
        private_url = self.private_download_url(
            base_url,
            expires=10,
        )
        r = requests.get(private_url)
        if r.status_code != 200:
            raise Exception("获取七牛文件失败, status_code = {}".format(r.status_code))
        return r.content

    def write(self, file_obj: FileObject):
        token = self.upload_token(
            bucket=self.bucket,
            key=file_obj.key(),
            expires=10,
        )
        r, info = self.put_data(
            token=token,
            key=file_obj.key(),
            data=file_obj.read(),
        )
        return r["key"]


class TencentClient(StorageClient):
    """腾讯云对象存储"""
    kind = "tencent"

    def __init__(self, secret_id, secret_key, region, bucket):
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
        )
        self.conn = CosS3Client(config)
        self.bucket = bucket

    def get_url(self, key):
        pass

    def read(self, key, range=None):
        params = {
            "Bucket": self.bucket,
            "Key": key,
        }
        if range:
            params["Range"] = range
        r = self.conn.get_object(**params)
        return r["Body"].get_raw_stream().read()

    def write(self, file_obj: FileObject):
        r = self.conn.put_object(
            Bucket=self.bucket,
            Body=file_obj.obj.read(),
            Key=file_obj.key(),
        )
        return r["ETag"].replace('"', "")


class AliyunClient(StorageClient):
    """阿里云OSS"""
    kind = "aliyun"

    def __init__(self, access_key, secret_key, endpoint, bucket):
        self.endpoint = endpoint
        self.bucket = bucket
        self.auth = oss2.Auth(access_key, secret_key)
        self.conn = oss2.Bucket(self.auth, self.endpoint, self.bucket)

    def put_object(self, key, body):
        return self.conn.put_object(key=key, data=body)

    def get_object(self, key, range):
        return self.conn.get_object(key, byte_range=range)

    def get_url(self, key):
        return f"https://{self.bucket}.{self.endpoint}/{key}"

    def read(self, key, range=None):
        r = self.get_object(
            key=key,
            range=range,
        )
        return r.read()

    def write(self, file_obj: FileObject):
        r = self.put_object(
            key=file_obj.key(),
            body=file_obj.obj.read(),
        )
        return r.etag.lower()
