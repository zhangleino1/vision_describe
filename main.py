from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
import cv2
import base64
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
import ollama
from datetime import datetime
from typing import List
import threading
import queue

app = FastAPI(title="视频识别服务")

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 全局变量
rtsp_url = "rtsp://admin:password@192.168.2.234:554/h264/ch1/main/av_stream"
connected_websockets: List[WebSocket] = []
frame_queue = queue.Queue(maxsize=10)
recognition_results = []
broadcast_queue = queue.Queue()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 如果连接已断开，从列表中移除
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

manager = ConnectionManager()

async def broadcast_worker():
    """后台任务：处理广播队列"""
    while True:
        try:
            # 从队列获取待广播的结果
            result = broadcast_queue.get(timeout=1)
            await manager.broadcast(json.dumps(result, ensure_ascii=False))
            broadcast_queue.task_done()
        except queue.Empty:
            # 队列为空时继续等待
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"广播出错: {e}")
            await asyncio.sleep(1)

def frame_to_base64(frame):
    """将视频帧转换为base64编码"""
    # 调整图像大小
    resized_frame = cv2.resize(frame, (640, 360))
    _, buffer = cv2.imencode('.jpg', resized_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str

def send_to_model(image_base64):
    """发送图像到大模型进行识别"""
    try:
        response = ollama.chat(
            model='qwen2.5vl:7b',
            messages=[{
                'role': 'user',
                'content': '详细描述这张图片中的内容',
                'images': [image_base64]
            }]
        )
          # 格式化结果
        created_at = response['created_at']
        try:
            # 尝试标准格式
            formatted_time = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # 处理更长的微秒格式，截取前6位微秒
                if '.' in created_at and created_at.endswith('Z'):
                    # 分割时间戳
                    main_part, microsec_part = created_at[:-1].split('.')
                    # 截取或填充微秒部分到6位
                    microsec_part = microsec_part[:6].ljust(6, '0')
                    # 重新组合时间戳
                    normalized_time = f"{main_part}.{microsec_part}Z"
                    formatted_time = datetime.strptime(normalized_time, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # 如果没有微秒部分，使用当前时间
                    formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                # 如果还是失败，使用当前时间
                formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = response['message']['content']
        
        result = {
            "time": formatted_time,
            "content": content
        }
        
        # 添加到结果列表
        recognition_results.append(result)
        if len(recognition_results) > 50:  # 保持最新50条记录
            recognition_results.pop(0)        # 广播结果到所有连接的WebSocket
        # 将结果放入广播队列，由后台任务处理
        broadcast_queue.put(result)
        
    except Exception as e:
        print(f"识别出错: {e}")

def generate_frames():
    """生成视频帧用于HTTP流"""
    while True:
        try:
            frame = frame_queue.get(timeout=1)
            # 调整帧大小用于Web显示
            frame = cv2.resize(frame, (640, 320))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except queue.Empty:
            # 如果队列为空，生成一个黑色帧
            black_frame = cv2.zeros((320, 640, 3), dtype=cv2.float32)
            cv2.putText(black_frame, 'Waiting for video stream...', (50, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', black_frame.astype('uint8'), [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue
        except Exception as e:
            print(f"生成帧出错: {e}")
            # 生成错误提示帧
            error_frame = cv2.zeros((320, 640, 3), dtype=cv2.float32)
            cv2.putText(error_frame, 'Video stream error', (150, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', error_frame.astype('uint8'), [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            break

def capture_rtsp_stream():
    """捕获RTSP视频流"""
    while True:  # 添加外层循环以支持重连
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        if not cap.isOpened():
            print("无法打开 RTSP 流，5秒后重试...")
            cv2.waitKey(5000)
            continue

        frame_skip = 10  # 跳帧参数
        frame_count = 0
        executor = ThreadPoolExecutor(max_workers=1)

        print("开始捕获视频流...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法读取视频帧，尝试重新连接...")
                break

            frame_count += 1
            if frame_count % frame_skip != 0:
                continue

            # 将帧放入队列用于Web流
            if not frame_queue.full():
                frame_queue.put(frame.copy())
            else:
                # 如果队列满了，清除旧帧
                try:
                    frame_queue.get_nowait()
                    frame_queue.put(frame.copy())
                except queue.Empty:
                    pass

            # 异步发送到大模型进行识别（每30帧识别一次）
            if frame_count % 30 == 0:
                image_base64 = frame_to_base64(frame)
                executor.submit(send_to_model, image_base64)

        cap.release()
        print("RTSP连接断开，5秒后重试...")
        cv2.waitKey(5000)

def generate_frames():
    """生成视频帧用于HTTP流"""
    while True:
        try:
            frame = frame_queue.get(timeout=1)
            # 调整帧大小用于Web显示
            frame = cv2.resize(frame, (640, 320))
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except queue.Empty:
            # 如果队列为空，生成一个黑色帧
            black_frame = cv2.zeros((320, 640, 3), dtype=cv2.float32)
            cv2.putText(black_frame, 'Waiting for video stream...', (50, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', black_frame.astype('uint8'), [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue
        except Exception as e:
            print(f"生成帧出错: {e}")
            # 生成错误提示帧
            error_frame = cv2.zeros((320, 640, 3), dtype=cv2.float32)
            cv2.putText(error_frame, 'Video stream error', (150, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            _, buffer = cv2.imencode('.jpg', error_frame.astype('uint8'), [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            break

@app.get("/")
async def index(request: Request):
    """主页面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
async def video_feed():
    """视频流端点"""
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点用于实时推送识别结果"""
    await manager.connect(websocket)
    
    # 发送历史记录
    for result in recognition_results[-10:]:  # 发送最近10条记录
        await websocket.send_text(json.dumps(result, ensure_ascii=False))
    
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """应用启动时开始视频捕获和广播任务"""
    # 在后台线程中启动视频捕获
    threading.Thread(target=capture_rtsp_stream, daemon=True).start()
    # 启动广播工作任务
    asyncio.create_task(broadcast_worker())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
