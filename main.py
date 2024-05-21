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
        logger.info(f"Starting save_audio with SSML: {ssml.strip()}")
        token = get_token(subscription_key)
        logger.info(f"Token: {token}")
        base_url = f"https://{region}.tts.speech.microsoft.com/"
        path = "cognitiveservices/v1"
        constructed_url = base_url + path
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mono-mp3',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': f'{region}.tts.speech.microsoft.com',
            'Connection': 'keep-alive'
        }

        logger.info(f"Constructed URL: {constructed_url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"SSML Body: {ssml.strip()}")
        response = requests.post(constructed_url, headers=headers, data=ssml.strip().encode('utf-8'))
        logger.info(f"Response Status Code: {response.status_code}")
        response.raise_for_status()
        with open(output_file, 'wb') as audio_file:
            audio_file.write(response.content)
        logger.info("Audio saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving audio: {e}", exc_info=True)
        return False

# 根路径路由
@app.route('/')
def index():
    return 'Hello, world2!'

# 生成音频文件的路由
@app.route('/generate_wav', methods=['POST'])
def generate_wav():
    logger.info("Received request to /generate_wav")
    try:
        data = request.json
        logger.info(f"Request data: {data}")
        text = data.get("text")
        voice_name = data.get("voice_name")
        language = data.get("language")

        ssml = f"""
<speak version="1.0" xml:lang="{language}">
    <voice xml:lang="{language}" name="{voice_name}">
        {text}
    </voice>
</speak>
"""
        output_file = "output.mp3"
        if save_audio(ssml, subscription_key, output_file):
            logger.info("Audio file created successfully")
            return send_file(output_file, mimetype='audio/mp3')
        else:
            logger.error("Failed to generate audio in save_audio function")
            return jsonify({"error": "Failed to generate audio"}), 500
    except Exception as e:
        logger.error(f"Error in generate_wav: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
