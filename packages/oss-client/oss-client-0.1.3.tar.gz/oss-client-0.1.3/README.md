# oss-client
集成了阿里云OSS、腾讯云对象存储和七牛云对象存储，为不同的对象存储实现了统一的Client，方便使用

## Install
> pip install oss-client


## Tutorial
```
from oss_client import AliyunClient

client = AliyunClient(
    access_key=ALY_ACCESS_KEY_ID,
    secret_key=ALY_ACCESS_KEY_SECRET,
    endpoint=ALY_OSS_ENDPOINT,
    bucket=ALY_OSS_BUCKET,
)
```
