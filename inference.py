import os
import shutil
import tempfile
import sys
sys.path.append('/root/autodl-tmp/TTS')

# 导入 FastAPI 和其他所需的模块
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

import torch
import datetime
from TTS.api import TTS

# 创建 FastAPI 实例
app = FastAPI()


# 获取设备（使用 GPU 或 CPU）
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 TTS（文本转语音）模型
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# 定义支持的语言列表
supported_languages = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"]

# 添加 CORS（跨域资源共享）中间件，以允许跨源请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 处理文本转语音的 API 端点，支持文件上传
@app.post('/tts')
async def tts_endpoint(
    text: str = Form(...),
    language: str = Form(...),
    speaker_wav: UploadFile = File(...),
    ):


    # 将上传的 WAV 文件保存到临时目录
    # 使用 Python 的 tempfile 模块创建一个临时文件，并保留在文件系统中（delete=False）
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        # 使用 shutil 模块的 copyfileobj 方法将上传的 WAV 文件内容复制到临时文件中
        shutil.copyfileobj(speaker_wav.file, tmp_file)
    
    # 获取临时文件的路径
    tmp_file_path = tmp_file.name

    # 执行文本转语音
    try:
        # 获取当前时间，精确到秒
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file_path = f"wav_file/{language}_output_{current_time}.wav"
        tts.tts_to_file(text=text, speaker_wav=tmp_file_path, language=language, file_path=output_file_path)
        
        # 将生成的 WAV 文件返回给前端
        return FileResponse(path=output_file_path, media_type="audio/wav", filename=f"{language}_output_{current_time}.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 删除临时的 WAV 文件
        os.remove(tmp_file_path)


# 新增路由以提供 HTML 文件
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = "templates/index.html"
    return FileResponse(html_path)
