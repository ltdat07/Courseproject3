import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import AccountApp from './AccountApp.tsx'
import './styles/retro.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AccountApp />
  </StrictMode>,
)
