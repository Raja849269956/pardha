import React, { useEffect, useRef, useState } from 'react';

function Overlay() {
  const [suggestion, setSuggestion] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const overlayRef = useRef(null);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const resizeStartRef = useRef({ x: 0, y: 0, width: 420, height: 300 });

  useEffect(() => {
    document.body.style.background = 'transparent';

    const saved = localStorage.getItem('latestSuggestion');
    if (saved) {
      setSuggestion(JSON.parse(saved));
    }

    const handleStorage = (e) => {
      if (e.key === 'latestSuggestion' && e.newValue) {
        setSuggestion(JSON.parse(e.newValue));
      }
      if (e.key === 'latestTranscript' && e.newValue) {
        const data = JSON.parse(e.newValue);
        if (data?.is_final) {
          setTranscript(data.text);
        }
      }
    };

    window.addEventListener('storage', handleStorage);
    return () => {
      document.body.style.background = '';
      window.removeEventListener('storage', handleStorage);
    };
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        const dx = e.clientX - dragStartRef.current.x;
        const dy = e.clientY - dragStartRef.current.y;
        dragStartRef.current = { x: e.clientX, y: e.clientY };
        if (window.electronAPI) {
          window.electronAPI.moveOverlay(dx, dy);
        }
      } else if (isResizing) {
        const dx = e.clientX - resizeStartRef.current.x;
        const dy = e.clientY - resizeStartRef.current.y;
        const newWidth = Math.max(280, resizeStartRef.current.width + dx);
        const newHeight = Math.max(180, resizeStartRef.current.height + dy);
        if (window.electronAPI) {
          window.electronAPI.resizeOverlay(newWidth, newHeight);
        }
      }
    };

    const handleMouseUp = () => {
      if (isResizing && overlayRef.current) {
        resizeStartRef.current.width = overlayRef.current.offsetWidth;
        resizeStartRef.current.height = overlayRef.current.offsetHeight;
      }
      setIsDragging(false);
      setIsResizing(false);
    };

    if (isDragging || isResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isResizing]);

  const handleHeaderMouseDown = (e) => {
    setIsDragging(true);
    dragStartRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleResizeMouseDown = (e) => {
    e.stopPropagation();
    setIsResizing(true);
    resizeStartRef.current = {
      x: e.clientX,
      y: e.clientY,
      width: overlayRef.current?.offsetWidth || 420,
      height: overlayRef.current?.offsetHeight || 300,
    };
  };

  return (
    <div className="overlay" ref={overlayRef}>
      <div className="overlay-header" onMouseDown={handleHeaderMouseDown}>
        <span>Interview Copilot</span>
      </div>
      <div className="overlay-content">
        {suggestion && (
          <div className="suggestion-box">
            <div className="suggestion-question">Q: {suggestion.question}</div>
            <div className="suggestion-answer">{suggestion.answer}</div>
          </div>
        )}
        {!suggestion && (
          <div className="overlay-placeholder">
            Listening...
            {transcript && <div className="overlay-transcript">{transcript}</div>}
          </div>
        )}
      </div>
      <div
        className="overlay-resize-handle"
        onMouseDown={handleResizeMouseDown}
      />
    </div>
  );
}

export default Overlay;
