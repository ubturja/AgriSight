import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import { BrowserRouter } from 'react-router-dom' // <-- ADD THIS IMPORT
import './index.css'
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>  {/* <-- WRAP YOUR APP */}
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)