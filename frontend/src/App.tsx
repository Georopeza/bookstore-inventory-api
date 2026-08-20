import { ToastProvider } from './components/ToastProvider'
import { InventoryDashboard } from './pages/InventoryDashboard'

export default function App() {
  return (
    <ToastProvider>
      <InventoryDashboard />
    </ToastProvider>
  )
}
