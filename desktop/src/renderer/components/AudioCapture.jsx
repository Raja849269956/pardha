import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getWsUrl, endSession } from '../api';

const SAMPLE_RATE = 16000;
const BUFFER_SIZE = 2048;

function AudioCapture() {
  const location = useLocation();
  const navigate = useNavigate();
  const profile = location.state?.profile;
  const session = location.state?.session;

  const [status, setStatus] = useState('idle');
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');

  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const streamRef = useRef(null);
  const wsRef = useRef(null);
  const audioQueueRef = useRef([]);

  useEffect(() => {
    if (!profile || !session) {
      navigate('/profiles');
      return;
    }
    loadDevices();
    return () => stopCapture();
  }, []);

  const loadDevices = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter((d) => d.kind === 'audioinput');
      setDevices(audioInputs);
      if (audioInputs.length > 0) {
        setSelectedDevice(audioInputs[0].deviceId);
      }
    } catch (err) {
      setError('Could not access microphone: ' + err.message);
    }
  };

  const startCapture = async () => {
    setError('');
    setStatus('connecting');

    try {
      const constraints = {
        audio: {
          deviceId: selectedDevice ? { exact: selectedDevice } : undefined,
          sampleRate: SAMPLE_RATE,
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
        },
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      const audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
      audioContextRef.current = audioContext;
      await audioContext.resume();
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(BUFFER_SIZE, 1, 1);
      processorRef.current = processor;

      const wsUrl = await getWsUrl();
      const ws = new WebSocket(`${wsUrl}/api/v1/audio/${session.id}`);
      wsRef.current = ws;

      ws.onopen = () => {
        const token = localStorage.getItem('token');
        ws.send(JSON.stringify({ type: 'auth', token }));
        while (audioQueueRef.current.length > 0) {
          const chunk = audioQueueRef.current.shift();
          ws.send(chunk);
        }
        setStatus('listening');
        if (window.electronAPI) {
          window.electronAPI.showOverlay();
        }
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'transcript') {
          setTranscript(message.payload.text);
          if (message.payload.is_final) {
            localStorage.setItem('latestTranscript', JSON.stringify(message.payload));
          }
        } else if (message.type === 'suggestion') {
          localStorage.setItem('latestSuggestion', JSON.stringify(message.payload));
        } else if (message.type === 'suggestion_start') {
          localStorage.setItem('latestSuggestion', JSON.stringify({
            question: message.payload.question,
            answer: '',
          }));
        } else if (message.type === 'suggestion_token') {
          const saved = localStorage.getItem('latestSuggestion');
          const current = saved ? JSON.parse(saved) : { question: '', answer: '' };
          current.answer += message.payload.token;
          localStorage.setItem('latestSuggestion', JSON.stringify(current));
        } else if (message.type === 'suggestion_end') {
          localStorage.setItem('latestSuggestion', JSON.stringify(message.payload));
        } else if (message.type === 'error') {
          setError(message.payload.message);
        }
      };

      ws.onerror = () => {
        setError('WebSocket error');
        setStatus('error');
      };

      ws.onclose = () => {
        setStatus('closed');
      };

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcm16[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7fff;
        }
        const buffer = pcm16.buffer;
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(buffer);
        } else {
          audioQueueRef.current.push(buffer);
        }
      };

      source.connect(processor);
      processor.connect(audioContext.destination);
    } catch (err) {
      setError('Failed to start: ' + err.message);
      setStatus('error');
    }
  };

  const stopCapture = async () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (audioContextRef.current) {
      await audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (session) {
      try {
        await endSession(session.id);
      } catch (err) {
        console.error(err);
      }
    }
    if (window.electronAPI) {
      window.electronAPI.closeOverlay();
    }
    setStatus('stopped');
  };

  return (
    <div className="audio-capture">
      <h2>Audio Capture</h2>
      <div className="capture-profile">
        {profile?.name} — {session?.name}
      </div>

      <div className="device-select">
        <label>Audio input (virtual mic):</label>
        <select value={selectedDevice} onChange={(e) => setSelectedDevice(e.target.value)}>
          {devices.map((d) => (
            <option key={d.deviceId} value={d.deviceId}>
              {d.label || d.deviceId}
            </option>
          ))}
        </select>
      </div>

      <div className="status">Status: {status}</div>
      {error && <div className="error">{error}</div>}

      <div className="transcript-preview">
        <strong>Latest transcript:</strong>
        <p>{transcript || '—'}</p>
      </div>

      <div className="capture-actions">
        {status === 'idle' || status === 'error' || status === 'stopped' ? (
          <button onClick={startCapture}>Start Listening</button>
        ) : (
          <button onClick={stopCapture}>Stop & End Session</button>
        )}
        <button onClick={() => { stopCapture(); navigate('/profiles'); }}>Back</button>
      </div>
    </div>
  );
}

export default AudioCapture;
