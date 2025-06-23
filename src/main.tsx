import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'  // TailwindCSS 다시 활성화
// import KidHabitsDashboard from './kid-habits-dashboard'
// import MinimalDashboard from './minimal-dashboard'
import SimpleKidHabitsDashboard from './simple-kid-habits-dashboard'
import ErrorBoundary from './error-boundary'
// import SimpleDashboard from './simple-dashboard'

console.log('🚀 main.tsx is loading...')
console.log('🌍 Environment:', {
  NODE_ENV: import.meta.env.MODE,
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000'
})

const rootElement = document.getElementById('root')
console.log('🎯 Root element found:', !!rootElement)

if (rootElement) {
  console.log('📦 Creating React root and rendering app...')
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ErrorBoundary>
        <SimpleKidHabitsDashboard />
      </ErrorBoundary>
    </React.StrictMode>,
  )
  console.log('✅ React app rendered successfully')
} else {
  console.error('❌ Root element not found!')
}