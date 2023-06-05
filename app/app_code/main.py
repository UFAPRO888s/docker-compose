from requests import session
from pylint_errors.pylint_errors import pylint_dict_final
from typing import Any
from typing import AnyStr
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Union
from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Cookie
from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
# from fastapi_socketio import SocketManager
from pydantic import BaseModel
import time
import sys
from pathlib import Path
import filetype
import secrets
import numpy as np
import cv2
import os
import json
import jinja2
import base64
import io
import uuid
import tempfile
import mmap
import re
import shutil
from PIL import Image
from datetime import datetime
from datetime import timezone
from datetime import timedelta
from pylint import epylint as lint
from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Pool, cpu_count
from model.model_loader import Yolo7


class Code(BaseModel):
    text: str

class TxtFile(BaseModel):
    filename: str
    text: str

class Imgfile(BaseModel):
    file: bytes = File()

class Json(BaseModel):
    res: Union[List[Any], Dict[AnyStr, Any]]

Yolo7.print_color_pair

app = FastAPI(openapi_url=None)

app.mount('/imgstore', StaticFiles(directory='./imgstore'), name='imgstore')
app.mount('/static/fonts', StaticFiles(directory='./server/static/fonts'), name='font1')
app.mount('/static/fonts', StaticFiles(directory='./server/static/fonts'), name='font2')
app.mount('/static', StaticFiles(directory='./server/static'), name='static')
#app.mount('/streaming', StaticFiles(directory='/streaming'), name='streaming')

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
}

templates = Jinja2Templates(directory='./server')
templates.env.globals["urlpath"] = app.url_path_for
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
templates.env.autoescape = False
templates.env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

num_cores = cpu_count()
session={"busy":False,"eval_busy":False,"sched_busy":False}


my_env = os.environ
my_env["PYTHONUNBUFFERED"] = "1"


rootDirectory = Path("../user_code")
currentDirectory=Path('.')
currentFile=Path()
homeDirectory=Path('.')
default_view = 0
tp_dict = {'image': [['.png', ".jpg", '.svg',".jpeg"], 'image-icon.svg'],
           'audio': [['.mp3', '.wav', ".ogg", ".mpeg", ".aac", ".3gpp", ".3gpp2", ".aiff", ".x-aiff", ".amr", ".mpga"], 'audio-icon.svg'], 
           'video': [['.mp4', '.flv', ".webm", ".opgg"], 'video-icon.svg'],
           "pdf": [['.pdf'], 'pdf-icon.svg'],
           "word": [['.docx', '.doc'], 'doc-icon.svg'],
           "txt": [['.txt'], 'txt-icon.svg'],
           "compressed":[[".zip", ".rar"], 'compressed-icon.svg'],
           "code": [['.css', '.scss', '.html', '.py', '.js', '.cpp'], 'code-icon.svg']
           }

supported_formats=sum([tp_dict[type][0] for type in tp_dict],[])
maxNameLength = 15
osWindows = False  # Not Windows
if 'win32' in sys.platform or 'win64' in sys.platform:
    osWindows = True
try:
    with open('hidden.txt','r') as f:
        fileText=f.read()
        fileText = fileText.split('\n').copy()
except:
    fileText=[]
hiddenList = list(fileText)



def is_video(filepath):
    exts = tuple(tp_dict['video'][0])
    if(filepath.lower().endswith(exts)):
        return "video/"+os.path.splitext(filepath)[-1].lstrip(".")
    else:
        return False
def is_audio(filepath):
    exts = tuple(tp_dict['audio'][0])
    if(filepath.lower().endswith(exts)):
        return "audio/"+os.path.splitext(filepath)[-1].lstrip(".")
    else:
        return False
def is_code(filepath):
    exts = tuple(tp_dict['code'][0])
    if(filepath.lower().endswith(exts)):
        return "application/"+os.path.splitext(filepath)[-1].lstrip(".")
    else:
        return False
def is_image(filepath):
    exts = tuple(tp_dict['image'][0])
    if(filepath.lower().endswith(exts)):
        return "image/"+os.path.splitext(filepath)[-1].lstrip(".")
    else:
        return False
def is_compressed(filepath):
    exts = tuple(tp_dict['compressed'][0])
    if(filepath.lower().endswith(exts)):
        return "application/"+os.path.splitext(filepath)[-1].lstrip(".")
    else:
        return False
