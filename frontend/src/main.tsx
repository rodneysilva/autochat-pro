import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { ThemeProvider } from './presentation/providers/ThemeProvider'
import { HttpClientProvider } from './presentation/providers/HttpClientProvider'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
      <ThemeProvider>
        <HttpClientProvider>
          <App />
        </HttpClientProvider>
      </ThemeProvider>
  </StrictMode>,
)
