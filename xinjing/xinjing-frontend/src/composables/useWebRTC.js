/**
 * useWebRTC — 全局单例，管理与 LiveTalking 数字人的 WebRTC 长连接。
 * 登录后自动连接，路由切换不断开，退出登录时才关闭。
 */
import { reactive } from 'vue'

const state = reactive({
  connected: false,
  connecting: false,
  failed: false,
  sessionId: null,
  remoteStream: null, // MediaStream，包含 video + audio track
})

let _pc = null
let _audioEl = null // MainLayout 注册的持久化 <audio> 元素

// ── 内部工具 ────────────────────────────────────────────
function _resetState() {
  state.connected = false
  state.connecting = false
  state.failed = false
  state.sessionId = null
  state.remoteStream = null
  _pc = null
}

function _attachAudio() {
  if (_audioEl && state.remoteStream) {
    _audioEl.srcObject = state.remoteStream
    _audioEl.play().catch(() => {})
  }
}

// ── 公开接口 ────────────────────────────────────────────
export function useWebRTC() {
  /** MainLayout 在 onMounted 时注册持久 <audio> 元素 */
  function registerAudioElement(el) {
    _audioEl = el
    _attachAudio()
  }

  /** 用户首次交互时调用，解锁浏览器自动播放限制 */
  function unlockAudio() {
    if (_audioEl && _audioEl.paused) {
      _audioEl.play().catch(() => {})
    }
  }

  /** 发起 WebRTC 连接（幂等，已连接时直接返回） */
  async function connect() {
    if (state.connecting || state.connected) return
    state.connecting = true
    state.failed = false

    try {
      const pc = new RTCPeerConnection({ sdpSemantics: 'unified-plan' })
      _pc = pc

      // 用单一 MediaStream 收集所有 track，方便外部直接绑定
      const remoteStream = new MediaStream()
      state.remoteStream = remoteStream

      pc.addEventListener('track', (evt) => {
        const track = evt.track
        remoteStream.addTrack(track)
        if (track.kind === 'audio') _attachAudio()
      })

      pc.addEventListener('connectionstatechange', () => {
        if (['disconnected', 'failed', 'closed'].includes(pc.connectionState)) {
          _resetState()
        }
      })

      pc.addTransceiver('video', { direction: 'recvonly' })
      pc.addTransceiver('audio', { direction: 'recvonly' })

      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      // 等待 ICE 收集完成
      await new Promise((resolve) => {
        if (pc.iceGatheringState === 'complete') { resolve(); return }
        const check = () => {
          if (pc.iceGatheringState === 'complete') {
            pc.removeEventListener('icegatheringstatechange', check)
            resolve()
          }
        }
        pc.addEventListener('icegatheringstatechange', check)
      })

      const localDesc = pc.localDescription
      const res = await fetch('/livetalking/offer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sdp: localDesc.sdp, type: localDesc.type }),
      })
      if (!res.ok) throw new Error('offer rejected')
      const answer = await res.json()
      state.sessionId = answer.sessionid
      await pc.setRemoteDescription(answer)
      state.connected = true
    } catch (e) {
      console.error('数字人连接失败:', e)
      _resetState()
      state.failed = true
    } finally {
      state.connecting = false
    }
  }

  /** 关闭连接（退出登录时调用） */
  function disconnect() {
    if (_pc) { _pc.close() }
    if (_audioEl) { _audioEl.srcObject = null }
    _resetState()
  }

  /** 打断当前语音（用户发新消息时立即调用，清空队列） */
  async function interruptSpeech() {
    if (!state.connected || state.sessionId === null) return
    try {
      await fetch('/livetalking/interrupt_talk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionid: state.sessionId }),
      })
    } catch (e) { /* 忽略 */ }
  }

  /** 让数字人朗读文本（interrupt:true 确保立即抢占，不在旧语音后排队） */
  async function speakReply(text) {
    if (!state.connected || state.sessionId === null) return
    try {
      await fetch('/livetalking/human', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, type: 'echo', interrupt: true, sessionid: state.sessionId }),
      })
    } catch (e) {
      console.warn('数字人发音失败:', e)
    }
  }

  return { state, registerAudioElement, unlockAudio, connect, disconnect, speakReply, interruptSpeech }
}
