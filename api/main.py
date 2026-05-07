from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Response, Request, status
import os
import uuid
from http import HTTPStatus
from pydantic import BaseModel
import tasks.celery_task as celeryTask

from tasks.celery_app import celery_app
from celery.result import AsyncResult
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import Optional

TEXT_FOLDER = "files_text"
EXCEL_FOLDER = "files_excel"
IMAGE_FOLDER = "files_image"

os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

TOKEN = "8065516745:AAEPBJ9DOATCvQ4o--SJ0GlGBySyTry7u6I"
WEBHOOK_URL = os.getenv("WEBHOOK_URL","https://marsh-delight-proceedings-guardian.trycloudflare.com/webhook")

ptb =(
    Application.builder()
    .updater(None)
    .token(TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    lifecycle manager for PTB
    """
    await ptb.bot.set_webhook(WEBHOOK_URL)
    async with ptb:
        await ptb.start()
        yield
    await ptb.stop()


class ResearchInput(BaseModel):
    topic : str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None

class RecommendationInput(BaseModel):
    motor_type: str
    km: int
    complaint: str
    usage: str



app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(request:Request):
    """
    The endpoint telegram will send update
    """
    req_json = await request.json()
    update = Update.de_json(req_json, ptb.bot)

    await ptb.process_update(update)
    return Response(status_code = HTTPStatus.OK)

async def start_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    """
    handler untuk command /start
    """
    await update.message.reply_text("startting ... bot nyala")

async def image_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):
    photo_size = update.message.photo[-1]
    file_id = photo_size.file_id
    file_unique_id = photo_size.file_unique_id
    width = photo_size.width
    height = photo_size.height
    file_size = photo_size.file_size


    reply_text =(
        f"<b>Received Image Data</b>"
        f"Dimension : {width}x{height}px\n"
        f"File Size : {round(file_size/1024,2)}KB\n"
        f"<code>file_id</code>: <code> {file_id}</code>\n"
        f"<code>file_unique_id</code>: <code>{file_unique_id}</code>"

    )
    await update.message.reply_text(reply_text,parse_mode="HTML")


async def bot_reserach(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Pesan salah, gunakan perintah:\n /research ['topic']", parse_mode="MarkdownV2"
        )
        return

        # await update.message.reply_text("Please provide a topic for research. Usage: /research <topic>")
        # return

    input_data = ResearchInput(topic=context.args[0])
    task = celeryTask.research.delay(input_data.topic)
    # await update.message.chat.send_action(action="typing")
    # await update.message.reply_text(f"task_id: /{task_id}")

    await update.message.reply_text(
        f"Research task has been queued with topic: {input_data.topic}\n"
        f"Task ID: {task.id}"
    )

async def bot_status(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Pesan salah, gunakan perintah:\n /status ['task_id']", parse_mode="MarkdownV2"
        )
        return

    task_result = AsyncResult(context.args[0], app=celery_app)
    response = {
        "task_id": context.args[0],
        "status": task_result.state,
        "result": str(task_result.result) if task_result.status == 'SUCCESS' else None,
        "error" : None
    }

    if task_result.state == 'SUCCESS':
       response['result'] = task_result.result

    elif task_result.state == 'FAILURE' :
        response['error'] = str(task_result.info)

    await update.message.chat.send_action(action='typing')




ptb.add_handler(CommandHandler("start", start_command))
ptb.add_handler(MessageHandler(filters.PHOTO, image_handler))
ptb.add_handler(CommandHandler("research",bot_reserach))
ptb.add_handler(CommandHandler("status",bot_status))

@app.post("/tes")
async def tes():
    return {"message":"hello world!"}

@app.post("/research")
async def research_endpoint(researchInput: ResearchInput):
    task = celeryTask.research_task.delay(researchInput.topic)

    return {
        "task_id": task.id,
        "status": "queued"
    }

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if not task_result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Task not found")

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": str(task_result.result) if task_result.status == 'SUCCESS' else None
    }

@app.post("/market")
async def research_endpoint(researchInput: ResearchInput):
    task = celeryTask.market.delay(researchInput.topic)

    return {
        "task_id": task.id,
        "status": "queued"
    }

# @app.post("/recommendation")
# async def research_endpoint(researchInput: ResearchInput):
#     task = recommendation_task.delay(researchInput.topic)

#     return {
#         "task_id": task.id,
#         "status": "queued"
#     }

@app.post("/recommendation")
async def recommendation(input: RecommendationInput):
    task = celeryTask.recommendation.delay(
        input.motor_type,
        input.km,
        input.complaint,
        input.usage
    )

    return {
        "task_id": task.id,
        "status": "queued"
    }


@app.post("/txt-analyzer")
async def txt_analyzer(file:UploadFile=File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail ="title must be TXT")

    file_extension =os.path.splitext(file.filename)[1] or ".txt"

    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_loc = os.path.join(TEXT_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.file_txt_analyzer.delay(file_loc)

    return {
        "status": "processing",
        "task_id": task.id,
        "file_loc": file_loc
    }

# deteksi_anomali_excel
@app.post("/anomali_deteksi_tool")
async def txt_analyzer(file:UploadFile=File(...)):
    # if file.content_type != "text/plain":
    #     raise HTTPException(status_code=400, detail ="title must be TXT")

    # file_extension =os.path.splitext(file.filename)[1] or ".txt"

      # validasi extension
    allowed_extensions = [".xlsx", ".xls"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File must be Excel (.xlsx or .xls)"
        )

    # optional: validasi content-type (tambahan keamanan)
    allowed_content_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel"  # .xls
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid content type for Excel file"
        )


    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_loc = os.path.join(EXCEL_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.deteksi_anomali_excel.delay(file_loc)

    return {
        "status": "processing",
        "task_id": task.id,
        "file_loc": file_loc
    }

@app.post("/excel-analyzer")
async def excel_analyzer(file:UploadFile=File(...)):
    allowed_extensions = [".xlsx", ".xls"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File must be Excel (.xlsx or .xls)"
        )

    # optional: validasi content-type (tambahan keamanan)
    allowed_content_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel"  # .xls
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid content type for Excel file"
        )

    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_loc = os.path.join(EXCEL_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.file_excel_analyzer.delay(file_loc)

    return {
        "status": "processing",
        "task_id": task.id,
        "file_loc": file_loc
    }


@app.post("/predict_tool")
async def txt_analyzer(file:UploadFile=File(...)):
    # if file.content_type != "text/plain":
    #     raise HTTPException(status_code=400, detail ="title must be TXT")

    # file_extension =os.path.splitext(file.filename)[1] or ".txt"

      # validasi extension
    allowed_extensions = [".xlsx", ".xls"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File must be Excel (.xlsx or .xls)"
        )

    # optional: validasi content-type (tambahan keamanan)
    allowed_content_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/vnd.ms-excel"  # .xls
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid content type for Excel file"
        )


    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_loc = os.path.join(EXCEL_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.predict_excel.delay(file_loc)

    return {
        "status": "processing",
        "task_id": task.id,
        "file_loc": file_loc
    }

@app.post("/deteksi_helm")
async def deteksi_helm(file:UploadFile=File(...)):

    if file.content_type != "image/jpeg":
        raise HTTPException(status_code=400, detail ="file must be an image")

    file_extension =os.path.splitext(file.filename)[1] or ".jpg"

    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    file_loc = os.path.join(IMAGE_FOLDER, unique_name)

    content = await file.read()
    with open(file_loc, "wb") as f:
        f.write(content)

    task = celeryTask.detect_helm.delay(file_loc)

    return {
        "task_id": task.id,
        "file_path":file_loc,
        "status": "queued"
    }
