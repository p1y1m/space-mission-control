import { Component, ErrorInfo, ReactNode } from 'react'

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  componentDidCatch(error: Error, info: ErrorInfo) { console.error('UI boundary', error, info) }
  render() {
    if (this.state.failed) return <main className="fatal"><div className="brand-mark">AC</div><h1>Telemetry display interrupted</h1><p>The interface encountered an unexpected error. No mission data was changed.</p><button onClick={() => location.reload()}>Restart interface</button></main>
    return this.props.children
  }
}
