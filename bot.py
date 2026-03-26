import os
import io
import base64
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = "http://127.0.0.1:8000"  # FastAPI server

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# HELPER: Severity emoji label
# ─────────────────────────────────────────────
def severity_emoji(grade: str) -> str:
    return {
        "Mild":     "🟡 Mild",
        "Moderate": "🟠 Moderate",
        "Severe":   "🔴 Severe",
        "Healthy":  "🟢 Healthy",
    }.get(grade, f"⚪ {grade}")


# ─────────────────────────────────────────────
# HELPER: Action tip based on severity
# ─────────────────────────────────────────────
def get_tip(severity: str) -> str:
    return {
        "Mild":     "💡 Tip: Monitor the plant closely. Remove affected leaves as a precaution.",
        "Moderate": "⚠️ Tip: Remove all infected leaves immediately and apply a suitable fungicide.",
        "Severe":   "🚨 Tip: Severe infection! Isolate the plant and consult an agronomist urgently.",
        "Healthy":  "✅ Tip: Plant looks healthy! Keep up with regular watering and fertilising.",
    }.get(severity, "💡 Consult a local agronomist for advice.")


# ─────────────────────────────────────────────
# COMMAND: /start
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args and len(args) > 0:
        token = args[0]
        user = update.message.from_user
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/auth/verify",
                    json={
                        "token": token,
                        "chat_id": str(user.id),
                        "first_name": user.first_name,
                        "username": user.username if user.username else ""
                    }
                )
                if response.status_code != 200:
                    print(f"Server rejected login. Status Code: {response.status_code}")
                    print(f"Response Body: {response.text}")
                
                response.raise_for_status()
            await update.message.reply_text("✅ Successfully logged in to AgriSight Web!")
            return
        except Exception as e:
            print(f"Connection Error: {e}")
            logger.error(f"Login auth error: {e}")
            await update.message.reply_text("❌ Login failed. Please try again.")
            return

    try:
        if update.effective_chat:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{BACKEND_URL}/api/register",
                    json={"telegram_chat_id": str(update.effective_chat.id)}
                )
    except Exception as e:
        logger.error(f"Registration error: {e}")

    await update.message.reply_text(
        "🌱 *Welcome to AgriSight!*\n\n"
        "I can detect crop pests and diseases from a photo.\n\n"
        "📸 Just send me a clear photo of a plant leaf and I will:\n"
        "  • Identify the disease or pest\n"
        "  • Tell you the severity (Mild / Moderate / Severe)\n"
        "  • Give you a quick action tip\n\n"
        "Commands:\n"
        "/start   – Welcome message\n"
        "/help    – How to use this bot\n"
        "/history – View your last 5 scans\n\n"
        "Go ahead — send your first leaf photo! 🍃",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# COMMAND: /help
# ─────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *AgriSight Help*\n\n"
        "📸 *How to scan a leaf:*\n"
        "Simply send a photo of the leaf directly in this chat.\n"
        "Make sure the leaf is well-lit and fills most of the frame.\n\n"
        "📋 *Commands:*\n"
        "/start   – Welcome message\n"
        "/help    – Show this help\n"
        "/history – View your last 5 scans\n\n"
        "🌿 *Severity Grades:*\n"
        "🟢 Healthy  – No disease detected\n"
        "🟡 Mild     – Less than 10% affected\n"
        "🟠 Moderate – 10% to 30% affected\n"
        "🔴 Severe   – More than 30% affected",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# COMMAND: /history
# ─────────────────────────────────────────────
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        return
    telegram_chat_id = str(update.effective_chat.id)
    await update.message.reply_text("🔍 Fetching your scan history...")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/history/{telegram_chat_id}")
            response.raise_for_status()
            records = response.json()

        if not records:
            await update.message.reply_text(
                "📭 No scan history yet.\nSend a leaf photo to get started!"
            )
            return

        # Show the 5 most recent scans
        recent = records[-5:][::-1]
        lines = ["📋 *Your Recent Scans:*\n"]

        for i, record in enumerate(recent, 1):
            timestamp = record.get("timestamp", "Unknown time")
            scan_id_short = record.get("scan_id", "")[:8]
            detections = record.get("detections", [])

            if detections:
                first    = detections[0]
                label    = first.get("class_label", "Unknown")
                severity = first.get("severity_grade", "Unknown")
                lines.append(
                    f"{i}. `{scan_id_short}...`\n"
                    f"   🦠 {label} | {severity_emoji(severity)}\n"
                    f"   🕐 {timestamp}\n"
                )
            else:
                lines.append(f"{i}. `{scan_id_short}...` | 🕐 {timestamp}\n")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except httpx.ConnectError:
        await update.message.reply_text(
            "⚠️ *Cannot reach the AgriSight server.*\n\n"
            "Make sure the backend is running:\n"
            "`py -m uvicorn main:app --reload`",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"History error: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")


# ─────────────────────────────────────────────
# MESSAGE HANDLER: Incoming photo
# ─────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text(
        "📷 Photo received!\n🔬 Analyzing with YOLOv8... please wait."
    )

    try:
        # ── Step 1: Download photo from Telegram ──────────────────────────
        # Always grab the last item — that's the highest resolution version
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()

        # ── Step 2: POST image to /api/predict ─────────────────
        chat_id = str(update.message.chat_id)  # Ensure chat_id is always a string
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BACKEND_URL}/api/predict",
                files={'file': ('image.jpg', bytes(photo_bytes), 'image/jpeg')},
                data={'telegram_chat_id': chat_id},  # Always send as string
            )
            if response.status_code != 200:
                print(f"API Error: {response.text}")
            response.raise_for_status()
            result = response.json()

        # ── Step 3: Handle backend errors ─────────────────────────────────
        if result.get("status") != "success":
            await status_msg.edit_text(
                f"❌ Backend error: {result.get('detail', 'Unknown error')}"
            )
            return

        detections = result.get("detections", [])
        annotated_b64 = result.get("annotated_image_base64", None)

        # ── Step 4: Build reply text ───────────────────────────────────────
        if not detections:
            await status_msg.edit_text(
                "🔍 *Scan Complete*\n\n"
                "✅ No diseases or pests detected!\n"
                "Your plant appears to be healthy. 🌿",
                parse_mode="Markdown",
            )
            return

        lines: list[str] = []
        for det in detections:
            label = det.get("label", "Unknown")
            confidence = det.get("confidence", 0) * 100
            severity_grade = det.get("severity", "Unknown")

            lines.append(
                f"⚠️ Detected: {label}\n"
                f"📊 Severity: {severity_grade}\n"
                f"Confidence: {confidence:.1f}%"
            )

        reply_text = "\n\n".join(lines)

        # ── Step 5: Send annotated image + results back to farmer ──────────
        if annotated_b64:
            image_data = base64.b64decode(annotated_b64)
            image_file = io.BytesIO(image_data)
            image_file.name = "result.jpg"

            await status_msg.delete()
            await update.message.reply_photo(
                photo=image_file,
                caption=reply_text,
                parse_mode="Markdown",
            )
        else:
            await status_msg.edit_text(reply_text, parse_mode="Markdown")

    except httpx.ConnectError:
        await status_msg.edit_text(
            "⚠️ *Cannot reach the AgriSight server.*\n\n"
            "Make sure the backend is running:\n"
            "`py -m uvicorn main:app --reload`",
            parse_mode="Markdown",
        )
    except httpx.TimeoutException:
        await status_msg.edit_text(
            "⏱️ The server took too long to respond.\n"
            "The model may still be loading. Please try again in a moment."
        )
    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await status_msg.edit_text("❌ An unexpected error occurred. Please try again.")


# ─────────────────────────────────────────────
# FALLBACK: User sends text instead of photo
# ─────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Please send a *photo* of a crop leaf for analysis.\n"
        "I can only analyse images, not text descriptions.\n\n"
        "Need help? Type /help",
        parse_mode="Markdown",
    )


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN not found!\n"
            "Make sure your .env file exists with: BOT_TOKEN=your_token_here"
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("help",    help_command))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ AgriSight Bot is running... Press Ctrl+C to stop.")
    app.run_polling()