def get_size(folder: str) -> int:
    return sum(p.stat().st_size for p in Path(folder).rglob('*'))
def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
def get_file_extension(fname):
    found_extension = re.search("\.[A-Za-z0-9]*$", fname, re.IGNORECASE)
    if found_extension:
        return found_extension[0][1:].lower()
def DirList(path):
    dList = [x for x in path.iterdir() if Path(path/x).is_dir()]
    finalList = list(set(dList)-set(hiddenList))
    return(finalList)
def FileList(path):
    dList = [x for x in path.iterdir() if Path(path/x).is_file()]
    finalList = list(set(dList)-set(hiddenList))
    return(finalList)
def getDirList(path):
    relpath=path
    path=Path(rootDirectory/path).resolve()
    print(relpath)
    print(path)
    global maxNameLength, tp_dict, hostname
    dList = DirList(path)
    fList = FileList(path)

    
    dir_list_dict = {}
    file_list_dict = {}

    for i in dList:
        image = 'folder.svg'
        if len(str(i.name)) > maxNameLength:
            dots = "..."
        else:
            dots = ""
        dir_stats = i.stat()
        dir_list_dict[i] = {}
        dir_list_dict[i]['f'] = str(i.name)[0:maxNameLength]+dots
        dir_list_dict[i]['f_url'] = re.sub("#", "|HASHTAG|", str(i.name))
        dir_list_dict[i]['currentDir'] = relpath
        dir_list_dict[i]['f_complete'] = str(i.name)
        dir_list_dict[i]['image'] = image
        dir_list_dict[i]['dtc'] = datetime.fromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        dir_list_dict[i]['dtm'] = datetime.fromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        dir_list_dict[i]['size'] = convert_bytes(get_size(i))

    for i in fList:
        image = None
        try:
            tp = i.suffix
            for file_type in tp_dict.values():
                if tp in file_type[0]:
                    image = "files_icon/"+file_type[1]
                    break
            tp = "" if not tp else tp
        except:
            pass
        if not image:
            image = 'files_icon/unknown-icon.png'
        if len(str(i.name)) > maxNameLength:
            dots = "..."
        else:
            dots = ""
        file_list_dict[i] = {}
        file_list_dict[i]['f'] = str(i.name)[0:maxNameLength]+dots
        file_list_dict[i]['f_url'] = re.sub("#", "|HASHTAG|",str(i.name))
        file_list_dict[i]['currentDir'] = relpath
        file_list_dict[i]['f_complete'] = str(i.name)
        file_list_dict[i]['image'] = image
        file_list_dict[i]['supported'] = True if tp.lower() in supported_formats else False
        try:
            dir_stats = i.stat()
        except:
            print("unable to find stat;",i.absolute().resolve())
        file_list_dict[i]['dtc'] = datetime.fromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        file_list_dict[i]['dtm'] = datetime.fromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        file_list_dict[i]['size'] = convert_bytes(os.path.getsize(i.absolute().resolve()))
        
    return dir_list_dict, file_list_dict


@app.middleware("http")
async def after_request(request: Request, call_next):

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["Accept-Ranges"] = "bytes"
    return response
 ######################################### api ###################################
# @app.post('/api/yolo7/')
# async def yolo7(file: bytes = File()):
#     image_stream = io.BytesIO(file)
#     file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
#     image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     res = Yolo7().get_predection(image)
#     json_compatible_item_data = jsonable_encoder(res)
#     return JSONResponse(content=json_compatible_item_data)

# @app.post('/api/drawn_detection/')
# async def draw7(file: UploadFile = File(...), token: str = Form()):
#     img_content = await file.read() 
#     print(token)
#     res_content=json.loads(str(token))
#     image_stream = io.BytesIO(img_content)
#     file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
#     image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     output_img= Yolo7().draw_result(image,res_content)

#     retval, buffer = cv2.imencode('.jpg', output_img)
#     return StreamingResponse(
#     io.BytesIO(buffer),
#     media_type='image/jpeg')

# @app.get('/api')
# async def api(request: Request):
# 	return templates.TemplateResponse('api.pug', {'request': request,})
############################ login ###############
def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
############################ change view ############################
@app.get('/changeView')
async def changeView(view:int=0):
    global default_view
    print('view received',view)
    v=(view)
    if v in [0, 1]:
        default_view = v
    else:
        default_view = 0

    json_compatible_item_data = jsonable_encoder({
        "txt": default_view,
    })
    return JSONResponse(content=json_compatible_item_data)

