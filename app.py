import streamlit as st
import streamlit.components.v1 as components
import base64
import cv2
import os
import uuid
import datetime
import json
import numpy as np
from ai_pipeline import run_inference, draw_annotations_and_encode
from models import SessionLocal, ScanLog, Detection
from sqlalchemy.orm import joinedload

st.set_page_config(page_title='AgriSight Pro', layout='wide', initial_sidebar_state='expanded')

st.markdown("""
    <style>
        /* Force Streamlit container properties */
        .stApp { background-color: #ffffff !important; }
        .block-container { max-width: 100% !important; padding: 2rem !important; }
        
        /* Hide Streamlit top header line */
        header {visibility: hidden;}
        
        /* Force Streamlit Sidebar to match Stitch Emerald-950 */
        [data-testid="stSidebar"] {
            background-color: #022c22 !important; 
        }
        [data-testid="stSidebar"] * {
            color: #ecfdf5 !important; /* Light text for dark background */
        }
    </style>
    """, unsafe_allow_html=True)

nav_selection = st.sidebar.radio("Navigation", ['Live Scan', 'Scan History'])

if nav_selection == 'Live Scan':
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        predictions, img_matrix = run_inference(image_bytes)
        base64_string = draw_annotations_and_encode(img_matrix, predictions)
        
        if predictions:
            primary = predictions[0]
            label = primary.get('label', 'Unknown').title()
            confidence = round(primary.get('confidence', 0) * 100, 1)
            severity_grade = primary.get('severity_grade', 'Unknown').title()
        else:
            label = "Healthy"
            confidence = 100.0
            severity_grade = "None"
            
        mild_classes = "opacity-40 grayscale"
        moderate_classes = "opacity-40 grayscale"
        severe_classes = "opacity-40 grayscale"
        
        sg_lower = severity_grade.lower()
        if sg_lower == 'mild':
            mild_classes = "ring-2 ring-emerald-800/10"
        elif sg_lower == 'moderate':
            moderate_classes = "ring-2 ring-orange-800/10"
        elif sg_lower == 'severe':
            severe_classes = "ring-2 ring-error/10 text-error"

        original_base64 = base64.b64encode(image_bytes).decode('utf-8')

        html_string = f"""
        <!DOCTYPE html><html class="light" lang="en"><head>
        <meta charset="utf-8">
        <meta content="width=device-width, initial-scale=1.0" name="viewport">
        <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
        <script id="tailwind-config">
              tailwind.config = {{
                darkMode: "class",
                theme: {{
                  extend: {{
                    colors: {{
                      "primary": "#012d1d",
                      "on-background": "#1c1b1b",
                      "error-container": "#ffdad6",
                      "on-primary-fixed-variant": "#274e3d",
                      "on-secondary": "#ffffff",
                      "surface-tint": "#3f6653",
                      "on-secondary-fixed-variant": "#0e5138",
                      "primary-fixed": "#c1ecd4",
                      "on-error-container": "#93000a",
                      "inverse-on-surface": "#f3f0ef",
                      "on-tertiary-container": "#d29895",
                      "tertiary-fixed-dim": "#f5b7b4",
                      "tertiary-fixed": "#ffdad8",
                      "on-primary-container": "#86af99",
                      "surface-container-lowest": "#ffffff",
                      "secondary-container": "#aeeecb",
                      "on-primary-fixed": "#002114",
                      "on-surface-variant": "#414844",
                      "surface-container": "#f0eded",
                      "on-primary": "#ffffff",
                      "on-secondary-fixed": "#002114",
                      "surface-dim": "#dcd9d9",
                      "surface-container-low": "#f6f3f2",
                      "surface-container-highest": "#e5e2e1",
                      "surface-bright": "#fcf9f8",
                      "on-secondary-container": "#316e52",
                      "outline-variant": "#c1c8c2",
                      "on-surface": "#1c1b1b",
                      "tertiary": "#401b1b",
                      "secondary-fixed-dim": "#95d4b3",
                      "inverse-primary": "#a5d0b9",
                      "on-tertiary": "#ffffff",
                      "secondary": "#2c694e",
                      "surface": "#fcf9f8",
                      "outline": "#717973",
                      "primary-fixed-dim": "#a5d0b9",
                      "on-tertiary-fixed-variant": "#673a39",
                      "error": "#ba1a1a",
                      "surface-variant": "#e5e2e1",
                      "secondary-fixed": "#b1f0ce",
                      "surface-container-high": "#eae7e7",
                      "tertiary-container": "#5a302f",
                      "primary-container": "#1b4332",
                      "on-error": "#ffffff",
                      "on-tertiary-fixed": "#331111",
                      "inverse-surface": "#313030",
                      "background": "#fcf9f8"
                    }},
                    fontFamily: {{
                      "headline": ["Manrope"],
                      "body": ["Inter"],
                      "label": ["Inter"]
                    }},
                    borderRadius: {{"DEFAULT": "0.5rem", "lg": "1rem", "xl": "1.25rem", "full": "9999px"}},
                  }},
                }},
              }}
            </script>
        <style>
                .material-symbols-outlined {{
                    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
                }}
                .bg-glass {{
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                }}
                .custom-dashed {{
                    background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='16' ry='16' stroke='%23C1C8C2' stroke-width='2' stroke-dasharray='8%2c 12' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
                }}
            </style>
        </head>
        <body class="bg-surface font-body text-on-surface antialiased" data-mode="connect">

        <div class="max-w-7xl mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <!-- Left Side: Results -->
        <div class="lg:col-span-8 space-y-8">
        <!-- Results Split-View -->
        <div class="grid md:grid-cols-2 gap-6 items-stretch">
        <!-- Original Image -->
        <div class="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
        <div class="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
        <span class="text-xs font-bold text-on-surface-variant tracking-wider uppercase">Original Specimen</span>
        <span class="material-symbols-outlined text-emerald-800/40 text-sm" data-icon="image">image</span>
        </div>
        <div class="aspect-square bg-surface-container-highest/50 relative">
        <img alt="Original Leaf" class="w-full h-full object-cover opacity-80" data-alt="Original image" src="data:image/jpeg;base64,{original_base64}">
        <div class="absolute inset-0 flex items-center justify-center bg-black/5">
        <div class="px-3 py-1 bg-black/40 backdrop-blur-md rounded-full text-[10px] text-white font-bold uppercase tracking-widest">Input Layer</div>
        </div>
        </div>
        </div>
        <!-- Annotated Image -->
        <div class="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
        <div class="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
        <span class="text-xs font-bold text-on-surface-variant tracking-wider uppercase">AI Inference Overlay</span>
        <span class="material-symbols-outlined text-emerald-800/40 text-sm" data-icon="neurology" style="font-variation-settings: 'FILL' 1;">neurology</span>
        </div>
        <div class="aspect-square bg-surface-container-highest/50 relative">
        <img alt="Annotated Leaf" class="w-full h-full object-cover" data-alt="Leaf image with bright digital bounding boxes over diseased areas" src="data:image/jpeg;base64,{base64_string}">
        <div class="absolute inset-0">
        </div>
        <div class="absolute bottom-4 right-4 p-2 bg-emerald-900/80 backdrop-blur-md rounded-lg text-white">
        <span class="material-symbols-outlined text-xl" data-icon="verified_user">verified_user</span>
        </div>
        </div>
        </div>
        </div>
        </div>
        <!-- Right Side: Diagnosis Panel -->
        <div class="lg:col-span-4">
        <div class="sticky top-24 bg-surface-container-lowest rounded-xl shadow-[0_12px_32px_-4px_rgba(28,27,27,0.06)] p-6 border border-outline-variant/5">
        <div class="flex items-center justify-between mb-8">
        <h2 class="text-sm font-black text-on-surface-variant uppercase tracking-widest">Diagnosis Results</h2>
        <span class="material-symbols-outlined text-primary" data-icon="analytics">analytics</span>
        </div>
        <div class="space-y-6">
        <!-- Disease Name -->
        <div>
        <label class="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter">Detected Pathology</label>
        <h3 class="text-3xl font-black text-on-surface font-headline leading-none mt-1">{label}</h3>
        <p class="text-sm text-on-surface-variant mt-2">AI Assessed Condition</p>
        </div>
        <!-- Confidence -->
        <div class="bg-surface-container-low rounded-lg p-4">
        <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-bold text-on-surface">Confidence Score</span>
        <span class="text-xl font-black text-primary font-headline">{confidence:.1f}%</span>
        </div>
        <div class="w-full h-2 bg-outline-variant/20 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-secondary to-primary" style="width: {confidence:.1f}%;"></div>
        </div>
        </div>
        <!-- Severity Badges -->
        <div>
        <label class="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter mb-3 block">Condition Severity</label>
        <div class="flex flex-wrap gap-2">
        <div class="px-4 py-1.5 rounded-full bg-emerald-100/50 text-emerald-800 text-xs font-bold flex items-center gap-1 {{mild_classes}}">
                                                Mild
                                            </div>
        <div class="px-4 py-1.5 rounded-full bg-orange-100/50 text-orange-800 text-xs font-bold flex items-center gap-1 {{moderate_classes}}">
                                                Moderate
                                            </div>
        <div class="px-4 py-1.5 rounded-full bg-error-container text-on-error-container text-xs font-bold flex items-center gap-1 {{severe_classes}}">
        <span class="material-symbols-outlined text-sm" data-icon="warning">warning</span>
                                                Severe
                                            </div>
        </div>
        </div>
        </div>
        </div>
        </div>
        </div>
        </div>
        </body></html>
        """
        components.html(html_string, height=850, scrolling=True)
        
        if st.button("Save Scan to Database"):
            db = SessionLocal()
            try:
                os.makedirs("static/uploads", exist_ok=True)
                filename = f"scan_{uuid.uuid4().hex}.jpg"
                filepath = os.path.join("static/uploads", filename)
                
                with open(filepath, "wb") as f:
                    f.write(image_bytes)
                
                scan_log = ScanLog(
                    image_path=filepath,
                    timestamp=datetime.datetime.utcnow()
                )
                db.add(scan_log)
                db.commit()
                db.refresh(scan_log)
                
                if predictions:
                    for pred in predictions:
                        det = Detection(
                            scan_id=scan_log.scan_id,
                            class_label=pred.get('label', 'Unknown'),
                            confidence_score=pred.get('confidence', 0),
                            severity_grade=pred.get('severity_grade', 'Unknown'),
                            bbox_coordinates=json.dumps(pred.get('bbox', []))
                        )
                        db.add(det)
                else:
                    det = Detection(
                        scan_id=scan_log.scan_id,
                        class_label="Healthy",
                        confidence_score=1.0,
                        severity_grade="None",
                        bbox_coordinates="[]"
                    )
                    db.add(det)
                
                db.commit()
                st.success("Successfully saved to history!")
            except Exception as e:
                db.rollback()
                st.error(f"Error saving to database: {e}")
            finally:
                db.close()

        else:
            empty_html_string = f'''<!DOCTYPE html><html class="light" lang="en"><head>
        <meta charset="utf-8">
        <meta content="width=device-width, initial-scale=1.0" name="viewport">
        <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
        <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
        <script id="tailwind-config">
              tailwind.config = {{
                darkMode: "class",
                theme: {{
                  extend: {{
                    colors: {{
                      "primary": "#012d1d",
                      "on-background": "#1c1b1b",
                      "error-container": "#ffdad6",
                      "on-primary-fixed-variant": "#274e3d",
                      "on-secondary": "#ffffff",
                      "surface-tint": "#3f6653",
                      "on-secondary-fixed-variant": "#0e5138",
                      "primary-fixed": "#c1ecd4",
                      "on-error-container": "#93000a",
                      "inverse-on-surface": "#f3f0ef",
                      "on-tertiary-container": "#d29895",
                      "tertiary-fixed-dim": "#f5b7b4",
                      "tertiary-fixed": "#ffdad8",
                      "on-primary-container": "#86af99",
                      "surface-container-lowest": "#ffffff",
                      "secondary-container": "#aeeecb",
                      "on-primary-fixed": "#002114",
                      "on-surface-variant": "#414844",
                      "surface-container": "#f0eded",
                      "on-primary": "#ffffff",
                      "on-secondary-fixed": "#002114",
                      "surface-dim": "#dcd9d9",
                      "surface-container-low": "#f6f3f2",
                      "surface-container-highest": "#e5e2e1",
                      "surface-bright": "#fcf9f8",
                      "on-secondary-container": "#316e52",
                      "outline-variant": "#c1c8c2",
                      "on-surface": "#1c1b1b",
                      "tertiary": "#401b1b",
                      "secondary-fixed-dim": "#95d4b3",
                      "inverse-primary": "#a5d0b9",
                      "on-tertiary": "#ffffff",
                      "secondary": "#2c694e",
                      "surface": "#fcf9f8",
                      "outline": "#717973",
                      "primary-fixed-dim": "#a5d0b9",
                      "on-tertiary-fixed-variant": "#673a39",
                      "error": "#ba1a1a",
                      "surface-variant": "#e5e2e1",
                      "secondary-fixed": "#b1f0ce",
                      "surface-container-high": "#eae7e7",
                      "tertiary-container": "#5a302f",
                      "primary-container": "#1b4332",
                      "on-error": "#ffffff",
                      "on-tertiary-fixed": "#331111",
                      "inverse-surface": "#313030",
                      "background": "#fcf9f8"
                    }},
                    fontFamily: {{
                      "headline": ["Manrope"],
                      "body": ["Inter"],
                      "label": ["Inter"]
                    }},
                    borderRadius: {{"DEFAULT": "0.5rem", "lg": "1rem", "xl": "1.25rem", "full": "9999px"}},
                  }},
                }},
              }}
            </script>
        <style>
                .material-symbols-outlined {{
                    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
                }}
                .bg-glass {{
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                }}
                .custom-dashed {{
                    background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='16' ry='16' stroke='%23C1C8C2' stroke-width='2' stroke-dasharray='8%2c 12' stroke-dashoffset='0' stroke-linecap='square'/%3e%3c/svg%3e");
                }}
            </style>
        </head>
            <body class="bg-surface font-body text-on-surface antialiased" data-mode="connect">
            <div class="max-w-7xl mx-auto px-6 py-8">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Left Side: Results -->
            <div class="lg:col-span-8 space-y-8">
            
            <!-- Upload Zone Placeholder Idea -->
            <div class="w-full h-32 custom-dashed rounded-2xl flex flex-col items-center justify-center bg-surface-container-lowest/50">
                <span class="material-symbols-outlined text-outline text-3xl mb-2">cloud_upload</span>
                <p class="text-sm font-semibold text-on-surface">Awaiting Image Upload</p>
                <p class="text-xs text-outline mt-1">Please use the Streamlit file uploader above.</p>
            </div>

            <!-- Results Split-View: Empty State -->
            <div class="grid md:grid-cols-2 gap-6 items-stretch opacity-50 grayscale">
            <!-- Original Image Placeholder -->
            <div class="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
            <div class="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
            <span class="text-xs font-bold text-on-surface-variant tracking-wider uppercase">Original Specimen</span>
            <span class="material-symbols-outlined text-emerald-800/40 text-sm">image</span>
            </div>
            <div class="aspect-square bg-surface-container-highest/50 relative flex items-center justify-center">
            <span class="material-symbols-outlined text-outline-variant" style="font-size: 4rem;">local_florist</span>
            </div>
            </div>
            <!-- Annotated Image Placeholder -->
            <div class="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
            <div class="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
            <span class="text-xs font-bold text-on-surface-variant tracking-wider uppercase">AI Inference Overlay</span>
            <span class="material-symbols-outlined text-emerald-800/40 text-sm">neurology</span>
            </div>
            <div class="aspect-square bg-surface-container-highest/50 relative flex items-center justify-center">
            <span class="material-symbols-outlined text-outline-variant" style="font-size: 4rem;">memory</span>
            </div>
            </div>
            </div>
            </div>
            <!-- Right Side: Diagnosis Panel: Empty State -->
            <div class="lg:col-span-4 opacity-50 grayscale">
            <div class="sticky top-24 bg-surface-container-lowest rounded-xl shadow-[0_12px_32px_-4px_rgba(28,27,27,0.06)] p-6 border border-outline-variant/5">
            <div class="flex items-center justify-between mb-8">
            <h2 class="text-sm font-black text-on-surface-variant uppercase tracking-widest">Diagnosis Results</h2>
            <span class="material-symbols-outlined text-primary">analytics</span>
            </div>
            <div class="space-y-6">
            <!-- Disease Name -->
            <div>
            <label class="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter">Detected Pathology</label>
            <h3 class="text-3xl font-black text-on-surface font-headline leading-none mt-1">Pending Scan</h3>
            <p class="text-sm text-on-surface-variant mt-2">Awaiting Image Input</p>
            </div>
            <!-- Confidence -->
            <div class="bg-surface-container-low rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
            <span class="text-sm font-bold text-on-surface">Confidence Score</span>
            <span class="text-xl font-black text-outline font-headline">0.0%</span>
            </div>
            <div class="w-full h-2 bg-outline-variant/20 rounded-full overflow-hidden">
            </div>
            </div>
            <!-- Severity Badges -->
            <div>
            <label class="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter mb-3 block">Condition Severity</label>
            <div class="flex flex-wrap gap-2">
            <div class="px-4 py-1.5 rounded-full bg-outline-variant/20 text-outline text-xs font-bold flex items-center gap-1">
                Unknown
            </div>
            </div>
            </div>
            </div>
            </div>
            </div>
            </div>
            </div>
            </body></html>
            '''
            components.html(empty_html_string, height=850, scrolling=True)
