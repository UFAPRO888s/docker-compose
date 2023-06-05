import numpy as np
import cv2
import os
from fastapi import FastAPI, Request, HTTPException, File,Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse,StreamingResponse
from pydantic import BaseModel
import json
import jinja2
import base64
import io
from PIL import Image
from model.model_loader import Yolo7
import uuid
from typing import Any, Dict, AnyStr, List, Union


class Imgfile(BaseModel):
    file: bytes = File()
class Json(BaseModel):
    res: Union[List[Any], Dict[AnyStr, Any]]
# Initialize the Flask application
#app = Flask(__name__)
app = FastAPI(openapi_url=None)
app.mount('/imgstore', StaticFiles(directory='./imgstore'), name='imgstore')
app.mount('/static', StaticFiles(directory='./server/static'), name='static')

Yolo7.print_color_pair

templates = Jinja2Templates(directory='./server')
templates.env.globals["urlpath"] = app.url_path_for
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
templates.env.autoescape = False

templates.env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

# route http posts to this method


@app.post('/api/yolo7/')
async def yolo7(file: bytes = File()):
    image_stream = io.BytesIO(file)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    res = Yolo7().get_predection(image)
    json_compatible_item_data = jsonable_encoder(res)
    return JSONResponse(content=json_compatible_item_data)

@app.post('/api/drawn_detection/')
async def draw7(file: bytes = File(), token: str = Form()):
    image_stream = io.BytesIO(file)
    file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    res_content=json.loads(str(token))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output_img= Yolo7().draw_result(image,res_content)
    retval, buffer = cv2.imencode('.jpg', output_img)
    return StreamingResponse(
    io.BytesIO(buffer),
    media_type='image/jpeg')


@app.get('/')
async def index(request: Request):
	return templates.TemplateResponse('api.pug', {'request': request,})


if __name__ == '__main__':
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description='API server')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', default='')
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