@app.get('/explorer')
async def filePage(request: Request):
    global currentDirectory,homeDirectory

    dir_dict, file_dict = getDirList(currentDirectory)
    if default_view == 0:
        var1, var2 = "DISABLED", ""
        default_view_css_1, default_view_css_2 = '', 'style=display:none'
    else:
        var1, var2 = "", "DISABLED"
        default_view_css_1, default_view_css_2 = 'style=display:none', ''
    ishome=currentDirectory==homeDirectory
    return templates.TemplateResponse("explorer.html", {"request": request,"ishome":ishome,'currentDir':os.path.basename(currentDirectory),  'default_view_css_1':default_view_css_1, 'default_view_css_2':default_view_css_2, 'view0_button':var1, 'view1_button':var2, 'currentDir_path':currentDirectory, 'dir_dict':dir_dict, 'file_dict':file_dict})
@app.get('/explorer/{var}')
async def filePage(request: Request,var=''):
    global currentDirectory,homeDirectory,rootDirectory
    print("curr:",currentDirectory)
    print("var:",var)
    if var == '' or var == '.':
        relPath=homeDirectory
    elif var == "<..>":
        if currentDirectory != homeDirectory:
            relPath=Path(currentDirectory).parent
        else:
            relPath=homeDirectory
    else:        
        relPath=Path(currentDirectory/var)
    checkingPath=Path(rootDirectory / relPath)
    print("checkingPath:",checkingPath)
    if(os.path.exists(checkingPath)):
        if(os.path.isdir(checkingPath)):
            currentDirectory=relPath
        else:
            print("Directory Doesn't Exist")
            raise HTTPException(status_code=300, detail="Invalid Directory Path")
    else:
        #Invalid Directory
        print("Path Doesn't Exist")
        raise HTTPException(status_code=404, detail="Invalid Path")
    dir_dict, file_dict = getDirList(currentDirectory)
    if default_view == 0:
        var1, var2 = "DISABLED", ""
        default_view_css_1, default_view_css_2 = '', 'style=display:none'
    else:
        var1, var2 = "", "DISABLED"
        default_view_css_1, default_view_css_2 = 'style=display:none', ''

    ishome=currentDirectory==homeDirectory
    return templates.TemplateResponse("explorer.html", {"request": request,"ishome":ishome,'currentDir':os.path.basename(currentDirectory),  'default_view_css_1':default_view_css_1, 'default_view_css_2':default_view_css_2, 'view0_button':var1, 'view1_button':var2, 'currentDir_path':currentDirectory, 'dir_dict':dir_dict, 'file_dict':file_dict})

@app.get('/controller')
async def controller(request: Request):
    return templates.TemplateResponse("controller.html", {"request": request,})

@app.get('/')
async def homePage(request: Request):
    global currentDirectory, osWindows,homeDirectory
    currentDirectory=homeDirectory
    response = RedirectResponse(url='/explorer/'+str(currentDirectory))
    return response
@app.get("/open/{var}")
async def openner(var:str):
    if is_code(var):
        response = RedirectResponse(url='/blockpy/'+var)
    elif is_audio(var):
        response = RedirectResponse(url='/audio_player/'+var)
    elif is_video(var):
        response = RedirectResponse(url='/video_player/'+var)
    elif is_image(var):
        response = RedirectResponse(url='/image_viewer/'+var)
    else:
        response = RedirectResponse(url='/download/'+var)
    return response

def yield_file(file_path: str):
    with open(file=file_path, mode="rb") as file_like:
        yield file_like.read()
        
