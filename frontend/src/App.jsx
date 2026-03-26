import { useState } from 'react';
import LiveScan from './LiveScan';
import ScanHistory from './ScanHistory';
import Overview from './components/Overview';
import Settings from './components/Settings';

// LiveScan has been moved to LiveScan.jsx

// ScanHistory has been moved to ScanHistory.jsx

function App() {
  const [currentView, setCurrentView] = useState('live_scan');

  return (
    <div className="bg-surface font-body text-on-surface antialiased min-h-screen">
      <aside className="h-screen w-64 fixed left-0 top-0 bg-emerald-50 dark:bg-emerald-950 border-r border-emerald-100/10 flex flex-col p-4 gap-2 z-50 hidden md:flex">
        <div className="mb-8 px-2 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
            <span className="material-symbols-outlined text-white" style={{fontVariationSettings: "'FILL' 1"}}>eco</span>
          </div>
          <div>
            <div className="text-lg font-black text-emerald-950 dark:text-white font-headline leading-tight">
              <h1 className="text-xl font-bold tracking-tight text-emerald-50 dark:text-emerald-100 mb-1">AgriScan Pro</h1>
            </div>
            <p className="text-[10px] uppercase tracking-widest text-emerald-800/60 font-bold">AgriSight</p>
          </div>
        </div>
        <nav className="flex flex-col gap-1 flex-1">
          <button onClick={() => setCurrentView('overview')} className={`flex items-center gap-3 px-4 py-3 rounded-lg font-manrope text-sm font-medium transition-all ${currentView === 'overview' ? 'bg-emerald-200/50 text-emerald-900' : 'text-emerald-800/70 hover:bg-emerald-100'}`}>
            <span className="material-symbols-outlined" data-icon="dashboard">dashboard</span>
            Overview
          </button>
          <button onClick={() => setCurrentView('live_scan')} className={`flex items-center gap-3 px-4 py-3 rounded-lg font-manrope text-sm font-medium transition-all ${currentView === 'live_scan' ? 'bg-emerald-200/50 text-emerald-900' : 'text-emerald-800/70 hover:bg-emerald-100'}`}>
            <span className="material-symbols-outlined" data-icon="center_focus_strong">center_focus_strong</span>
            Live Scan
          </button>
          <button onClick={() => setCurrentView('history')} className={`flex items-center gap-3 px-4 py-3 rounded-lg font-manrope text-sm font-medium transition-all ${currentView === 'history' ? 'bg-emerald-200/50 text-emerald-900' : 'text-emerald-800/70 hover:bg-emerald-100'}`}>
            <span className="material-symbols-outlined" data-icon="history">history</span>
            Scan History
          </button>
          <button onClick={() => setCurrentView('settings')} className={`flex items-center gap-3 px-4 py-3 rounded-lg font-manrope text-sm font-medium transition-all mt-auto ${currentView === 'settings' ? 'bg-emerald-200/50 text-emerald-900' : 'text-emerald-800/70 hover:bg-emerald-100'}`}>
            <span className="material-symbols-outlined" data-icon="settings">settings</span>
            Settings
          </button>
        </nav>
        <button onClick={() => setCurrentView('live_scan')} className="mt-4 bg-primary text-white py-3 px-4 rounded-lg font-headline font-semibold flex items-center justify-center gap-2 hover:bg-primary-container transition-transform active:scale-95">
          <span className="material-symbols-outlined text-sm" data-icon="add">add</span>
          New Analysis
        </button>
      </aside>

      <main className="md:ml-64 min-h-screen">
        <header className="w-full sticky top-0 z-40 bg-emerald-50/70 backdrop-blur-xl flex justify-between items-center px-6 py-4 max-w-7xl mx-auto">
          <div className="flex flex-col">
            <h1 className="text-2xl font-black text-emerald-900 font-headline tracking-tight">
              {currentView === 'live_scan' ? 'Live Scan' : currentView === 'history' ? 'Scan History' : currentView === 'settings' ? 'Settings' : 'Overview'}
            </h1>
            <p className="text-sm text-on-surface-variant font-medium">
              {currentView === 'live_scan' ? 'Upload a leaf image for real-time AI analysis.' : currentView === 'settings' ? 'Manage your account preferences and integrations.' : 'View your recent AI diagnoses.'}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-emerald-800/60 hover:text-emerald-900 transition-colors">
              <span className="material-symbols-outlined" data-icon="notifications">notifications</span>
            </button>
            <div className="w-10 h-10 rounded-full bg-surface-container-high overflow-hidden border-2 border-primary/10">
              <img alt="User profile" className="w-full h-full object-cover" data-alt="Portrait of a farm manager" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD9cs7qY9T_Vc7Bb7d4DQYDCD223DQx1BZmPnRW7-STbpYoPkDk1Ul5U-uK1ftEVD_n0sU-bpr1QH8EerVQ7jJf9-IbGY6Du8gRVmc3JYnzUdiqDDDzqFnQjHNrkyt71XZdhVVJcSTBL9Tj33H48AuGJAP5ETRpPyT4YPl1BO2DtOqLDAqLRHLzHNx2R4L_YaXifEzzoXG_ALjAheJC522HLKptUC1TbwK4Oofv60Cjybh9790iR74PHdZ8Wl9LoASA7SdOep4j9ViD" />
            </div>
          </div>
        </header>

        {currentView === 'live_scan' ? <LiveScan /> : currentView === 'history' ? <ScanHistory /> : currentView === 'settings' ? <Settings /> : (
          <Overview />
        )}
      </main>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-outline-variant/10 flex justify-around items-center py-3 px-6 z-50">
        <button onClick={() => setCurrentView('overview')} className={`flex flex-col items-center gap-1 ${currentView === 'overview' ? 'text-primary' : 'text-emerald-800/60'}`}>
          <span className="material-symbols-outlined" data-icon="dashboard">dashboard</span>
          <span className="text-[10px] font-bold uppercase">Overview</span>
        </button>
        <button onClick={() => setCurrentView('live_scan')} className={`flex flex-col items-center gap-1 ${currentView === 'live_scan' ? 'text-primary' : 'text-emerald-800/60'}`}>
          <span className="material-symbols-outlined" data-icon="center_focus_strong" style={{fontVariationSettings: currentView === 'live_scan' ? "'FILL' 1" : undefined}}>center_focus_strong</span>
          <span className="text-[10px] font-bold uppercase">Scan</span>
        </button>
        <button onClick={() => setCurrentView('history')} className={`flex flex-col items-center gap-1 ${currentView === 'history' ? 'text-primary' : 'text-emerald-800/60'}`}>
          <span className="material-symbols-outlined" data-icon="history">history</span>
          <span className="text-[10px] font-bold uppercase">History</span>
        </button>
        <button className="flex flex-col items-center gap-1 text-emerald-800/60">
          <span className="material-symbols-outlined" data-icon="settings">settings</span>
          <span className="text-[10px] font-bold uppercase">Settings</span>
        </button>
      </nav>
    </div>
  );
}

export default App;
