from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Response, Request, status
import os
import uuid
from http import HTTPStatus
from pydantic import BaseModel
import tasks.celery_task as celeryTask

from tasks.celery_app import celery_app
from celery.result import AsyncResult
# from tasks.celery_task import research as research_task
# from tasks.celery_task import market as market_task
# from tasks.celery_task import recommendation as recommendation_task
# # from tasks.celery_task import file_txt_analyzer as file_txt
# import tasks.celery_task as celeryTask


from typing import Optional

TEXT_FOLDER = "files_text"
EXCEL_FOLDER = "files_excel"
IMAGE_FOLDER = "files_image"

os.makedirs(TEXT_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

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



app = FastAPI()
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