@app.get('/download/{var}')
async def downloadFile(var:str):
    global currentDirectory

    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    try:
        fullpath=Path(rootDirectory/fPath).absolute().resolve()
        if(fullpath.exists()):
            return RedirectResponse(url='/get?path='+str(fPath))
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
@app.get('/get/')
async def downloadFile(path:str):
    fPath=Path(path)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    try:
        fullpath=Path(rootDirectory/fPath).absolute().resolve()
        print(fullpath)
        return FileResponse(fullpath)
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
@app.get('/mkdir/')
def mkdir(path:str):
    fPath=Path(currentDirectory/path)
    fullpath=Path(rootDirectory/fPath).absolute()
    try:
        fullpath=fullpath.resolve().mkdir(parents=True, exist_ok=True)
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
@app.get('/delete/')
def mkdir(path:str):
    print("delete path:", path)
    fPath=Path(currentDirectory/path)
    fullpath=Path(rootDirectory/fPath).absolute()
    try:
        fullpath=fullpath.resolve()
        print(fullpath)
        if fullpath.exists():
            shutil.rmtree(fullpath, ignore_errors=False)
        else:
            raise HTTPException(status_code=404, detail="File not found")
        return RedirectResponse(url='/explorer/')
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
@app.get('/move/')
async def moveFile(target:str, source:str):
    fPath_t=Path(currentDirectory/target)
    fPath_s=Path(currentDirectory/source)
    if(set({str(fPath_s), str(fPath_t)}) in set(hiddenList)):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath_s=Path(rootDirectory/fPath_s).absolute()
    fullpath_t=Path(rootDirectory/fPath_t).absolute()
    try:
        fullpath_s=fullpath_s.resolve()
        fullpath_t=fullpath_t.resolve()
    except:
        raise HTTPException(status_code=404, detail="File Not Found")
    try:
        if fullpath_s.exists():     
            shutil.move(fullpath_s, fullpath_t)
        else:
            raise HTTPException(status_code=404, detail="File Not Found")
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
    return RedirectResponse(url='/explorer/')
    
@app.get('/stream/{var}')
async def streamFile(var:str):
    global currentDirectory

    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    try:
        fullpath=Path(rootDirectory/fPath).absolute().resolve()
        file_contents = yield_file(file_path=fullpath)
        kind = filetype.guess(fullpath.resolve())
        mime = kind.mime if kind else "application/octet-stream"
        response = StreamingResponse(
            content=file_contents,
            status_code=status.HTTP_200_OK,
            media_type=mime,
        )
        return response
    except FileNotFoundError:
        raise HTTPException(detail="File not found.", status_code=status.HTTP_404_NOT_FOUND)
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")


@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    global currentDirectory
    for file in files:
        fPath=Path(currentDirectory/file.filename)
        if(str(fPath) in hiddenList):
            #FILE HIDDEN
            raise HTTPException(status_code=100, detail="File Hidden")
        fullpath=Path(rootDirectory/fPath).absolute()
        try:
            with open(fullpath, 'wb') as f:
                while contents := file.file.read(1024 * 1024):
                    f.write(contents)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()
            
    return {"message": f"Successfuly uploaded {', '.join(file.filename for file in files)}"}  
 
@app.get("/audio_player/{var}")
async def audio_player(request: Request,var:str):
    global currentDirectory
    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    if fullpath.resolve().exists():
        kind = filetype.guess(fullpath.resolve())
        if kind is None:
            raise HTTPException(status_code=200, detail="Wrong format")
        else:
            print('File extension: %s' % kind.extension)
            print('File MIME type: %s' % kind.mime)
            return templates.TemplateResponse("audio_player.html", {"request": request,"media":var,"media_type":kind.mime})
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.get("/video_player/{var}")
async def video_player(request: Request,var:str):
    global currentDirectory
    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    if fullpath.resolve().exists():
        kind = filetype.guess(fullpath.resolve())
        if kind is None:
            raise HTTPException(status_code=200, detail="Wrong format")
        else:
            print('File extension: %s' % kind.extension)
            print('File MIME type: %s' % kind.mime)
            return templates.TemplateResponse("video_player.html", {"request": request,"media":var,"media_type":kind.mime})
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.get("/image_viewer/{var}")
async def image_viewer(request: Request,var:str):
    global currentDirectory
    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    if fullpath.resolve().exists():
        return templates.TemplateResponse("image_viewer.html", {"request": request,"media":var})
    else:
        raise HTTPException(status_code=404, detail="File not found")
    


@app.exception_handler(404)
async def custom_404_handler(request: Request, _):
    response =templates.TemplateResponse("error.html", {"request": request,"errorText":'Page not found!'})
    response.status_code = 404
    return response
@app.exception_handler(100)
async def custom_100_handler(request: Request, _):
    response = templates.TemplateResponse("error.html", {"request": request,"errorText":'File Hidden'})
    response.status_code = 100
    return response
@app.exception_handler(200)
async def custom_200_handler(request: Request, _):
    response = templates.TemplateResponse("error.html", {"request": request,"errorText":'Permission Denied'})
    response.status_code = 200
    return response
