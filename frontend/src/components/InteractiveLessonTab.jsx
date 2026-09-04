import React, { useState, useEffect, useRef } from 'react';
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
  Languages
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
  const [showScript, setShowScript] = useState(false);

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
                        controls
                        autoPlay
                        src={mediaData.audio_url}
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

          {/* Spoken Script & Whiteboard Summary Expander */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden">
            <button
              onClick={() => setShowScript(!showScript)}
              className="w-full flex items-center justify-between p-4 text-left hover:bg-slate-800/40 transition"
            >
              <div className="flex items-center space-x-2 text-sm font-semibold text-white">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span>📄 View Spoken Script & Whiteboard Summary</span>
              </div>
              {showScript ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
            </button>

            {showScript && (
              <div className="p-5 border-t border-slate-800/80 space-y-4 text-xs sm:text-sm text-slate-300 bg-slate-950/40">
                <div>
                  <strong className="text-white block mb-1">Spoken Script ({mediaData?.difficulty || concept.difficulty} level):</strong>
                  <p className="text-slate-300 leading-relaxed bg-slate-900/80 p-4 rounded-xl border border-slate-800">
                    {mediaData?.spoken_script || concept.spoken_script}
                  </p>
                </div>

                {mediaData?.summary_points && mediaData.summary_points.length > 0 && (
                  <div>
                    <strong className="text-white block mb-2">Key Concept Bullet Points:</strong>
                    <ul className="space-y-1.5 list-disc list-inside text-slate-300">
                      {mediaData.summary_points.map((pt, i) => (
                        <li key={i}>{pt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {mediaData?.source_references && mediaData.source_references.length > 0 && (
                  <div className="pt-2 border-t border-slate-800">
                    <strong className="text-slate-400 block mb-1">Grounding Source Passages:</strong>
                    {mediaData.source_references.map((ref, i) => (
                      <p key={i} className="text-xs text-slate-400 italic">• {ref}</p>
                    ))}
                  </div>
                )}
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

