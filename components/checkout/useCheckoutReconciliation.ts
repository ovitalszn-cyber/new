'use client'

import { useEffect, useState } from 'react'

import { api, ApiError } from '@/lib/api-client'

type Phase = 'reconciling' | 'retrying' | 'delivered' | 'terminal'

export interface CheckoutState {
  phase: Phase
  message: string
  apiKey: string | null
  plan: string | null
}

const INITIAL_STATE: CheckoutState = {
  phase: 'reconciling',
  message: 'Confirming payment and provisioning your account…',
  apiKey: null,
  plan: null,
}

function terminalMessage(status: string) {
  return status === 'expired'
    ? 'This checkout session expired. Return to pricing to start again.'
    : 'This checkout session cannot be reconciled.'
}

export function useCheckoutReconciliation(sessionId: string) {
  const [state, setState] = useState<CheckoutState>(INITIAL_STATE)

  useEffect(() => {
    let active = true
    let timer: ReturnType<typeof setTimeout>
    let failures = 0

    const poll = async () => {
      try {
        const result = await api.getCheckoutSessionStatus(sessionId)
        if (!active) return
        failures = 0
        if (result.api_key) {
          setState({
            phase: 'delivered',
            message: 'Your account and API key are ready.',
            apiKey: result.api_key,
            plan: result.plan,
          })
          return
        }
        if (result.status === 'expired') {
          setState({
            phase: 'terminal',
            message: terminalMessage(result.status),
            apiKey: null,
            plan: result.plan,
          })
          return
        }
        const paid =
          result.payment_status === 'paid' || result.status === 'complete'
        setState({
          phase: 'reconciling',
          message: paid
            ? 'Payment confirmed. Waiting for secure key delivery…'
            : 'Waiting for Stripe to confirm payment…',
          apiKey: null,
          plan: result.plan,
        })
        timer = setTimeout(poll, 2000)
      } catch (cause) {
        if (!active) return
        if (cause instanceof ApiError && [400, 403, 404].includes(cause.status)) {
          setState({
            phase: 'terminal',
            message: cause.message,
            apiKey: null,
            plan: null,
          })
          return
        }
        failures += 1
        setState({
          phase: 'retrying',
          message:
            'Reconciliation is temporarily unavailable. Retrying automatically…',
          apiKey: null,
          plan: null,
        })
        timer = setTimeout(poll, failures > 4 ? 5000 : 2000)
      }
    }

    timer = setTimeout(poll, 0)
    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [sessionId])

  return state
}
