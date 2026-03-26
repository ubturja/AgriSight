import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Overview() {
  const [historyLogs, setHistoryLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      const chatId = localStorage.getItem('telegram_chat_id');
      if (!chatId) {
        navigate('/settings', { replace: true });
        return;
      }
      try {
        const response = await fetch(`http://localhost:8000/api/history/${chatId}`);
        if (response.ok) {
          const data = await response.json();
          setHistoryLogs(data);
        } else {
          throw new Error('Failed to fetch data');
        }
      } catch (err) {
        setError(err.message);
        console.error('Error fetching overview data:', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, [navigate]);

  const totalScans = historyLogs.length;
  
  const severeDetections = historyLogs.filter(log => {
      const detection = log.detections && log.detections.length > 0 ? log.detections[0] : null;
      if (!detection) return false;
      return detection.severity_grade?.toLowerCase() === 'severe';
  }).length;

  const healthyCrops = historyLogs.filter(log => {
      const detection = log.detections && log.detections.length > 0 ? log.detections[0] : null;
      if (!detection) return false;
      return detection.class_label?.toLowerCase() === 'healthy';
  }).length;
  
  const recentActivity = historyLogs.slice(0, 4);

  const formatDate = (isoString) => {
    if (!isoString) return 'Unknown Date';
    const date = new Date(isoString);
    const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center flex-col items-center py-20 px-6">
        <span className="material-symbols-outlined animate-spin text-4xl text-primary" style={{fontVariationSettings: "'FILL' 1"}}>sync</span>
        <p className="mt-4 text-on-surface-variant font-medium">Loading Overview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-20 px-6 max-w-7xl mx-auto text-center flex flex-col items-center">
        <div className="bg-error-container/20 text-error p-6 rounded-xl inline-flex flex-col items-center">
            <span className="material-symbols-outlined text-4xl mb-2">error</span>
            <p className="font-bold text-lg">Error loading data</p>
            <p className="text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Card 1: Total Scans */}
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary/20 text-primary flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{fontVariationSettings: "'FILL' 1"}}>qr_code_scanner</span>
            </div>
            <div>
                <p className="text-on-surface-variant text-sm font-semibold uppercase tracking-wider">Total Scans</p>
                <h3 className="text-3xl font-extrabold text-primary">{totalScans}</h3>
            </div>
        </div>

        {/* Card 2: Critical Alerts */}
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-error-container/40 text-error flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{fontVariationSettings: "'FILL' 1"}}>warning</span>
            </div>
            <div>
                <p className="text-on-surface-variant text-sm font-semibold uppercase tracking-wider">Severe Detections</p>
                <h3 className="text-3xl font-extrabold text-error">{severeDetections}</h3>
            </div>
        </div>

        {/* Card 3: Healthy Crops */}
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-secondary-container/40 text-secondary flex items-center justify-center">
                <span className="material-symbols-outlined text-2xl" style={{fontVariationSettings: "'FILL' 1"}}>psychiatry</span>
            </div>
            <div>
                <p className="text-on-surface-variant text-sm font-semibold uppercase tracking-wider">Healthy / Optimal</p>
                <h3 className="text-3xl font-extrabold text-secondary">{healthyCrops}</h3>
            </div>
        </div>

      </div>

      {/* Recent Activity */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm">
         <h2 className="text-xl font-bold text-on-surface mb-6 font-headline">Recent Activity</h2>
         {recentActivity.length === 0 ? (
             <p className="text-on-surface-variant">No recent activity found.</p>
         ) : (
             <div className="flex flex-col gap-4">
                 {recentActivity.map((log) => {
                     const detection = log.detections && log.detections.length > 0 ? log.detections[0] : null;
                     const classLabel = detection ? detection.class_label : (log.class_label || 'Unknown Element');
                     const severityGrade = detection ? detection.severity_grade : log.severity_grade;
                     
                     const s = severityGrade?.toLowerCase();
                     let severityClass = "bg-surface-variant text-on-surface-variant";
                     if (s === 'severe') severityClass = "bg-error-container/40 text-error";
                     else if (s === 'moderate') severityClass = "bg-tertiary-fixed/40 text-tertiary-container";
                     else if (s === 'mild') severityClass = "bg-primary-fixed/40 text-on-primary-fixed-variant";
                     else if (s === 'healthy' || s === 'optimal') severityClass = "bg-secondary-container/40 text-secondary";

                     return (
                         <div key={log.scan_id || log.id} className="flex items-center justify-between p-4 bg-surface-container-low rounded-xl transition-all duration-300 hover:bg-surface-container hover:-translate-y-0.5 shadow-sm">
                             <div className="flex items-center gap-4">
                               <div className="w-12 h-12 rounded-lg bg-surface-container-high overflow-hidden flex-shrink-0 border border-outline-variant/30">
                                  {log.image_base64 ? (
                                      <img src={`data:image/jpeg;base64,${log.image_base64}`} alt={classLabel} className="w-full h-full object-cover" />
                                  ) : log.image_url ? (
                                      <img src={log.image_url} alt={classLabel} className="w-full h-full object-cover" />
                                  ) : (
                                      <div className="w-full h-full bg-on-surface/5 flex items-center justify-center">
                                          <span className="material-symbols-outlined text-on-surface-variant text-lg">image</span>
                                      </div>
                                  )}
                               </div>
                               <div>
                                   <p className="font-bold text-on-surface capitalize">{classLabel}</p>
                                   <p className="text-[11px] text-on-surface-variant mt-0.5 tracking-wide uppercase font-semibold">{formatDate(log.timestamp)}</p>
                               </div>
                             </div>
                             
                             <div className={`px-3 py-1 rounded-full text-[10px] items-center gap-1 font-bold uppercase tracking-wider flex ${severityClass}`}>
                                 <span className={`w-1.5 h-1.5 rounded-full bg-current`}></span>
                                 {severityGrade || 'UNKNOWN'}
                             </div>
                         </div>
                     );
                 })}
             </div>
         )}
      </div>

    </div>
  );
}