@app.exception_handler(300)
async def custom_300_handler(request: Request, _):
    response = templates.TemplateResponse("error.html", {"request": request,"errorText":'Invalid Directory Path'})
    response.status_code = 300
    return response

########################## python editor ########################################
@app.route("/blockpy")
async def blockpy(request: Request):
    return templates.TemplateResponse("blockpy.html", {"request": request,"loaded_code":""})
@app.get("/blockpy/{var}")
async def blockpy(request: Request,var: str):
    global currentDirectory,currentFile
    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    try:
        if fullpath.resolve().exists():
            if fullpath.suffix == '.py':
                return templates.TemplateResponse("blockpy.html", {"request": request,"loaded_code":var})
            else:
                return RedirectResponse(url='/stream/'+var)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
@app.route('/python_editor')
async def python_temp_editor(request: Request):
    session["count"] = 0
    session["time_now"] = datetime.now(timezone.utc)
    return templates.TemplateResponse('editor.html', {'request': request,"fileText":'',"filename":"untitled.py"})
@app.get('/python_editor/{var}')
async def python_file_editor(request: Request,var: str):
    session["count"] = 0
    session["time_now"] = datetime.now(timezone.utc)
    global currentDirectory,currentFile
    fPath=Path(currentDirectory/var)
    if(str(fPath) in hiddenList):
        #FILE HIDDEN
        raise HTTPException(status_code=100, detail="File Hidden")
    fullpath=Path(rootDirectory/fPath).absolute()
    print(fullpath)
    currentFile=fullpath
    try:
        fullpath=Path(rootDirectory/fPath).absolute().resolve()
        print(fullpath)
        fileText=''
        with open(fullpath,'r') as f:
            fileText=f.read()
        return templates.TemplateResponse('editor.html', {'request': request,"fileText":fileText,"filename":var})
    except:
        raise HTTPException(status_code=200, detail="Permission Denied")
    

@app.post('/save_code')
async def save_code(request: Request):
    global currentDirectory
    TxtFile=await request.json()
    print(TxtFile)
    fn=''
    if 'filename' in TxtFile.keys():
        if TxtFile['filename'] != '':
            fn=TxtFile['filename']
        else:
            print("missing filename")
            fn="Untitled.py"
    else:
        fn="Untitled.py"
    fPath=Path(rootDirectory/currentDirectory/fn)
    code=TxtFile['text']
    with open(fPath, 'w') as f:
        f.write(code)

    return JSONResponse(content=jsonable_encoder(["result saved"]))

@app.post('/check_code')
async def check_code(request: Request):

    """Run pylint on code and get output
        :return: JSON object of pylint errors
            {
                {
                    "code":...,
                    "error": ...,
                    "message": ...,
                    "line": ...,
                    "error_info": ...,
                }
                ...
            }

        For more customization, please look at Pylint's library code:
        https://github.com/PyCQA/pylint/blob/master/pylint/lint.py
    """
    TxtFile=await request.json()
    code=TxtFile['text']
    
    # Session to handle multiple users at one time and to get textarea from AJAX call
    if session["eval_busy"]:
        try:
            json_compatible_item_data = jsonable_encoder(session["eval"])
            return JSONResponse(content=json_compatible_item_data)
        except:
            json_compatible_item_data = jsonable_encoder("")
            return JSONResponse(content=json_compatible_item_data)

    session["code"] = code
    session["eval_busy"]=True
    output = evaluate_pylint(code)
    session["eval_busy"]=False
    session["eval"]=output
    # MANAGER.astroid_cache.clear()
    json_compatible_item_data = jsonable_encoder(output)
    return JSONResponse(content=json_compatible_item_data)

# Run python in secure system
@app.post('/run_code')
async def run_code(request: Request,background_tasks: BackgroundTasks):
    """Run python 3 code
        :return: JSON object of python 3 output
            {
                ...
            }
    """
    if os.path.exists("output.jpg"):
        os.remove("output.jpg")
    else:
        print("The file does not exist")
    TxtFile=await request.json()
    code=TxtFile['text']
    session["code"] = code
    if session["busy"]:
        try:
            session["process"].kill()
        except:
            pass
    session["busy"] = True
    dir=Path(rootDirectory/currentDirectory).absolute().resolve()
    write_temp(code,new=True)
    background_tasks.add_task(code_runner, dir)
    # code_runner(code, dir)
    json_compatible_item_data = jsonable_encoder(session["file_name"])
    return JSONResponse(content=json_compatible_item_data)
