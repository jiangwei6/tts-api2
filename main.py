from flask import Flask, request, jsonify, send_file
import requests
import logging

app = Flask(__name__)

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 直接在代码中设置 subscription_key 和 region
subscription_key = "4a59d27f1fbd4fa69bf13b23cc01a6bc"
region = "eastus"

# 获取 Azure 语音服务的访问令牌
def get_token(subscription_key):
    try:
        fetch_token_url = f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        response = requests.post(fetch_token_url, headers=headers)
        response.raise_for_status()
        logger.info("Token obtained successfully")
        return response.text
    except Exception as e:
        logger.error(f"Error obtaining token: {e}", exc_info=True)
        raise

# 将文本转换为音频文件
def save_audio(ssml, subscription_key, output_file):
    try:
        logger.info(f"Starting sa
