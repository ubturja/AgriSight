import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Extract the head block to reuse
head_match = re.search(r'(<!DOCTYPE html><html class="light" lang="en"><head>.*?</head>)', content, re.DOTALL)
if head_match:
    head_html = head_match.group(1)
    
    # 2. Add an else block
    empty_html = f"""
        else:
            empty_html_string = f'''{head_html}
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
elif nav_selection == 'Scan History':"""

    content = content.replace("elif nav_selection == 'Scan History':", empty_html)
    
    with open("app.py", "w") as f:
        f.write(content)
    print("Patched app.py!")
else:
    print("Could not find head block")

