import os
import shutil
import tempfile

# 导入 FastAPI 和其他所需的模块
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

import torch
from TTS.api import TTS

# 创建 FastAPI 实例
app = FastAPI()


# 获取设备（使用 GPU 或 CPU）
device = "cuda" if torch.cuda.is_available() else "cpu"

# 初始化 TTS（文本转语音）模型
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

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
    wav_file: UploadFile = File(...),
    ):
    text = text
    language = language

    # 获取上传的 WAV 文件
    speaker_wav = wav_file

    # 检查指定的语言是否受支持
    if language not in supported_languages:
        raise HTTPException(status_code=400, detail="不支持的语言")

    # 将上传的 WAV 文件保存到临时目录
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        shutil.copyfileobj(speaker_wav.file, tmp_file)
        tmp_file_path = tmp_file.name

    # 执行文本转语音
    try:
        output_file_path = f"wav_file/{language}_output.wav"
        tts.tts_to_file(text=text, speaker_wav=tmp_file_path, language=language, file_path=output_file_path)
        
        # 将生成的 WAV 文件返回给前端
        return FileResponse(path=output_file_path, media_type="audio/wav", filename=f"{language}_output.wav")
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
