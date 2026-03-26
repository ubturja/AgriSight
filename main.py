import os
import uuid
import datetime
import asyncio
import base64
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import joinedload # type: ignore
from dotenv import load_dotenv
from models import SessionLocal, ScanLog, Detection, User, init_db # type: ignore
from ai_pipeline import run_inference, draw_annotations_and_encode

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_agrisight_email(to_email: str, subject: str, body_text: str):
    if not to_email:
        return
    msg = MIMEText(body_text)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_weekly_summaries():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.weekly_summary == True, User.email.isnot(None)).all()
        seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        
        for user in users:
            logs = db.query(ScanLog).filter(
                ScanLog.user_id == user.user_id, 
                ScanLog.timestamp >= seven_days_ago
            ).all()
            
            total_scans = len(logs)
            if total_scans == 0:
                continue
            
            severe_count = sum(
                1 for log in logs for det in log.detections if det.severity_grade == "Severe"
            )
            
            summary_body = (
                f"Hello!\n\nHere is your AgriSight weekly summary for the past 7 days:\n"
                f"- Total scans performed: {total_scans}\n"
                f"- Scans with 'Severe' detections: {severe_count}\n\n"
                f"Stay vigilant and check your dashboard for more details!"
            )
            send_agrisight_email(user.email, "AgriSight Weekly Summary", summary_body)
    except Exception as e:
        print(f"Error in send_weekly_summaries: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_weekly_summaries, trigger='cron', day_of_week='mon', hour=8)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="AgriSight Backend", lifespan=lifespan)

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    telegram_chat_id: str

login_sessions = {}

class AuthVerify(BaseModel):
    token: str
    chat_id: str
    first_name: str
    username: str

class UserPreferencesUpdate(BaseModel):
    telegram_chat_id: str
    email: Optional[str] = None
    email_reports: bool
    sms_alerts: bool
    weekly_summary: bool

@app.post("/api/auth/verify")
async def verify_auth(payload: AuthVerify):
    login_sessions[payload.token] = payload.model_dump()
    
    # Ensure they exist in DB so we can update their preferences later
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_chat_id == payload.chat_id).first()
        if not user:
            user = User(telegram_chat_id=payload.chat_id)
            db.add(user)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
        
    return {"status": "success"}

@app.get("/api/auth/status")
async def auth_status(token: str):
    if token in login_sessions:
        return {"status": "success", "user": login_sessions[token]}
    return {"status": "pending"}

@app.put("/api/user/preferences")
async def update_preferences(prefs: UserPreferencesUpdate):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_chat_id == prefs.telegram_chat_id).first()
        if not user:
            # Create user if not exists just in case
            user = User(telegram_chat_id=prefs.telegram_chat_id)
            db.add(user)
        user.email = prefs.email
        user.email_reports = prefs.email_reports
        user.sms_alerts = prefs.sms_alerts
        user.weekly_summary = prefs.weekly_summary
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/register")
async def register(user_data: UserRegister):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_chat_id == user_data.telegram_chat_id).first()
        if not user:
            user = User(telegram_chat_id=user_data.telegram_chat_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"user_id": user.user_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/api/predict")
async def predict(background_tasks: BackgroundTasks, file: UploadFile = File(...), telegram_chat_id: str = Form(...)):
    db = SessionLocal()
    try:
        print(f"[DEBUG] /api/predict called with telegram_chat_id: {telegram_chat_id}")
        # Ensure user exists for FK constraint
        user = db.query(User).filter(User.telegram_chat_id == telegram_chat_id).first()
        if not user:
            print(f"[DEBUG] No user found for chat_id {telegram_chat_id}, creating new user.")
            user = User(telegram_chat_id=telegram_chat_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"[DEBUG] Found user {user.user_id} for chat_id {telegram_chat_id}")

        current_user_id = user.user_id

        scan_id = str(uuid.uuid4())

        # Save exact uploaded file to disk
        file_extension = file.filename.split(".")[-1]
        file_name = f"{scan_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        image_bytes = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(image_bytes)

        predictions, img_matrix = run_inference(image_bytes)
        base64_string = draw_annotations_and_encode(img_matrix, predictions)

        # Create ScanLog
        new_log = ScanLog(
            scan_id=scan_id,
            user_id=current_user_id,
            image_path=file_path,
            inference_time_ms=500.0,
            timestamp=datetime.datetime.utcnow()
        )
        db.add(new_log)

        detections_list = []
        for pred in predictions:
            new_detection = Detection(
                detection_id=str(uuid.uuid4()),
                scan_id=scan_id,
                class_label=pred["label"],
                confidence_score=pred["confidence"],
                severity_grade=pred["severity_grade"],
                bbox_coordinates=str(pred["bbox"])
            )
            db.add(new_detection)

            detections_list.append({
                "label": pred["label"],
                "confidence": pred["confidence"],
                "severity": pred["severity_grade"]
            })

        db.commit()

        # Send instant email report if user opted in
        if user.email_reports and user.email and detections_list:
            body_lines = ["AgriSight Alert! Your scan results:\n"]
            for d in detections_list:
                # Include Crop and Disease label and Confidence
                body_lines.append(f"- Detected: {d['label']} (Confidence: {d['confidence']:.2f}, Severity: {d['severity']})")
            body_text = "\n".join(body_lines)
            background_tasks.add_task(send_agrisight_email, user.email, "AgriSight Instant Scan Report", body_text)

        return {
            "status": "success", 
            "detections": detections_list,
            "annotated_image_base64": base64_string
        }
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Exception in /api/predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/api/history/{telegram_chat_id}")
async def get_history(telegram_chat_id: str):
    db = SessionLocal()
    try:
        # Query with joinedload to fetch detections in one query
        results = db.query(ScanLog).join(User).options(joinedload(ScanLog.detections)).filter(User.telegram_chat_id == telegram_chat_id).all()
        
        # Manually serialize the SQLAlchemy models to raw JSON dictionaries
        history_list = []
        for log in results:
            image_base64 = None
            if log.image_path and os.path.exists(log.image_path):
                with open(log.image_path, "rb") as img_file:
                    image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    
            log_dict = {
                "scan_id": log.scan_id,
                "user_id": log.user_id,
                "image_path": log.image_path,
                "image_base64": image_base64,
                "inference_time_ms": log.inference_time_ms,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "detections": []
            }
            for det in log.detections:
                log_dict["detections"].append({
                    "detection_id": det.detection_id,
                    "class_label": det.class_label,
                    "confidence_score": det.confidence_score,
                    "severity_grade": det.severity_grade,
                    "bbox_coordinates": det.bbox_coordinates
                })
            history_list.append(log_dict)
            
        return history_list
    finally:
        db.close()