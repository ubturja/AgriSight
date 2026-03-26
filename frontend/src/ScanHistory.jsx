import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ScanHistory() {
  const [historyLogs, setHistoryLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const chatId = localStorage.getItem('telegram_chat_id');

  useEffect(() => {
    const fetchHistory = async () => {
      if (!chatId) {
        navigate('/settings', { replace: true });
        return;
      }
      try {
        const response = await fetch(`http://localhost:8000/api/history/${chatId}`, {
          cache: 'no-store',
        });
        if (response.ok) {
          const data = await response.json();
          setHistoryLogs(data);
        } else {
          throw new Error('Failed to fetch history');
        }
      } catch (error) {
        console.error('Error fetching history:', error);
        setHistoryLogs([]);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHistory();
  }, [chatId, navigate]);

  const getSeverityStyles = (severity) => {
    const s = severity?.toLowerCase();
    switch (s) {
      case 'severe':
        return {
          badge: 'bg-error-container/40 text-error',
          dot: 'bg-error',
          label: 'SEVERE'
        };
      case 'moderate':
        return {
          badge: 'bg-tertiary-fixed/40 text-tertiary-container',
          dot: 'bg-tertiary-container',
          label: 'MODERATE'
        };
      case 'mild':
        return {
          badge: 'bg-primary-fixed/40 text-on-primary-fixed-variant',
          dot: 'bg-primary-fixed-dim',
          label: 'MILD'
        };
      case 'healthy':
      case 'optimal':
        return {
          badge: 'bg-secondary-container/40 text-secondary',
          dot: 'bg-secondary',
          label: 'OPTIMAL'
        };
      default:
        return {
          badge: 'bg-surface-variant text-on-surface-variant',
          dot: 'bg-outline',
          label: severity?.toUpperCase() || 'UNKNOWN'
        };
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    const options = { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options).replace(',', ' -');
  };

  return (
    <div className="px-8 py-10">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-extrabold text-primary tracking-tight font-headline">Scan History</h2>
          <p className="text-on-surface-variant font-body mt-2">Review past AI detections and crop health logs.</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <span className="material-symbols-outlined animate-spin text-4xl text-primary" style={{fontVariationSettings: "'FILL' 1"}}>sync</span>
          </div>
        ) : historyLogs.length === 0 ? (
          <div className="text-center py-20 bg-surface-container-low rounded-xl">
             <span className="material-symbols-outlined text-4xl text-on-surface-variant/50 mb-2">history</span>
             <p className="text-on-surface-variant font-medium">No past scans found yet.</p>
          </div>
        ) : (
          <>
            {/* History Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {historyLogs.map((log) => {
                const detection = log.detections && log.detections.length > 0 ? log.detections[0] : null;
                const classLabel = detection ? detection.class_label : (log.class_label || 'Unknown Element');
                const severityGrade = detection ? detection.severity_grade : log.severity_grade;
                const confidenceScore = detection ? detection.confidence_score : log.confidence_score;
                
                const styles = getSeverityStyles(severityGrade);
                // Handle image dynamically - either base64 or a URL
                const imgSrc = log.image_base64 
                   ? `data:image/jpeg;base64,${log.image_base64}` 
                   : (log.image_url || `https://via.placeholder.com/300x200?text=${encodeURIComponent(classLabel)}`);

                return (
                  <div key={log.scan_id || log.id} className="bg-surface-container-lowest rounded-xl p-5 flex flex-col shadow-[0_12px_32px_-4px_rgba(28,27,27,0.06)] group hover:scale-[1.01] transition-all duration-300">
                    <div className="flex justify-between items-start mb-4">
                      <span className="text-[10px] font-semibold text-on-surface-variant tracking-wider bg-surface-container-low px-2 py-1 rounded-full uppercase">
                        {formatDate(log.timestamp)}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 ${styles.badge}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${styles.dot}`}></span>
                        {styles.label}
                      </span>
                    </div>
                    
                    <div className="aspect-video w-full rounded-lg overflow-hidden mb-4 bg-surface-container">
                      <img 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                        alt={classLabel} 
                        src={imgSrc} 
                      />
                    </div>
                    
                    <h3 className="text-xl font-bold text-on-surface mb-1 capitalize">{classLabel}</h3>
                    
                    <div className="flex justify-between items-center mt-auto pt-4 border-t border-surface-variant/20">
                      <div className="flex flex-col">
                        <span className="text-[10px] text-on-surface-variant font-medium">Confidence Score</span>
                        <span className="text-sm font-bold text-primary">
                          {confidenceScore ? (confidenceScore * 100).toFixed(1) : '0'}%
                        </span>
                      </div>
                      <button className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-on-primary">
                        <span className="material-symbols-outlined text-sm" data-icon="chevron_right">chevron_right</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination/Load More Footer */}
            <div className="mt-12 flex justify-center">
              <button className="px-8 py-3 bg-primary text-on-primary rounded-lg font-semibold hover:bg-primary-container transition-all shadow-lg shadow-primary/10">
                Load Previous Scans
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