elif nav_selection == 'Scan History':
    db = SessionLocal()
    logs = db.query(ScanLog).options(joinedload(ScanLog.detections)).order_by(ScanLog.timestamp.desc()).limit(12).all()
    db.close()

    history_html_string = """<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8">
<meta content="width=device-width, initial-scale=1.0" name="viewport">
<title>Scan History - AgriScan Pro</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet">
<script id="tailwind-config">
      tailwind.config = {
        darkMode: "class",
        theme: {
          extend: {
            colors: {
              "tertiary-fixed-dim": "#f5b7b4",
              "on-tertiary-fixed-variant": "#673a39",
              "secondary-fixed-dim": "#95d4b3",
              "surface-container-low": "#f6f3f2",
              "tertiary": "#401b1b",
              "on-primary-fixed": "#002114",
              "on-tertiary": "#ffffff",
              "on-error-container": "#93000a",
              "on-background": "#1c1b1b",
              "error": "#ba1a1a",
              "outline": "#717973",
              "secondary-container": "#aeeecb",
              "primary-fixed-dim": "#a5d0b9",
              "on-tertiary-container": "#d29895",
              "surface-container": "#f0eded",
              "on-primary": "#ffffff",
              "on-secondary-fixed": "#002114",
              "surface-variant": "#e5e2e1",
              "on-surface-variant": "#414844",
              "primary": "#012d1d",
              "tertiary-fixed": "#ffdad8",
              "on-secondary": "#ffffff",
              "inverse-on-surface": "#f3f0ef",
              "surface-container-highest": "#e5e2e1",
              "secondary": "#2c694e",
              "inverse-surface": "#313030",
              "surface-bright": "#fcf9f8",
              "surface": "#fcf9f8",
              "on-primary-fixed-variant": "#274e3d",
              "outline-variant": "#c1c8c2",
              "tertiary-container": "#5a302f",
              "surface-tint": "#3f6653",
              "error-container": "#ffdad6",
              "on-error": "#ffffff",
              "surface-dim": "#dcd9d9",
              "primary-container": "#1b4332",
              "on-surface": "#1c1b1b",
              "primary-fixed": "#c1ecd4",
              "on-secondary-container": "#316e52",
              "inverse-primary": "#a5d0b9",
              "secondary-fixed": "#b1f0ce",
              "surface-container-lowest": "#ffffff",
              "on-tertiary-fixed": "#331111",
              "on-secondary-fixed-variant": "#0e5138",
              "background": "#fcf9f8"
            },
            fontFamily: {
              "headline": ["Manrope"],
              "body": ["Inter"],
              "label": ["Inter"]
            },
            borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px"},
          },
        },
      }
    </script>
<style>
      .material-symbols-outlined {
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
      }
      body {
        font-family: 'Inter', sans-serif;
      }
      h1, h2, h3 {
        font-family: 'Manrope', sans-serif;
      }
    </style>
<style>*, ::before, ::after{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }::backdrop{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }/* ! tailwindcss v3.4.17 | MIT License | https://tailwindcss.com */*,::after,::before{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}::after,::before{--tw-content:''}:host,html{line-height:1.5;-webkit-text-size-adjust:100%;-moz-tab-size:4;tab-size:4;font-family:ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";font-feature-settings:normal;font-variation-settings:normal;-webkit-tap-highlight-color:transparent}body{margin:0;line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,pre,samp{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;font-feature-settings:normal;font-variation-settings:normal;font-size:1em}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}button,input,optgroup,select,textarea{font-family:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-size:100%;font-weight:inherit;line-height:inherit;letter-spacing:inherit;color:inherit;margin:0;padding:0}button,select{text-transform:none}button,input:where([type=button]),input:where([type=reset]),input:where([type=submit]){-webkit-appearance:button;background-color:transparent;background-image:none}:-moz-focusring{outline:auto}:-moz-ui-invalid{box-shadow:none}progress{vertical-align:baseline}::-webkit-inner-spin-button,::-webkit-outer-spin-button{height:auto}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}summary{display:list-item}blockquote,dd,dl,figure,h1,h2,h3,h4,h5,h6,hr,p,pre{margin:0}fieldset{margin:0;padding:0}legend{padding:0}menu,ol,ul{list-style:none;margin:0;padding:0}dialog{padding:0}textarea{resize:vertical}input::placeholder,textarea::placeholder{opacity:1;color:#9ca3af}[role=button],button{cursor:pointer}:disabled{cursor:default}audio,canvas,embed,iframe,img,object,svg,video{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}[hidden]:where(:not([hidden=until-found])){display:none}[type='text'],input:where(:not([type])),[type='email'],[type='url'],[type='password'],[type='number'],[type='date'],[type='datetime-local'],[type='month'],[type='search'],[type='tel'],[type='time'],[type='week'],[multiple],textarea,select{-webkit-appearance:none;appearance:none;background-color:#fff;border-color:#6b7280;border-width:1px;border-radius:0px;padding-top:0.5rem;padding-right:0.75rem;padding-bottom:0.5rem;padding-left:0.75rem;font-size:1rem;line-height:1.5rem;--tw-shadow:0 0 #0000;}[type='text']:focus, input:where(:not([type])):focus, [type='email']:focus, [type='url']:focus, [type='password']:focus, [type='number']:focus, [type='date']:focus, [type='datetime-local']:focus, [type='month']:focus, [type='search']:focus, [type='tel']:focus, [type='time']:focus, [type='week']:focus, [multiple]:focus, textarea:focus, select:focus{outline:2px solid transparent;outline-offset:2px;--tw-ring-inset:var(--tw-empty,/*!*/ /*!*/);--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:#2563eb;--tw-ring-offset-shadow:var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);--tw-ring-shadow:var(--tw-ring-inset) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color);box-shadow:var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow);border-color:#2563eb}input::placeholder,textarea::placeholder{color:#6b7280;opacity:1}::-webkit-datetime-edit-fields-wrapper{padding:0}::-webkit-date-and-time-value{min-height:1.5em;text-align:inherit}::-webkit-datetime-edit{display:inline-flex}::-webkit-datetime-edit,::-webkit-datetime-edit-year-field,::-webkit-datetime-edit-month-field,::-webkit-datetime-edit-day-field,::-webkit-datetime-edit-hour-field,::-webkit-datetime-edit-minute-field,::-webkit-datetime-edit-second-field,::-webkit-datetime-edit-millisecond-field,::-webkit-datetime-edit-meridiem-field{padding-top:0;padding-bottom:0}select{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");background-position:right 0.5rem center;background-repeat:no-repeat;background-size:1.5em 1.5em;padding-right:2.5rem;print-color-adjust:exact}[multiple],[size]:where(select:not([size="1"])){background-image:initial;background-position:initial;background-repeat:unset;background-size:initial;padding-right:0.75rem;print-color-adjust:unset}[type='checkbox'],[type='radio']{-webkit-appearance:none;appearance:none;padding:0;print-color-adjust:exact;display:inline-block;vertical-align:middle;background-origin:border-box;-webkit-user-select:none;user-select:none;flex-shrink:0;height:1rem;width:1rem;color:#2563eb;background-color:#fff;border-color:#6b7280;border-width:1px;--tw-shadow:0 0 #0000}[type='checkbox']{border-radius:0px}[type='radio']{border-radius:100%}[type='checkbox']:focus,[type='radio']:focus{outline:2px solid transparent;outline-offset:2px;--tw-ring-inset:var(--tw-empty,/*!*/ /*!*/);--tw-ring-offset-width:2px;--tw-ring-offset-color:#fff;--tw-ring-color:#2563eb;--tw-ring-offset-shadow:var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);--tw-ring-shadow:var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);box-shadow:var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}[type='checkbox']:checked,[type='radio']:checked{border-color:transparent;background-color:currentColor;background-size:100% 100%;background-position:center;background-repeat:no-repeat}[type='checkbox']:checked{background-image:url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");}@media (forced-colors: active) {[type='checkbox']:checked{-webkit-appearance:auto;appearance:auto}}[type='radio']:checked{background-image:url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3ccircle cx='8' cy='8' r='3'/%3e%3c/svg%3e");}@media (forced-colors: active) {[type='radio']:checked{-webkit-appearance:auto;appearance:auto}}[type='checkbox']:checked:hover,[type='checkbox']:checked:focus,[type='radio']:checked:hover,[type='radio']:checked:focus{border-color:transparent;background-color:currentColor}[type='checkbox']:indeterminate{background-image:url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 16 16'%3e%3cpath stroke='white' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M4 8h8'/%3e%3c/svg%3e");border-color:transparent;background-color:currentColor;background-size:100% 100%;background-position:center;background-repeat:no-repeat;}@media (forced-colors: active) {[type='checkbox']:indeterminate{-webkit-appearance:auto;appearance:auto}}[type='checkbox']:indeterminate:hover,[type='checkbox']:indeterminate:focus{border-color:transparent;background-color:currentColor}[type='file']{background:unset;border-color:inherit;border-width:0;border-radius:0;padding:0;font-size:unset;line-height:inherit}[type='file']:focus{outline:1px solid ButtonText;outline:1px auto -webkit-focus-ring-color}.fixed{position:fixed}.absolute{position:absolute}.relative{position:relative}.sticky{position:sticky}.left-0{left:0px}.left-3{left:0.75rem}.right-0{right:0px}.top-0{top:0px}.top-1\/2{top:50%}.z-30{z-index:30}.z-40{z-index:40}.mx-auto{margin-left:auto;margin-right:auto}.mb-1{margin-bottom:0.25rem}.mb-4{margin-bottom:1rem}.mb-8{margin-bottom:2rem}.ml-0{margin-left:0px}.ml-64{margin-left:16rem}.mt-12{margin-top:3rem}.mt-2{margin-top:0.5rem}.mt-4{margin-top:1rem}.mt-auto{margin-top:auto}.flex{display:flex}.grid{display:grid}.hidden{display:none}.aspect-video{aspect-ratio:16 / 9}.h-1\.5{height:0.375rem}.h-10{height:2.5rem}.h-16{height:4rem}.h-8{height:2rem}.h-full{height:100%}.h-screen{height:100vh}.min-h-screen{min-height:100vh}.w-1\.5{width:0.375rem}.w-10{width:2.5rem}.w-64{width:16rem}.w-8{width:2rem}.w-full{width:100%}.max-w-7xl{max-width:80rem}.flex-1{flex:1 1 0%}.-translate-y-1\/2{--tw-translate-y:-50%;transform:translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y))}.grid-cols-1{grid-template-columns:repeat(1, minmax(0, 1fr))}.flex-col{flex-direction:column}.items-start{align-items:flex-start}.items-center{align-items:center}.justify-center{justify-content:center}.justify-between{justify-content:space-between}.gap-1{gap:0.25rem}.gap-3{gap:0.75rem}.gap-4{gap:1rem}.gap-6{gap:1.5rem}.space-y-2 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.5rem * var(--tw-space-y-reverse))}.overflow-hidden{overflow:hidden}.rounded-full{border-radius:9999px}.rounded-lg{border-radius:0.5rem}.rounded-xl{border-radius:0.75rem}.border-b-2{border-bottom-width:2px}.border-r-0{border-right-width:0px}.border-r-4{border-right-width:4px}.border-t{border-top-width:1px}.border-none{border-style:none}.border-emerald-400{--tw-border-opacity:1;border-color:rgb(52 211 153 / var(--tw-border-opacity, 1))}.border-emerald-800{--tw-border-opacity:1;border-color:rgb(6 95 70 / var(--tw-border-opacity, 1))}.border-emerald-900\/20{border-color:rgb(6 78 59 / 0.2)}.border-surface-variant\/20{border-color:rgb(229 226 225 / 0.2)}.bg-emerald-800{--tw-bg-opacity:1;background-color:rgb(6 95 70 / var(--tw-bg-opacity, 1))}.bg-emerald-950\/70{background-color:rgb(2 44 34 / 0.7)}.bg-error{--tw-bg-opacity:1;background-color:rgb(186 26 26 / var(--tw-bg-opacity, 1))}.bg-error-container\/40{background-color:rgb(255 218 214 / 0.4)}.bg-primary{--tw-bg-opacity:1;background-color:rgb(1 45 29 / var(--tw-bg-opacity, 1))}.bg-primary-fixed-dim{--tw-bg-opacity:1;background-color:rgb(165 208 185 / var(--tw-bg-opacity, 1))}.bg-primary-fixed\/40{background-color:rgb(193 236 212 / 0.4)}.bg-secondary{--tw-bg-opacity:1;background-color:rgb(44 105 78 / var(--tw-bg-opacity, 1))}.bg-secondary-container\/40{background-color:rgb(174 238 203 / 0.4)}.bg-stone-50\/80{background-color:rgb(250 250 249 / 0.8)}.bg-surface{--tw-bg-opacity:1;background-color:rgb(252 249 248 / var(--tw-bg-opacity, 1))}.bg-surface-container{--tw-bg-opacity:1;background-color:rgb(240 237 237 / var(--tw-bg-opacity, 1))}.bg-surface-container-highest{--tw-bg-opacity:1;background-color:rgb(229 226 225 / var(--tw-bg-opacity, 1))}.bg-surface-container-low{--tw-bg-opacity:1;background-color:rgb(246 243 242 / var(--tw-bg-opacity, 1))}.bg-surface-container-lowest{--tw-bg-opacity:1;background-color:rgb(255 255 255 / var(--tw-bg-opacity, 1))}.bg-tertiary-container{--tw-bg-opacity:1;background-color:rgb(90 48 47 / var(--tw-bg-opacity, 1))}.bg-tertiary-fixed\/40{background-color:rgb(255 218 216 / 0.4)}.object-cover{object-fit:cover}.p-2{padding:0.5rem}.p-5{padding:1.25rem}.p-6{padding:1.5rem}.px-2{padding-left:0.5rem;padding-right:0.5rem}.px-3{padding-left:0.75rem;padding-right:0.75rem}.px-4{padding-left:1rem;padding-right:1rem}.px-8{padding-left:2rem;padding-right:2rem}.py-1{padding-top:0.25rem;padding-bottom:0.25rem}.py-1\.5{padding-top:0.375rem;padding-bottom:0.375rem}.py-10{padding-top:2.5rem;padding-bottom:2.5rem}.py-3{padding-top:0.75rem;padding-bottom:0.75rem}.pb-1{padding-bottom:0.25rem}.pl-10{padding-left:2.5rem}.pl-4{padding-left:1rem}.pr-4{padding-right:1rem}.pt-4{padding-top:1rem}.font-body{font-family:Inter}.font-headline{font-family:Manrope}.text-3xl{font-size:1.875rem;line-height:2.25rem}.text-\[10px\]{font-size:10px}.text-base{font-size:1rem;line-height:1.5rem}.text-lg{font-size:1.125rem;line-height:1.75rem}.text-sm{font-size:0.875rem;line-height:1.25rem}.text-xl{font-size:1.25rem;line-height:1.75rem}.text-xs{font-size:0.75rem;line-height:1rem}.font-black{font-weight:900}.font-bold{font-weight:700}.font-extrabold{font-weight:800}.font-medium{font-weight:500}.font-semibold{font-weight:600}.uppercase{text-transform:uppercase}.tracking-tight{letter-spacing:-0.025em}.tracking-wide{letter-spacing:0.025em}.tracking-wider{letter-spacing:0.05em}.text-emerald-100\/50{color:rgb(209 250 229 / 0.5)}.text-emerald-100\/60{color:rgb(209 250 229 / 0.6)}.text-emerald-400{--tw-text-opacity:1;color:rgb(52 211 153 / var(--tw-text-opacity, 1))}.text-emerald-50{--tw-text-opacity:1;color:rgb(236 253 245 / var(--tw-text-opacity, 1))}.text-emerald-800{--tw-text-opacity:1;color:rgb(6 95 70 / var(--tw-text-opacity, 1))}.text-emerald-900{--tw-text-opacity:1;color:rgb(6 78 59 / var(--tw-text-opacity, 1))}.text-error{--tw-text-opacity:1;color:rgb(186 26 26 / var(--tw-text-opacity, 1))}.text-on-primary{--tw-text-opacity:1;color:rgb(255 255 255 / var(--tw-text-opacity, 1))}.text-on-primary-fixed-variant{--tw-text-opacity:1;color:rgb(39 78 61 / var(--tw-text-opacity, 1))}.text-on-surface{--tw-text-opacity:1;color:rgb(28 27 27 / var(--tw-text-opacity, 1))}.text-on-surface-variant{--tw-text-opacity:1;color:rgb(65 72 68 / var(--tw-text-opacity, 1))}.text-primary{--tw-text-opacity:1;color:rgb(1 45 29 / var(--tw-text-opacity, 1))}.text-secondary{--tw-text-opacity:1;color:rgb(44 105 78 / var(--tw-text-opacity, 1))}.text-stone-500{--tw-text-opacity:1;color:rgb(120 113 108 / var(--tw-text-opacity, 1))}.text-tertiary-container{--tw-text-opacity:1;color:rgb(90 48 47 / var(--tw-text-opacity, 1))}.shadow-2xl{--tw-shadow:0 25px 50px -12px rgb(0 0 0 / 0.25);--tw-shadow-colored:0 25px 50px -12px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-\[0_12px_32px_-4px_rgba\(28\2c 27\2c 27\2c 0\.06\)\]{--tw-shadow:0 12px 32px -4px rgba(28,27,27,0.06);--tw-shadow-colored:0 12px 32px -4px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-lg{--tw-shadow:0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);--tw-shadow-colored:0 10px 15px -3px var(--tw-shadow-color), 0 4px 6px -4px var(--tw-shadow-color);box-shadow:var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow)}.shadow-primary\/10{--tw-shadow-color:rgb(1 45 29 / 0.1);--tw-shadow:var(--tw-shadow-colored)}.backdrop-blur-md{--tw-backdrop-blur:blur(12px);-webkit-backdrop-filter:var(--tw-backdrop-blur) var(--tw-backdrop-brightness) var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale) var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert) var(--tw-backdrop-opacity) var(--tw-backdrop-saturate) var(--tw-backdrop-sepia);backdrop-filter:var(--tw-backdrop-blur) var(--tw-backdrop-brightness) var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale) var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert) var(--tw-backdrop-opacity) var(--tw-backdrop-saturate) var(--tw-backdrop-sepia)}.backdrop-blur-xl{--tw-backdrop-blur:blur(24px);-webkit-backdrop-filter:var(--tw-backdrop-blur) var(--tw-backdrop-brightness) var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale) var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert) var(--tw-backdrop-opacity) var(--tw-backdrop-saturate) var(--tw-backdrop-sepia);backdrop-filter:var(--tw-backdrop-blur) var(--tw-backdrop-brightness) var(--tw-backdrop-contrast) var(--tw-backdrop-grayscale) var(--tw-backdrop-hue-rotate) var(--tw-backdrop-invert) var(--tw-backdrop-opacity) var(--tw-backdrop-saturate) var(--tw-backdrop-sepia)}.transition-all{transition-property:all;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.transition-colors{transition-property:color, background-color, border-color, fill, stroke, -webkit-text-decoration-color;transition-property:color, background-color, border-color, text-decoration-color, fill, stroke;transition-property:color, background-color, border-color, text-decoration-color, fill, stroke, -webkit-text-decoration-color;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.transition-transform{transition-property:transform;transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1);transition-duration:150ms}.duration-300{transition-duration:300ms}.duration-500{transition-duration:500ms}.ease-in-out{transition-timing-function:cubic-bezier(0.4, 0, 0.2, 1)}.hover\:scale-\[1\.01\]:hover{--tw-scale-x:1.01;--tw-scale-y:1.01;transform:translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y))}.hover\:bg-emerald-800\/40:hover{background-color:rgb(6 95 70 / 0.4)}.hover\:bg-primary-container:hover{--tw-bg-opacity:1;background-color:rgb(27 67 50 / var(--tw-bg-opacity, 1))}.hover\:bg-stone-100:hover{--tw-bg-opacity:1;background-color:rgb(245 245 244 / var(--tw-bg-opacity, 1))}.hover\:text-emerald-100:hover{--tw-text-opacity:1;color:rgb(209 250 229 / var(--tw-text-opacity, 1))}.hover\:text-emerald-700:hover{--tw-text-opacity:1;color:rgb(4 120 87 / var(--tw-text-opacity, 1))}.focus\:ring-2:focus{--tw-ring-offset-shadow:var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);--tw-ring-shadow:var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);box-shadow:var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000)}.focus\:ring-primary:focus{--tw-ring-opacity:1;--tw-ring-color:rgb(1 45 29 / var(--tw-ring-opacity, 1))}.group:hover .group-hover\:scale-105{--tw-scale-x:1.05;--tw-scale-y:1.05;transform:translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y))}.dark\:border-emerald-300:is(.dark *){--tw-border-opacity:1;border-color:rgb(110 231 183 / var(--tw-border-opacity, 1))}.dark\:bg-emerald-950\/80:is(.dark *){background-color:rgb(2 44 34 / 0.8)}.dark\:bg-stone-900\/80:is(.dark *){background-color:rgb(28 25 23 / 0.8)}.dark\:text-emerald-100:is(.dark *){--tw-text-opacity:1;color:rgb(209 250 229 / var(--tw-text-opacity, 1))}.dark\:text-emerald-300:is(.dark *){--tw-text-opacity:1;color:rgb(110 231 183 / var(--tw-text-opacity, 1))}.dark\:text-emerald-50:is(.dark *){--tw-text-opacity:1;color:rgb(236 253 245 / var(--tw-text-opacity, 1))}.dark\:text-stone-400:is(.dark *){--tw-text-opacity:1;color:rgb(168 162 158 / var(--tw-text-opacity, 1))}.dark\:hover\:bg-stone-800:hover:is(.dark *){--tw-bg-opacity:1;background-color:rgb(41 37 36 / var(--tw-bg-opacity, 1))}@media (min-width: 640px){.sm\:block{display:block}}@media (min-width: 768px){.md\:flex{display:flex}.md\:grid-cols-2{grid-template-columns:repeat(2, minmax(0, 1fr))}}@media (min-width: 1024px){.lg\:grid-cols-3{grid-template-columns:repeat(3, minmax(0, 1fr))}}</style></head>
<body class="bg-surface text-on-surface" data-mode="connect">
<div class="px-8 py-10">
<div class="max-w-7xl mx-auto">
<div class="mb-8">
<h2 class="text-3xl font-extrabold text-primary tracking-tight font-headline">Scan History</h2>
<p class="text-on-surface-variant font-body mt-2">Review past AI detections and crop health logs.</p>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
"""

    for scan in logs:
        if scan.detections:
            detection = scan.detections[0]
            formatted_label = detection.class_label.replace('_', ' ').title()
            confidence = (detection.confidence_score or 0.0) * 100
            severity_grade = detection.severity_grade or 'Unknown'
        else:
            formatted_label = "Healthy"
            confidence = 100.0
            severity_grade = "Optimal"
            
        formatted_date = scan.timestamp.strftime("%b %d, %Y - %H:%M").upper() if scan.timestamp else "UNKNOWN"
        
        base64_string = ""
        if scan.image_path and os.path.exists(scan.image_path):
            try:
                with open(scan.image_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read()).decode('utf-8')
            except Exception:
                pass
                
        sg_lower = severity_grade.lower()
        if sg_lower == 'severe':
            badge_bg = "bg-error-container/40"
            badge_text = "text-error"
            dot_color = "bg-error"
        elif sg_lower == 'moderate':
            badge_bg = "bg-tertiary-fixed/40"
            badge_text = "text-tertiary-container"
            dot_color = "bg-tertiary-container"
        elif sg_lower == 'mild':
            badge_bg = "bg-primary-fixed/40"
            badge_text = "text-on-primary-fixed-variant"
            dot_color = "bg-primary-fixed-dim"
        else:
            badge_bg = "bg-secondary-container/40"
            badge_text = "text-secondary"
            dot_color = "bg-secondary"
            severity_grade = "Optimal" if sg_lower == 'healthy' else severity_grade

        card_html = f"""
<div class="bg-surface-container-lowest rounded-xl p-5 flex flex-col shadow-[0_12px_32px_-4px_rgba(28,27,27,0.06)] group hover:scale-[1.01] transition-all duration-300">
<div class="flex justify-between items-start mb-4">
<span class="text-[10px] font-semibold text-on-surface-variant tracking-wider bg-surface-container-low px-2 py-1 rounded-full uppercase">{formatted_date}</span>
<span class="px-3 py-1 rounded-full text-[10px] font-bold {badge_bg} {badge_text} flex items-center gap-1">
<span class="w-1.5 h-1.5 rounded-full {dot_color}"></span>
                                {severity_grade.upper()}
                            </span>
</div>
<div class="aspect-video w-full rounded-lg overflow-hidden mb-4 bg-surface-container">
<img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="data:image/jpeg;base64,{base64_string}">
</div>
<h3 class="text-xl font-bold text-on-surface mb-1">{formatted_label}</h3>
<div class="flex justify-between items-center mt-auto pt-4 border-t border-surface-variant/20">
<div class="flex flex-col">
<span class="text-[10px] text-on-surface-variant font-medium">Confidence Score</span>
<span class="text-sm font-bold text-primary">{confidence:.1f}%</span>
</div>
<button class="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-on-primary">
<span class="material-symbols-outlined text-sm" data-icon="chevron_right">chevron_right</span>
</button>
</div>
</div>
"""
        history_html_string += card_html

    history_html_string += """
</div>
</div>
</div>
</body></html>
"""

    components.html(history_html_string, height=900, scrolling=True)
