import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Volume2, 
  RotateCcw, 
  Lightbulb, 
  ArrowRight, 
  ChevronLeft, 
  ChevronRight, 
  Sparkles, 
  FileText,
  Video,
  Info,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Send,
  Mic,
  MicOff,
  Layers,
  FileDown,
  Languages,
  Play,
  Pause,
  CheckCircle2,
  BookmarkCheck
} from 'lucide-react';
import axios from 'axios';

export default function InteractiveLessonTab({ 
  sessionId, 
  lessonPlan, 
  conceptIndex, 
  setConceptIndex, 
  onProceedToCheckpoint,
  onOpenFlashcards
}) {
  const [mediaData, setMediaData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAnalogy, setShowAnalogy] = useState(false);
  const [showScript, setShowScript] = useState(true); // Directly visible by default

  // Live Narration Synchronization & Highlighting State
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSentenceIndex, setActiveSentenceIndex] = useState(0);
  const [activePointIndex, setActivePointIndex] = useState(0);

  // In-Lesson Follow-Up Doubt Solver State (Task 2 & Section 11)
  const [showDoubtDrawer, setShowDoubtDrawer] = useState(false);
  const [doubtInput, setDoubtInput] = useState('');
  const [doubtLoading, setDoubtLoading] = useState(false);
  const [doubtAnswer, setDoubtAnswer] = useState(null);
  const [isRecordingDoubt, setIsRecordingDoubt] = useState(false);
  const recognitionRef = useRef(null);

  // In-Lesson Dynamic Multilingual Switcher (Section 8)
  const [currentLang, setCurrentLang] = useState(lessonPlan?.language || 'Hinglish');
  const [switchingLang, setSwitchingLang] = useState(false);
  const [downloadingNotes, setDownloadingNotes] = useState(false);

  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const activeSentenceRef = useRef(null);
  const doubtAudioRef = useRef(null);

  const concept = lessonPlan?.concepts?.[conceptIndex];

  useEffect(() => {
    if (!sessionId || !concept) return;

    let isMounted = true;
    setLoading(true);
    setError('');
    setDoubtAnswer(null);

    axios.get(`/api/lessons/${sessionId}/concept/${conceptIndex}/media`)
      .then(res => {
        if (isMounted) {
          setMediaData(res.data);
          setLoading(false);
        }
      })
      .catch(err => {
        if (isMounted) {
          console.error('Media fetch error:', err);
          setError('Failed to load media assets for this concept.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [sessionId, conceptIndex]);

  // Reset playback and tracking state on concept change
  useEffect(() => {
    setCurrentTime(0);
    setActiveSentenceIndex(0);
    setActivePointIndex(0);
    setIsPlaying(false);
  }, [conceptIndex]);

  // Update total duration whenever mediaData arrives
  useEffect(() => {
    if (mediaData?.audio_duration) {
      setDuration(mediaData.audio_duration);
    }
  }, [mediaData]);

  // Format seconds to mm:ss
  const formatTime = (seconds) => {
    if (isNaN(seconds) || seconds <= 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  // Split spoken script into natural sentences and calculate cumulative duration ratios
  const sentences = useMemo(() => {
    const script = mediaData?.spoken_script || concept?.spoken_script || '';
    if (!script.trim()) return [];
    // Split sentences on full stops, question marks, exclamation marks, devanagari danda, or newlines
    const raw = script.match(/[^.!?।\n]+[.!?।]?/g) || [script];
    const cleanList = raw.map(s => s.trim()).filter(Boolean);
    if (cleanList.length === 0) return [{ index: 0, text: script, startRatio: 0, endRatio: 1 }];

    const totalChars = cleanList.reduce((sum, s) => sum + s.length, 0);
    let cumChars = 0;
    return cleanList.map((text, idx) => {
      const startRatio = cumChars / totalChars;
      cumChars += text.length;
      const endRatio = cumChars / totalChars;
      return {
        index: idx,
        text,
        startRatio,
        endRatio
      };
    });
  }, [mediaData?.spoken_script, concept?.spoken_script]);

  // Extract whiteboard summary points and calculate timing ratios
  const summaryPoints = useMemo(() => {
    const pts = mediaData?.summary_points || concept?.whiteboard_bullet_points || concept?.key_points || [];
    if (!Array.isArray(pts) || pts.length === 0) return [];
    return pts.map((pt, idx) => {
      const startRatio = idx / pts.length;
      const endRatio = (idx + 1) / pts.length;
      return {
        index: idx,
        text: pt,
        startRatio,
        endRatio
      };
    });
  }, [mediaData?.summary_points, concept?.whiteboard_bullet_points, concept?.key_points]);

  // Real-time time update handler on audio or video element
  const handleTimeUpdate = (e) => {
    const media = e.target;
    const cur = media.currentTime || 0;
    const dur = media.duration || duration || mediaData?.audio_duration || 1;
    setCurrentTime(cur);
    if (media.duration && !isNaN(media.duration) && media.duration > 0) {
      setDuration(media.duration);
    }

    const progress = dur > 0 ? Math.min(1, Math.max(0, cur / dur)) : 0;

    // Synchronize active spoken sentence
    if (sentences.length > 0) {
      const sIdx = sentences.findIndex(s => progress >= s.startRatio && progress < s.endRatio);
      setActiveSentenceIndex(sIdx !== -1 ? sIdx : (progress >= 0.95 ? sentences.length - 1 : 0));
    }

    // Synchronize active whiteboard summary bullet point
    if (summaryPoints.length > 0) {
      const pIdx = summaryPoints.findIndex(p => progress >= p.startRatio && progress < p.endRatio);
      setActivePointIndex(pIdx !== -1 ? pIdx : (progress >= 0.95 ? summaryPoints.length - 1 : 0));
    }
  };

  // Seek audio/video to exact sentence start
  const seekToSentence = (sent) => {
    const media = videoRef.current || audioRef.current;
    if (media && duration > 0) {
      const target = sent.startRatio * duration;
      media.currentTime = target;
      media.play().catch(() => {});
      setIsPlaying(true);
      setActiveSentenceIndex(sent.index);
    }
  };

  // Seek audio/video to exact whiteboard bullet point start
  const seekToPoint = (pt) => {
    const media = videoRef.current || audioRef.current;
    if (media && duration > 0) {
      const target = pt.startRatio * duration;
      media.currentTime = target;
      media.play().catch(() => {});
      setIsPlaying(true);
      setActivePointIndex(pt.index);
    }
  };

  // Play / Pause toggle
  const togglePlayPause = () => {
    const media = videoRef.current || audioRef.current;
    if (!media) return;
    if (isPlaying) {
      media.pause();
      setIsPlaying(false);
    } else {
      media.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  // Auto-scroll active sentence into view smoothly
  useEffect(() => {
    if (activeSentenceRef.current && isPlaying) {
      activeSentenceRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [activeSentenceIndex, isPlaying]);

  // Voice speech-to-text recognition for asking doubts
  const toggleDoubtVoice = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please type your question.');
      return;
    }

    if (isRecordingDoubt) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsRecordingDoubt(false);
    } else {
      const recognition = new SpeechRecognition();
      recognition.lang = currentLang === 'Hindi' ? 'hi-IN' : 'en-US';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => setIsRecordingDoubt(true);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setDoubtInput(prev => (prev ? `${prev} ${transcript}` : transcript));
      };
      recognition.onerror = () => setIsRecordingDoubt(false);
      recognition.onend = () => setIsRecordingDoubt(false);

      recognitionRef.current = recognition;
      recognition.start();
    }
  };

  const handleSendDoubt = async (e) => {
    if (e) e.preventDefault();
    if (!doubtInput.trim() || doubtLoading) return;

    setDoubtLoading(true);
    try {
      const formData = new FormData();
      formData.append('text_question', doubtInput.trim());
      formData.append('language', currentLang);

      const res = await axios.post(
        `/api/lessons/${sessionId}/concept/${conceptIndex}/ask_doubt`,
        formData
      );
      setDoubtAnswer(res.data);
      setDoubtInput('');
      setShowDoubtDrawer(true);
    } catch (err) {
      console.error('Error submitting doubt:', err);
    } finally {
      setDoubtLoading(false);
    }
  };

  const handleSwitchLanguage = async (newLang) => {
    if (newLang === currentLang || switchingLang) return;
    setSwitchingLang(true);
    try {
      const res = await axios.post(
        `/api/lessons/${sessionId}/concept/${conceptIndex}/switch_language`,
        { new_language: newLang }
      );
      setMediaData(res.data);
      setCurrentLang(newLang);
    } catch (err) {
      console.error('Error switching language:', err);
    } finally {
      setSwitchingLang(false);
    }
  };

  const handleDownloadNotes = async () => {
    setDownloadingNotes(true);
    try {
      const res = await axios.get(`/api/lessons/${sessionId}/notes`);
      const blob = new Blob([res.data.markdown_notes], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', res.data.download_filename || 'StudyNotes.md');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Error downloading notes:', err);
    } finally {
      setDownloadingNotes(false);
    }
  };

  const handleRepeat = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
    }
  };

  if (!concept) {
    return (
      <div className="text-center py-12 text-slate-400 text-sm">
        No active concept selected. Please check your Lesson Plan.
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Concept Header & Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Concept {conceptIndex + 1} of {lessonPlan.concepts.length}
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 capitalize">
              {concept.difficulty} Level
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
            {concept.title}
          </h2>
        </div>

        {/* Prev / Next concept quick switches */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setConceptIndex(Math.max(0, conceptIndex - 1))}
            disabled={conceptIndex === 0}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 transition"
            title="Previous Concept"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <span className="text-xs text-slate-400 font-mono">
            {conceptIndex + 1} / {lessonPlan.concepts.length}
          </span>
          <button
            onClick={() => setConceptIndex(Math.min(lessonPlan.concepts.length - 1, conceptIndex + 1))}
            disabled={conceptIndex === lessonPlan.concepts.length - 1}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 transition"
            title="Next Concept"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-12 text-center space-y-4">
          <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mx-auto"></div>
          <h3 className="text-base font-semibold text-white">
            🎬 Preparing AI Teacher Narration, Visual Whiteboard & Motion Avatar...
          </h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Generating multilingual speech, educational visual diagram, and synthesizing audio-driven lip-synced teacher avatar video.
          </p>
        </div>
      ) : error ? (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          {error}
        </div>
      ) : (
        <>
          {/* Main 2-Column Classroom Experience */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left 60% (7/12): Whiteboard Visual Representation */}
            <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-lg">
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <span>🎨 Whiteboard Visual Representation</span>
                </h3>
                <span className="text-[11px] text-slate-400">{concept.visual?.visual_type}</span>
              </div>
              <div className="p-4 bg-slate-950/60 flex items-center justify-center min-h-[340px]">
                {mediaData?.visual_url ? (
                  <img
                    src={mediaData.visual_url}
                    alt={concept.visual?.title || 'Visual'}
                    className="max-h-[380px] w-auto max-w-full rounded-xl object-contain shadow-md"
                  />
                ) : (
                  <div className="text-slate-500 text-xs">Visual diagram loading...</div>
                )}
              </div>
              {mediaData?.visual_caption && (
                <div className="p-3 bg-slate-900 border-t border-slate-800/80 text-xs text-slate-400 italic">
                  Caption: {mediaData.visual_caption}
                </div>
              )}
            </div>

            {/* Right 40% (5/12): Dedicated Human Talking & Acting AI Teacher Video Player */}
            <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-lg flex flex-col">
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <span>{mediaData?.teacher_name || '👩‍🏫 AI Teacher'}</span>
                </h3>
                {/* Dynamic In-Lesson Multilingual Switcher (Section 8) */}
                <div className="flex items-center space-x-1">
                  <Languages className="w-3.5 h-3.5 text-indigo-400 mr-0.5" />
                  {['English', 'Hindi', 'Hinglish'].map(lang => (
                    <button
                      key={lang}
                      type="button"
                      onClick={() => handleSwitchLanguage(lang)}
                      disabled={switchingLang}
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold transition ${
                        currentLang === lang
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      {lang}
                    </button>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-slate-950/60 flex-1 flex flex-col justify-center">
                {mediaData?.avatar_video_url ? (
                  <video
                    ref={videoRef}
                    key={mediaData.avatar_video_url}
                    src={mediaData.avatar_video_url}
                    controls
                    autoPlay
                    playsInline
                    onTimeUpdate={handleTimeUpdate}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onEnded={() => setIsPlaying(false)}
                    onLoadedMetadata={(e) => {
                      if (e.target.duration) setDuration(e.target.duration);
                    }}
                    className="w-full rounded-xl shadow-2xl border border-indigo-500/20 bg-slate-900 aspect-square object-cover"
                  />
                ) : (
                  <div className="space-y-3">
                    <img
                      src={mediaData?.default_avatar_url || '/media_cache/default_teacher_avatar.png'}
                      alt="AI Teacher"
                      className="w-full rounded-xl aspect-square object-cover shadow-lg border border-slate-800"
                    />
                    {mediaData?.audio_url && (
                      <audio
                        ref={audioRef}
                        key={mediaData.audio_url}
                        controls
                        autoPlay
                        src={mediaData.audio_url}
                        onTimeUpdate={handleTimeUpdate}
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                        onEnded={() => setIsPlaying(false)}
                        onLoadedMetadata={(e) => {
                          if (e.target.duration) setDuration(e.target.duration);
                        }}
                        className="w-full"
                      />
                    )}
                  </div>
                )}
              </div>

              <div className="px-4 py-2.5 bg-slate-900 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>Lip-synced & facial motion synced</span>
                </span>
                <span className="text-[11px] text-slate-500">Multilingual audio</span>
              </div>
            </div>
          </div>

          {/* Simplified Analogy Alert Banner */}
          {showAnalogy && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/15 via-slate-900 to-slate-900 border border-amber-500/30 text-amber-200 text-sm space-y-1 animate-fadeIn">
              <div className="flex items-center space-x-2 font-bold text-amber-400">
                <Lightbulb className="w-4 h-4" />
                <span>Simplified Real-World Analogy</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {mediaData?.simple_analogy || concept.simple_analogy}
              </p>
            </div>
          )}

          {/* Direct Synchronized Live Explanation Studio & Whiteboard Highlighting */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl space-y-0 animate-fadeIn">
            {/* Header with Live Sync Controls */}
            <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${isPlaying ? 'bg-amber-500/20 text-amber-400 ring-2 ring-amber-500/40 animate-pulse' : 'bg-indigo-500/20 text-indigo-400'}`}>
                  {isPlaying ? <Volume2 className="w-5 h-5 animate-bounce" /> : <FileText className="w-5 h-5" />}
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-white">Live Explanation & Whiteboard Synchronizer</h3>
                    {isPlaying ? (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping"></span>
                        <span>EXPLAINING NOW</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                        <span>Click audio to track</span>
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-slate-400">Highlights the active spoken sentence & whiteboard concept in real time as the teacher explains.</p>
                </div>
              </div>

              {/* Playback time, quick controls & toggle */}
              <div className="flex items-center space-x-2.5">
                <div className="flex items-center space-x-2 bg-slate-900/90 px-3 py-1.5 rounded-xl border border-slate-800 text-xs text-slate-300 shadow-inner">
                  <button
                    type="button"
                    onClick={togglePlayPause}
                    className="text-indigo-400 hover:text-white transition p-0.5 flex items-center justify-center"
                    title={isPlaying ? "Pause Narration" : "Play Narration"}
                  >
                    {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
                  </button>
                  <span className="font-mono text-[11px] text-amber-300 font-semibold">{formatTime(currentTime)}</span>
                  <span className="text-slate-600 font-mono">/</span>
                  <span className="font-mono text-[11px] text-slate-400">{formatTime(duration)}</span>
                </div>

                <button
                  type="button"
                  onClick={() => setShowScript(!showScript)}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition flex items-center space-x-1.5 border border-slate-700"
                >
                  {showScript ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  <span>{showScript ? 'Hide View' : 'Direct View'}</span>
                </button>
              </div>
            </div>

            {/* Audio/Video Progress bar indicator */}
            <div className="w-full bg-slate-950 h-1.5 relative overflow-hidden">
              <div 
                className="bg-gradient-to-r from-indigo-500 via-purple-500 to-amber-400 h-full transition-all duration-150"
                style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>

            {showScript && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 divide-y lg:divide-y-0 lg:divide-x divide-slate-800/80 bg-slate-950/40">
                {/* Left 5 Cols: Whiteboard Summary (Live Topic Tracking) */}
                <div className="lg:col-span-5 p-4 sm:p-5 space-y-3.5">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
                    <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-indigo-400">
                      <span>🎨 Whiteboard Summary</span>
                    </div>
                    <span className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">
                      {summaryPoints.length} Key Takeaway{summaryPoints.length !== 1 ? 's' : ''}
                    </span>
                  </div>

                  {summaryPoints.length > 0 ? (
                    <div className="space-y-2.5">
                      {summaryPoints.map((pt, idx) => {
                        const isActive = idx === activePointIndex && (isPlaying || currentTime > 0);
                        const isCovered = idx < activePointIndex;
                        return (
                          <div
                            key={idx}
                            onClick={() => seekToPoint(pt)}
                            className={`p-3 rounded-xl border transition-all duration-300 cursor-pointer select-none text-xs sm:text-sm ${
                              isActive
                                ? 'bg-gradient-to-r from-indigo-500/25 via-indigo-500/10 to-transparent border-l-4 border-indigo-400 text-white font-semibold shadow-lg shadow-indigo-500/15 ring-1 ring-indigo-400/40 translate-x-1'
                                : isCovered
                                ? 'bg-slate-900/60 border-emerald-500/30 text-slate-300 hover:bg-slate-800/60'
                                : 'bg-slate-900/30 border-slate-800/60 text-slate-500 hover:bg-slate-800/40 hover:text-slate-400'
                            }`}
                          >
                            <div className="flex items-start space-x-2.5">
                              <span className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold mt-0.5 ${
                                isActive
                                  ? 'bg-indigo-500 text-white shadow-md shadow-indigo-500/50 animate-pulse ring-2 ring-indigo-300'
                                  : isCovered
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                                  : 'bg-slate-800 text-slate-500 border border-slate-700'
                              }`}>
                                {isCovered ? '✓' : idx + 1}
                              </span>

                              <div className="flex-1 space-y-1">
                                <p className="leading-snug">{pt.text}</p>
                                {isActive && (
                                  <div className="inline-flex items-center space-x-1 text-[10px] text-indigo-300 font-bold bg-indigo-500/20 px-2 py-0.5 rounded border border-indigo-400/30 animate-fadeIn">
                                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping"></span>
                                    <span>⚡ Now Explaining</span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500 italic">No summary points generated for this concept.</p>
                  )}

                  {mediaData?.source_references && mediaData.source_references.length > 0 && (
                    <div className="pt-3 border-t border-slate-800/60 space-y-1">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">Grounding Passages:</span>
                      {mediaData.source_references.map((ref, i) => (
                        <p key={i} className="text-[11px] text-slate-400 italic bg-slate-900/40 p-2 rounded-lg border border-slate-800/50">
                          📌 {ref}
                        </p>
                      ))}
                    </div>
                  )}
                </div>

                {/* Right 7 Cols: Live Spoken Script (Sentence Karaoke Highlighting) */}
                <div className="lg:col-span-7 p-4 sm:p-5 space-y-3.5">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/60">
                    <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-amber-400">
                      <Volume2 className="w-3.5 h-3.5" />
                      <span>Spoken Script ({mediaData?.difficulty || concept.difficulty} Level)</span>
                    </div>
                    <span className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded-md border border-slate-800">
                      Click any sentence to jump audio ⏭
                    </span>
                  </div>

                  <div className="max-h-[340px] overflow-y-auto pr-1 space-y-2.5 custom-scrollbar">
                    {sentences.map((sent, idx) => {
                      const isActive = idx === activeSentenceIndex && (isPlaying || currentTime > 0);
                      const isCovered = idx < activeSentenceIndex;
                      return (
                        <div
                          key={idx}
                          ref={isActive ? activeSentenceRef : null}
                          onClick={() => seekToSentence(sent)}
                          className={`p-3.5 rounded-xl border transition-all duration-300 cursor-pointer select-none text-xs sm:text-sm leading-relaxed ${
                            isActive
                              ? 'bg-gradient-to-r from-amber-500/25 via-amber-500/10 to-transparent border-l-4 border-amber-400 text-amber-100 font-semibold shadow-xl shadow-amber-500/10 ring-1 ring-amber-400/40 scale-[1.01]'
                              : isCovered
                              ? 'bg-slate-900/40 border-slate-800/80 text-slate-300 hover:bg-slate-800/50 hover:text-white'
                              : 'bg-slate-900/20 border-slate-800/40 text-slate-500 hover:bg-slate-800/30 hover:text-slate-400'
                          }`}
                        >
                          <div className="flex items-start space-x-2">
                            {isActive ? (
                              <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-400/20 text-amber-300 border border-amber-400/40 flex-shrink-0 mt-0.5 animate-pulse">
                                <Volume2 className="w-3 h-3 animate-bounce" />
                                <span>Speaking</span>
                              </span>
                            ) : (
                              <span className="text-[10px] text-slate-600 font-mono mt-0.5 flex-shrink-0">
                                {idx + 1}.
                              </span>
                            )}
                            <span className={isActive ? 'font-medium text-amber-100' : ''}>
                              {sent.text}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* In-Lesson Interactive Doubt Solver Drawer (Task 2 & Section 11) */}
          <div className="bg-slate-900/90 border border-indigo-500/30 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-4 bg-indigo-950/30 border-b border-indigo-500/20 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white flex items-center space-x-1.5">
                    <span>Ask AI Teacher a Follow-Up Doubt</span>
                    <span className="text-[10px] text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">Task 2 Interactive</span>
                  </h4>
                  <p className="text-[11px] text-slate-400">Ask any question or confusion regarding this concept via text or microphone.</p>
                </div>
              </div>
            </div>

            <div className="p-4 sm:p-5 space-y-4">
              {/* Question Input form with voice button */}
              <form onSubmit={handleSendDoubt} className="flex items-center space-x-2">
                <input
                  type="text"
                  value={doubtInput}
                  onChange={(e) => setDoubtInput(e.target.value)}
                  placeholder={`Ask ${mediaData?.teacher_name || 'Teacher'} a doubt about "${concept.title}"...`}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-xs sm:text-sm focus:outline-none focus:border-indigo-500 transition placeholder:text-slate-500"
                />

                <button
                  type="button"
                  onClick={toggleDoubtVoice}
                  className={`p-2.5 rounded-xl border transition ${
                    isRecordingDoubt
                      ? 'bg-rose-600 border-rose-500 text-white animate-pulse'
                      : 'bg-slate-800 border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700'
                  }`}
                  title={isRecordingDoubt ? 'Stop Voice Recording' : 'Ask using Microphone Voice'}
                >
                  {isRecordingDoubt ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>

                <button
                  type="submit"
                  disabled={doubtLoading || !doubtInput.trim()}
                  className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center space-x-1.5 transition disabled:opacity-40"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{doubtLoading ? 'Thinking...' : 'Ask'}</span>
                </button>
              </form>

              {/* Teacher's In-Character Response Card */}
              {doubtAnswer && (
                <div className="p-4 rounded-xl bg-slate-950/80 border border-indigo-500/30 space-y-3 animate-fadeIn">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                    <span className="text-xs font-bold text-indigo-300 flex items-center space-x-1.5">
                      <span>👩‍🏫 {doubtAnswer.teacher_name || 'AI Teacher'}'s Direct Answer:</span>
                    </span>
                    {doubtAnswer.audio_url && (
                      <audio
                        ref={doubtAudioRef}
                        src={doubtAnswer.audio_url}
                        controls
                        autoPlay
                        className="h-7 w-48 sm:w-60"
                      />
                    )}
                  </div>

                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                    {doubtAnswer.answer_text}
                  </p>

                  <div className="p-2.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300">
                    <strong>🔑 Key Takeaway:</strong> {doubtAnswer.key_takeaway}
                  </div>

                  {doubtAnswer.follow_up_prompt && (
                    <div className="text-[11px] text-slate-400 italic">
                      💬 Teacher Follow-up: "{doubtAnswer.follow_up_prompt}"
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Bottom Action Buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2">
            <button
              onClick={handleRepeat}
              className="flex items-center justify-center space-x-1.5 py-2.5 px-3 rounded-xl font-semibold text-xs text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition active:scale-98"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>🔁 Repeat</span>
            </button>

            <button
              onClick={() => setShowAnalogy(!showAnalogy)}
              className="flex items-center justify-center space-x-1.5 py-2.5 px-3 rounded-xl font-semibold text-xs text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition active:scale-98"
            >
              <Lightbulb className="w-3.5 h-3.5" />
              <span>💡 {showAnalogy ? 'Hide Analogy' : 'Analogy'}</span>
            </button>

            {/* Active Recall Flashcards Button (Section 18) */}
            <button
              onClick={() => onOpenFlashcards && onOpenFlashcards(sessionId)}
              className="flex items-center justify-center space-x-1.5 py-2.5 px-3 rounded-xl font-semibold text-xs text-sky-300 bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 transition active:scale-98"
              title="Open Interactive Active Recall Flashcards"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>🗂️ Flashcards</span>
            </button>

            {/* Download Study Notes Button (Section 18) */}
            <button
              onClick={handleDownloadNotes}
              disabled={downloadingNotes}
              className="flex items-center justify-center space-x-1.5 py-2.5 px-3 rounded-xl font-semibold text-xs text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 transition active:scale-98"
              title="Download Markdown Study Notes for Revision"
            >
              <FileDown className="w-3.5 h-3.5" />
              <span>{downloadingNotes ? 'Exporting...' : '📝 Notes'}</span>
            </button>

            <button
              onClick={onProceedToCheckpoint}
              className="col-span-2 sm:col-span-1 flex items-center justify-center space-x-1.5 py-2.5 px-4 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition active:scale-98"
            >
              <span>✍️ Checkpoint</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </>
      )}
    </div>
  );
}