def code_runner(cwd):
    print("path exist:",Path(cwd,session["file_name"]).is_file())
    f=open(Path("/streaming"+session["file_name"]+".stdout"),"w")
    f.write("START".center(24,"+")+"\n")
    f.flush()
    p = Popen(['python3' ,session["file_name"]], cwd=cwd,stdout=f, stderr=f, env=my_env)
    session['process']=p
    while(1):
        poll = p.poll()
        if poll is None:
            print("running:",session["file_name"])
        else:
            print("done:",session["file_name"])
            break
        time.sleep(0.5)
    p.wait()
    f.write("END".center(24,"+")+"\n")
    f.close()
    session["busy"] =False
# Slow down if user clicks "Run" too many times
def slow():
    session["count"] += 1
    time = datetime.now(timezone.utc) - session["time_now"]
    if float(session["count"]) / float(time.total_seconds()) > 2:
        return True
    return False


def write_temp(text,new=False):
    if ("file_name" in session) and not new:
        f = open(session["file_name"], "w")
        for t in text:
            f.write(t)
        f.flush()
    else:
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            session["file_name"] = temp.name
            for t in text:
                temp.write(t.encode("utf-8"))
            temp.flush()

def evaluate_pylint(text):
    """Create temp files for pylint parsing on user code

    :param text: user code
    :return: dictionary of pylint errors:
        {
            {
                "code":...,
                "error": ...,
                "message": ...,
                "line": ...,
                "error_info": ...,
            }
            ...
        }
    """
    # Open temp file for specific session.
    # IF it doesn't exist (aka the key doesn't exist), create one
    write_temp(text)

    try:
        ARGS = " -r n --disable=R,C"
        (pylint_stdout, pylint_stderr) = lint.py_run(
            session["file_name"] + ARGS, return_std=True)
    except Exception as e:
        raise Exception(e)

    if pylint_stderr.getvalue():
        raise Exception("Issue with pylint configuration")

    return format_errors(pylint_stdout.getvalue())

def process_error(error):
    """Formats error message into dictionary

        :param error: pylint error full text
        :return: dictionary of error as:
            {
                "code":...,
                "error": ...,
                "message": ...,
                "line": ...,
                "error_info": ...,
            }
    """
    # Return None if not an error or warning
    if error == " " or error is None:
        return None
    if error.find("Your code has been rated at") > -1:
        return None

    list_words = error.split()
    if len(list_words) < 3:
        return None

    # Detect OS
    line_num = None
    if is_os_linux():
        try:
            line_num = error.split(":")[1]
        except Exception as e:
            print(os.name + " not compatible: " + e)
    else:
        line_num = error.split(":")[2]

    error_yet, message_yet, first_time = False, False, True
    i, length = 0, len(list_words)
    while i < length:
        word = list_words[i]
        if (word == "error" or word == "warning") and first_time:
            error_yet = True
            first_time = False
            i += 1
            continue
        if error_yet:
            error_code = word[1:-1]
            error_string = list_words[i + 1][:-1]
            i = i + 3
            error_yet = False
            message_yet = True
            continue
        if message_yet:
            full_message = ' '.join(list_words[i:length - 1])
            break
        i += 1

    error_info = pylint_dict_final[error_code]

    return {
        "code": error_code,
        "error": error_string,
        "message": full_message,
        "line": line_num,
        "error_info": error_info,
    }

def format_errors(pylint_text):
    """Format errors into parsable nested dictionary

    :param pylint_text: original pylint output
    :return: dictionary of errors as:
        {
            {
                "code":...,
                "error": ...,
                "message": ...,
                "line": ...,
                "error_info": ...,
            }
            ...
        }
    """
    errors_list = pylint_text.splitlines(True)

    # If there is not an error, return nothing
    if "--------------------------------------------------------------------" in errors_list[1] and \
            "Your code has been rated at" in errors_list[2] and "module" not in errors_list[0]:
        return None

    errors_list.pop(0)

    pylint_dict = {}
    try:
        pool = Pool(num_cores)
        pylint_dict = pool.map(process_error, errors_list)
    finally:
        pool.close()
        pool.join()
        return pylint_dict

    return pylint_dict

if __name__ == '__main__':
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description='clerous app server')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', default='')
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)

