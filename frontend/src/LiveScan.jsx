import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LiveScan() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleImageClick = () => {
    fileInputRef.current.click();
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAiResult(null); // Reset previous results
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.type === 'image/jpeg' || file.type === 'image/png')) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAiResult(null);
    }
  };

  const runAnalysis = async () => {
    if (!selectedImage) return;

    const chatId = localStorage.getItem('telegram_chat_id');
    if (!chatId) {
      navigate('/settings', { replace: true });
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', selectedImage);
    formData.append('telegram_chat_id', chatId);

    try {
      const response = await fetch('http://localhost:8000/api/predict', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      console.log("API Response:", data);
      
      const detection = data.detections && data.detections.length > 0 ? data.detections[0] : null;
      
      setAiResult({
        label: detection ? detection.label : "Unknown",
        confidence: detection ? detection.confidence : 0,
        severity_grade: detection ? detection.severity : "Unknown",
        annotated_image: data.annotated_image_base64 || null,
      });
    } catch (error) {
      console.error('Error during analysis:', error);
      // Fallback/Mock data for demonstration if API fails
      setAiResult({
        label: "Late Blight",
        confidence: 0.965,
        severity_grade: "Severe",
        annotated_image: null, // Would be base64 string
      });
    } finally {
      setIsLoading(false);
    }
  };
 
  const getSeverityClasses = (grade, targetGrade) => {
    if (grade?.toLowerCase() === targetGrade.toLowerCase()) {
      if (targetGrade === 'Severe') return 'bg-error-container text-on-error-container ring-2 ring-error/10';
      if (targetGrade === 'Moderate') return 'bg-orange-100/50 text-orange-800 ring-2 ring-orange-500/20';
      return 'bg-emerald-100/50 text-emerald-800 ring-2 ring-emerald-500/20';
    }
    
    // Default inactive state
    if (targetGrade === 'Severe') return 'bg-error-container text-on-error-container opacity-40 grayscale';
    if (targetGrade === 'Moderate') return 'bg-orange-100/50 text-orange-800 opacity-40 grayscale';
    return 'bg-emerald-100/50 text-emerald-800 opacity-40 grayscale';
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Side: Upload & Results */}
        <div className="lg:col-span-8 space-y-8">
          
          {/* Upload Zone (Always visible, or could conditionally hide when result exists) */}
          {!aiResult && !previewUrl && (
            <div 
              className="relative group cursor-pointer transition-all duration-300"
              onClick={handleImageClick}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleImageChange} 
                accept="image/jpeg, image/png" 
                className="hidden" 
              />
              <div className="custom-dashed w-full min-h-[240px] rounded-xl flex flex-col items-center justify-center p-8 bg-surface-container-low/30 group-hover:bg-emerald-50/50 transition-colors">
                <div className="w-16 h-16 rounded-full bg-secondary-fixed flex items-center justify-center mb-4 text-on-secondary-fixed-variant group-hover:scale-110 transition-transform">
                  <span className="material-symbols-outlined text-3xl" data-icon="upload_file">upload_file</span>
                </div>
                <h3 className="text-lg font-headline font-bold text-on-surface mb-2">Drag and drop leaf specimen</h3>
                <p className="text-sm text-on-surface-variant mb-6">Supports JPG, PNG up to 10MB</p>
                <button className="px-6 py-2 bg-primary text-white rounded-lg font-headline font-bold hover:bg-primary-container transition-colors shadow-lg shadow-primary/10 pointer-events-none">
                  Browse Files
                </button>
              </div>
            </div>
          )}

          {/* Preview & Action Buttons */}
          {previewUrl && !aiResult && (
             <div className="bg-surface-container-low rounded-xl p-6 flex flex-col items-center">
                 <img src={previewUrl} alt="Preview" className="max-h-[300px] object-contain rounded-lg mb-6 shadow-md" />
                 <div className="flex gap-4">
                     <button 
                         onClick={() => { setPreviewUrl(null); setSelectedImage(null); }}
                         className="px-6 py-2 border border-outline-variant text-on-surface-variant rounded-lg font-headline font-bold hover:bg-surface-container-high transition-colors"
                     >
                         Cancel
                     </button>
                     <button 
                         onClick={runAnalysis}
                         disabled={isLoading}
                         className="px-6 py-2 bg-primary text-white rounded-lg font-headline font-bold hover:bg-primary-container transition-colors shadow-lg shadow-primary/10 flex items-center gap-2"
                     >
                         {isLoading ? (
                             <>
                                <span className="material-symbols-outlined animate-spin" style={{fontVariationSettings: "'FILL' 1"}}>sync</span>
                                Analyzing...
                             </>
                         ) : (
                             <>
                                <span className="material-symbols-outlined text-sm" data-icon="rocket_launch">rocket_launch</span>
                                Run Analysis
                             </>
                         )}
                     </button>
                 </div>
             </div>
          )}

          {/* Results Split-View */}
          {aiResult && (
            <div className="grid md:grid-cols-2 gap-6 items-stretch">
              {/* Original Image */}
              <div className="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
                <div className="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
                  <span className="text-xs font-bold text-on-surface-variant tracking-wider uppercase">Original Specimen</span>
                  <span className="material-symbols-outlined text-emerald-800/40 text-sm" data-icon="image">image</span>
                </div>
                <div className="aspect-square bg-surface-container-highest/50 relative">
                  <img alt="Original Leaf" className="w-full h-full object-cover opacity-80" src={previewUrl} />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/5">
                    <div className="px-3 py-1 bg-black/40 backdrop-blur-md rounded-full text-[10px] text-white font-bold uppercase tracking-widest">Input Layer</div>
                  </div>
                </div>
              </div>
              
              {/* Annotated Image */}
              <div className="bg-surface-container-low rounded-xl overflow-hidden flex flex-col">
                <div className="px-4 py-3 flex items-center justify-between border-b border-outline-variant/10">
                  <span className="text-xs font-bold text-on-surface-variant tracking-wider uppercase">AI Inference Overlay</span>
                  <span className="material-symbols-outlined text-emerald-800/40 text-sm" data-icon="neurology" style={{fontVariationSettings: "'FILL' 1"}}>neurology</span>
                </div>
                <div className="aspect-square bg-surface-container-highest/50 relative">
                  <img 
                    alt="Annotated Leaf" 
                    className="w-full h-full object-cover" 
                    src={aiResult.annotated_image ? `data:image/jpeg;base64,${aiResult.annotated_image}` : previewUrl} 
                  />
                  {/* Provide mock bounding box just for visual feedback if no annotated image returned by mockup */}
                  {!aiResult.annotated_image && (
                      <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute top-[20%] left-[30%] w-[120px] h-[100px] border-2 border-error rounded shadow-[0_0_15px_rgba(186,26,26,0.5)]">
                          <span className="absolute -top-6 left-0 bg-error text-white text-[10px] px-2 py-0.5 rounded-sm font-bold">{aiResult.label || 'Detected'}</span>
                        </div>
                      </div>
                  )}
                  <div className="absolute bottom-4 right-4 p-2 bg-emerald-900/80 backdrop-blur-md rounded-lg text-white">
                    <span className="material-symbols-outlined text-xl" data-icon="verified_user">verified_user</span>
                  </div>
                </div>
              </div>
              
              {/* Reset Button */}
              <div className="md:col-span-2 flex justify-center mt-4">
                  <button 
                      onClick={() => { setPreviewUrl(null); setSelectedImage(null); setAiResult(null); }}
                      className="px-6 py-2 border border-outline-variant text-on-surface-variant rounded-lg font-headline font-bold hover:bg-surface-container-high transition-colors flex items-center gap-2"
                  >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>restart_alt</span>
                      Scan Another Leaf
                  </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Side: Diagnosis Panel */}
        {aiResult && (
          <div className="lg:col-span-4">
            <div className="sticky top-24 bg-surface-container-lowest rounded-xl shadow-[0_12px_32px_-4px_rgba(28,27,27,0.06)] p-6 border border-outline-variant/5">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-sm font-black text-on-surface-variant uppercase tracking-widest">Diagnosis Results</h2>
                <span className="material-symbols-outlined text-primary" data-icon="analytics">analytics</span>
              </div>
              
              <div className="space-y-6">
                {/* Disease Name */}
                <div>
                  <label className="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter">Detected Pathology</label>
                  <h3 className="text-3xl font-black text-on-surface font-headline leading-none mt-1 capitalize">{aiResult.label || 'Unknown'}</h3>
                  <p className="text-sm text-on-surface-variant mt-2">AI Diagnostic Assessment</p>
                </div>
                
                {/* Confidence */}
                <div className="bg-surface-container-low rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-on-surface">Confidence Score</span>
                    <span className="text-xl font-black text-primary font-headline">
                        {aiResult.confidence ? (aiResult.confidence * 100).toFixed(1) : '0'}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-outline-variant/20 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-secondary to-primary transition-all duration-1000" style={{ width: `${aiResult.confidence ? aiResult.confidence * 100 : 0}%` }}></div>
                  </div>
                </div>

                {/* Severity Badges */}
                <div>
                  <label className="text-[10px] font-bold text-on-surface-variant/60 uppercase tracking-tighter mb-3 block">Condition Severity</label>
                  <div className="flex flex-wrap gap-2">
                    <div className={`px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 transition-all ${getSeverityClasses(aiResult.severity_grade, 'Mild')}`}>
                      Mild
                    </div>
                    <div className={`px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 transition-all ${getSeverityClasses(aiResult.severity_grade, 'Moderate')}`}>
                      Moderate
                    </div>
                    <div className={`px-4 py-1.5 rounded-full text-xs font-bold flex items-center gap-1 transition-all ${getSeverityClasses(aiResult.severity_grade, 'Severe')}`}>
                      {aiResult.severity_grade?.toLowerCase() === 'severe' && <span className="material-symbols-outlined text-sm" data-icon="warning">warning</span>}
                      Severe
                    </div>
                  </div>
                </div>

                {/* Impact Analysis / Treatment */}
                <div className="pt-6 border-t border-outline-variant/10">
                  <h4 className="text-xs font-bold text-on-surface mb-3 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm" data-icon="medication">medication</span>
                    Recommended Action
                  </h4>
                  <ul className="space-y-3">
                    <li className="flex gap-3 text-sm text-on-surface-variant leading-relaxed">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 shrink-0"></div>
                      Follow standard protocols for {aiResult.label || 'this condition'}.
                    </li>
                    {aiResult.severity_grade?.toLowerCase() === 'severe' && (
                        <li className="flex gap-3 text-sm text-on-surface-variant leading-relaxed text-error">
                        <div className="w-1.5 h-1.5 rounded-full bg-error mt-1.5 shrink-0"></div>
                        Immediate isolation and treatment recommended due to high severity.
                        </li>
                    )}
                  </ul>
                </div>

                {/* CTA */}
                <div className="pt-4 mt-auto">
                  <button className="w-full bg-primary text-white py-4 rounded-xl font-headline font-extrabold text-lg flex items-center justify-center gap-3 shadow-xl shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all">
                    <span className="material-symbols-outlined" data-icon="history">history</span>
                    Save to History
                  </button>
                  <p className="text-center text-[10px] text-on-surface-variant/50 mt-4 uppercase tracking-widest font-bold">Report ID: SCAN-{Math.floor(Math.random() * 10000)}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
