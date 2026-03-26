import { useState, useEffect } from 'react';
import { QRCode } from "react-qr-code";
import { v4 as uuidv4 } from 'uuid';

export default function Settings() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('telegram_user');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loginToken, setLoginToken] = useState('');
  const [authStatus, setAuthStatus] = useState(user ? 'success' : 'pending');

  const [emailReports, setEmailReports] = useState(user?.email_reports || false);
  const [emailAddress, setEmailAddress] = useState(user?.email || '');
  const [smsAlerts, setSmsAlerts] = useState(user?.sms_alerts || false);
  const [weeklySummary, setWeeklySummary] = useState(user?.weekly_summary || false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (user) return;

    const token = uuidv4();
    setLoginToken(token);

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/auth/status?token=${token}`);
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'success' && data.user) {
            clearInterval(interval);
            setAuthStatus('success');
            setUser(data.user);
            localStorage.setItem('telegram_user', JSON.stringify(data.user));
            localStorage.setItem('telegram_chat_id', data.user.chat_id);
            
            setEmailReports(data.user.email_reports || false);
            setEmailAddress(data.user.email || '');
            setSmsAlerts(data.user.sms_alerts || false);
            setWeeklySummary(data.user.weekly_summary || false);
          }
        }
      } catch (err) {
        // error handling omitted for brevity
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [user]);

  const handleLogout = () => {
    localStorage.removeItem('telegram_user');
    localStorage.removeItem('telegram_chat_id');
    setUser(null);
    setAuthStatus('pending');
    setLoginToken('');
  };

  const handleSavePreferences = async () => {
    if (!user) return;
    try {
      const response = await fetch('http://localhost:8000/api/user/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          telegram_chat_id: user.chat_id,
          email: emailAddress,
          email_reports: emailReports,
          sms_alerts: smsAlerts,
          weekly_summary: weeklySummary,
        }),
      });

      if (response.ok) {
        setSaveSuccess(true);
        // update local storage user object with new prefs
        const updatedUser = { ...user, email: emailAddress, email_reports: emailReports, sms_alerts: smsAlerts, weekly_summary: weeklySummary };
        setUser(updatedUser);
        localStorage.setItem('telegram_user', JSON.stringify(updatedUser));
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8 animate-fade-in text-on-surface">
      <div className="mb-6">
        <h2 className="text-3xl font-extrabold text-primary tracking-tight font-headline">Settings</h2>
        <p className="text-on-surface-variant font-body mt-2">Manage your account preferences and integrations.</p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {!user ? (
          <section className="bg-surface-container-lowest rounded-xl p-8 shadow-sm border border-outline-variant/20 flex flex-col items-center justify-center text-center space-y-6">
            <h3 className="text-2xl font-bold font-headline text-primary">Login with Telegram</h3>
            <p className="text-on-surface-variant max-w-sm">
              Scan this QR code with your phone's camera or Telegram app to log in.
            </p>
            {loginToken && (
              <div className="p-4 bg-white rounded-xl shadow-inner">
                <QRCode 
                  value={`https://t.me/AgriSightBot?start=${loginToken}`} 
                  size={200} 
                />
              </div>
            )}
            <p className="text-sm font-semibold animate-pulse text-secondary">Awaiting scan...</p>
          </section>
        ) : (
          <section className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/20">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold font-headline flex items-center gap-2 text-primary">
                <span className="material-symbols-outlined">person</span>
                Profile Information
              </h3>
              <button 
                onClick={handleLogout}
                className="px-4 py-2 bg-error/10 text-error rounded-lg font-semibold hover:bg-error/20 transition-all text-sm shadow-sm"
              >
                Logout
              </button>
            </div>
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 rounded-full bg-surface-container-high overflow-hidden border-4 border-primary/20 flex-shrink-0 flex items-center justify-center text-3xl font-bold text-primary">
                {user.first_name ? user.first_name.charAt(0).toUpperCase() : '?'}
              </div>
              <div>
                <h4 className="text-xl font-bold text-on-surface">{user.first_name}</h4>
                {user.username && <p className="text-sm text-primary font-semibold mt-1">@{user.username}</p>}
                <p className="text-sm text-on-surface-variant mt-1">Chat ID: {user.chat_id}</p>
              </div>
            </div>
          </section>
        )}

        {/* Section 3: Notification Preferences */}
        {user && (
          <section className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/20">
            <h3 className="text-xl font-bold font-headline mb-4 flex items-center gap-2 text-primary">
              <span className="material-symbols-outlined">notifications_active</span>
              Notification Preferences
            </h3>
            <p className="text-sm text-on-surface-variant mb-6">
              Choose what alerts and reports you want to receive.
            </p>
            <div className="space-y-4">
              {/* Toggle 1 */}
              <div className="flex flex-col py-2">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-on-surface">Email Reports</p>
                    <p className="text-xs text-on-surface-variant">Receive daily harvest and scan summaries via email.</p>
                  </div>
                  <button 
                    onClick={() => setEmailReports(!emailReports)}
                    className={`w-11 h-6 rounded-full flex items-center transition-colors px-0.5 ${emailReports ? 'bg-primary' : 'bg-surface-variant'}`}
                  >
                    <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${emailReports ? 'translate-x-5' : 'translate-x-0'}`}></div>
                  </button>
                </div>
                {emailReports && (
                  <div className="mt-3 animate-fade-in">
                    <label htmlFor="emailAddress" className="block text-[11px] font-bold text-on-surface-variant uppercase tracking-wider mb-1">
                      Email Address
                    </label>
                    <input
                      id="emailAddress"
                      type="email"
                      value={emailAddress}
                      onChange={(e) => setEmailAddress(e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant/50 rounded-lg px-4 py-2 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                      placeholder="Enter your email address"
                    />
                  </div>
                )}
              </div>
              
              <hr className="border-outline-variant/20" />

              {/* Toggle 2 */}
              <div className="flex items-center justify-between py-2 opacity-60">
                <div>
                  <p className="font-bold text-on-surface flex items-center gap-2">
                    Severe Disease SMS Alerts
                    <span className="text-[10px] bg-secondary-container text-on-secondary-container px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">Coming Soon</span>
                  </p>
                  <p className="text-xs text-on-surface-variant">Immediate text message when critical conditions are detected.</p>
                </div>
                <button 
                  disabled
                  className={`w-11 h-6 rounded-full flex items-center transition-colors px-0.5 cursor-not-allowed bg-surface-variant`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform duration-300 translate-x-0`}></div>
                </button>
              </div>

              <hr className="border-outline-variant/20" />

              {/* Toggle 3 */}
              <div className="flex items-center justify-between py-2">
                <div>
                  <p className="font-bold text-on-surface">Weekly Summary</p>
                  <p className="text-xs text-on-surface-variant">A comprehensive overview of crop health every Monday.</p>
                </div>
                <button 
                  onClick={() => setWeeklySummary(!weeklySummary)}
                  className={`w-11 h-6 rounded-full flex items-center transition-colors px-0.5 ${weeklySummary ? 'bg-primary' : 'bg-surface-variant'}`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform duration-300 ${weeklySummary ? 'translate-x-5' : 'translate-x-0'}`}></div>
                </button>
              </div>
              
              <div className="pt-4 flex items-center justify-end gap-4">
                {saveSuccess && (
                  <p className="text-sm text-secondary font-medium flex items-center gap-1 animate-fade-in">
                    <span className="material-symbols-outlined text-sm">check_circle</span>
                    Preferences saved!
                  </p>
                )}
                <button
                  onClick={handleSavePreferences}
                  className="px-6 py-2 bg-primary text-on-primary rounded-lg font-semibold hover:bg-primary-container hover:text-on-primary-container transition-all active:scale-95 shadow-sm whitespace-nowrap"
                >
                  Save Preferences
                </button>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}