import { useState } from 'react'

import { Modal } from './Modal'
import { Spinner } from './Spinner'

interface ConfirmDialogProps {
  title: string
  message: string
  confirmLabel: string
  onConfirm: () => Promise<void>
  onCancel: () => void
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const [working, setWorking] = useState(false)

  const confirm = async () => {
    setWorking(true)
    try {
      await onConfirm()
    } finally {
      setWorking(false)
    }
  }

  return (
    <Modal title={title} onClose={onCancel} width="max-w-md">
      <p className="px-5 py-5 text-sm text-slate-600">{message}</p>
      <footer className="flex justify-end gap-3 border-t border-slate-200 px-5 py-4">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={confirm}
          disabled={working}
          className="inline-flex items-center gap-2 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-60"
        >
          {working && <Spinner />}
          {confirmLabel}
        </button>
      </footer>
    </Modal>
  )
}
