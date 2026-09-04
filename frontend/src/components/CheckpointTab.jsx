import React, { useState, useRef } from 'react';
import { 
  HelpCircle, 
  Mic, 
  Square, 
  MessageSquare, 
  Send, 
  Zap, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  RefreshCw,
  Sparkles
} from 'lucide-react';
import axios from 'axios';
import confetti from 'canvas-confetti';

export default function CheckpointTab({ 
  sessionId, 
  lessonPlan, 
  conceptIndex, 
  onAdvanceConcept, 
  onGoToAssessment 
}) {
  const [inputMode, setInputMode] = useState('typed'); // 'typed' or 'voice'
  const [typedAnswer, setTypedAnswer] = useState('');
  
  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const [submitting, setSubmitting] = useState(false);
  const [evalResult, setEvalResult] = useState(null);
  const [error, setError] = useState('');

  const concept = lessonPlan?.concepts?.[conceptIndex];
  const questionInfo = concept?.checkpoint_question;

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setRecordedAudioBlob(audioBlob);
        setRecordedAudioUrl(URL.createObjectURL(audioBlob));
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setError('');
    } catch (err) {
      console.error('Microphone access error:', err);
      setError('Could not access microphone. Please ensure microphone permissions are granted.');
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleDemoMisconception = () => {
    setInputMode('typed');
    setTypedAnswer('Current increases.');
  };

  const handleSubmit = async () => {
    if (!typedAnswer.trim() && !recordedAudioBlob) return;
    setSubmitting(true);
    setError('');

    try {
      const formData = new FormData();
      if (inputMode === 'typed' || !recordedAudioBlob) {
        formData.append('text_answer', typedAnswer);
      } else {
        formData.append('audio_file', recordedAudioBlob, 'voice_answer.wav');
        if (typedAnswer) formData.append('text_answer', typedAnswer);
      }

      const res = await axios.post(`/api/lessons/${sessionId}/checkpoint/evaluate`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setEvalResult(res.data);

      if (res.data.correctness_score >= 0.70) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Evaluation failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAdvance = async () => {
    try {
      const res = await axios.post(`/api/lessons/${sessionId}/checkpoint/advance`);
      setEvalResult(null);
      setTypedAnswer('');
      setRecordedAudioBlob(null);
      setRecordedAudioUrl(null);

      if (res.data.is_final_assessment) {
        onGoToAssessment();
      } else {
        onAdvanceConcept(res.data.current_concept_index);
      }
    } catch (err) {
      console.error('Advance error:', err);
    }
  };

  if (!concept) {
    return (
      <div className="text-center py-12 text-slate-400 text-sm">
        No active concept available for checkpoint.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <HelpCircle className="w-5 h-5" />
        </div>
        <div>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            Concept {conceptIndex + 1} Checkpoint
          </span>
          <h2 className="text-xl font-bold text-white mt-1">Understanding Verification</h2>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Question Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-3 shadow-lg">
        <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Diagnostic Question</h3>
        <p className="text-lg sm:text-xl font-semibold text-white leading-relaxed">
          {questionInfo?.question_text || 'Explain the core relationship learned in this concept.'}
        </p>
      </div>

      {/* Input Mode Selector */}
      <div className="grid grid-cols-2 gap-3 bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800">
        <button
          onClick={() => setInputMode('typed')}
          className={`py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center justify-center space-x-2 ${
            inputMode === 'typed'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>💬 Typed Answer</span>
        </button>

        <button
          onClick={() => setInputMode('voice')}
          className={`py-2.5 px-4 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center justify-center space-x-2 ${
            inputMode === 'voice'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Mic className="w-4 h-4" />
          <span>🎙️ Spoken Voice Answer</span>
        </button>
      </div>

      {/* Answer Inputs */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        {inputMode === 'typed' ? (
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Your Conceptual Explanation
            </label>
            <textarea
              rows={4}
              value={typedAnswer}
              onChange={(e) => setTypedAnswer(e.target.value)}
              placeholder="Type your explanation here. The AI teacher evaluates conceptual understanding, not just rote keywords."
              className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition resize-none"
            />
          </div>
        ) : (
          <div className="text-center py-6 space-y-4">
            <p className="text-xs text-slate-400">
              Click the microphone button to record your voice answer. Groq Whisper will transcribe it automatically.
            </p>

            <div className="flex items-center justify-center space-x-4">
              {!isRecording ? (
                <button
                  type="button"
                  onClick={startVoiceRecording}
                  className="w-16 h-16 rounded-full bg-rose-600 hover:bg-rose-500 text-white flex items-center justify-center shadow-lg shadow-rose-600/30 transition transform active:scale-95"
                >
                  <Mic className="w-7 h-7" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={stopVoiceRecording}
                  className="w-16 h-16 rounded-full bg-slate-800 border-2 border-rose-500 text-rose-400 flex items-center justify-center animate-pulse transition transform active:scale-95"
                >
                  <Square className="w-6 h-6 fill-current" />
                </button>
              )}
            </div>

            <p className="text-xs font-semibold text-slate-300">
              {isRecording ? '🔴 Recording voice... Click square to stop.' : recordedAudioBlob ? '✅ Voice recorded! Ready to submit.' : 'Click to start recording'}
            </p>

            {recordedAudioUrl && (
              <div className="max-w-xs mx-auto pt-2">
                <audio controls src={recordedAudioUrl} className="w-full" />
              </div>
            )}
          </div>
        )}

        {/* Demo Misconception Test Helper */}
        <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={handleDemoMisconception}
            className="flex items-center space-x-1.5 text-xs text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 px-3 py-1.5 rounded-lg border border-amber-500/30 transition"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>⚡ Test Incorrect Answer Misconception Scenario</span>
          </button>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting || (!typedAnswer.trim() && !recordedAudioBlob)}
            className="flex items-center space-x-2 py-2.5 px-6 rounded-xl font-semibold text-xs sm:text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition disabled:opacity-50 active:scale-98"
          >
            <Send className="w-4 h-4" />
            <span>{submitting ? 'Analyzing Response...' : 'Submit Checkpoint Answer'}</span>
          </button>
        </div>
      </div>

      {/* Real-time AI Diagnostic Result Card */}
      {evalResult && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xl animate-fadeIn">
          {evalResult.correctness_score >= 0.70 ? (
            /* Pass state */
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-bold text-base">🎉 Excellent Understanding!</span>
                </div>
                <span className="font-mono font-bold text-lg">{Math.round(evalResult.correctness_score * 100)}%</span>
              </div>

              <p className="text-slate-300 text-sm leading-relaxed bg-slate-800/40 p-4 rounded-xl border border-slate-800">
                {evalResult.feedback_to_student}
              </p>

              <button
                onClick={handleAdvance}
                className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-lg shadow-emerald-600/30 transition transform active:scale-98"
              >
                <span>➡️ Advance to Next Concept</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : evalResult.correctness_score >= 0.40 ? (
            /* Partial progress */
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5" />
                  <span className="font-bold text-base">👍 Good Progress!</span>
                </div>
                <span className="font-mono font-bold text-lg">{Math.round(evalResult.correctness_score * 100)}%</span>
              </div>

              <p className="text-slate-300 text-sm leading-relaxed bg-slate-800/40 p-4 rounded-xl border border-slate-800">
                {evalResult.feedback_to_student}
              </p>

              <button
                onClick={handleAdvance}
                className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition transform active:scale-98"
              >
                <span>➡️ Continue</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            /* Misconception Detected & Adaptive Remediation */
            <div className="space-y-5">
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-bold text-base">⚠️ Diagnostic Gap Detected</span>
                </div>
                <span className="font-mono font-bold text-lg">{Math.round(evalResult.correctness_score * 100)}%</span>
              </div>

              {evalResult.identified_misconception && (
                <div className="p-3 bg-slate-800/70 rounded-xl border border-slate-700 text-xs sm:text-sm text-slate-300">
                  <strong className="text-rose-400 block mb-1">Identified Misconception:</strong>
                  <span>{evalResult.identified_misconception}</span>
                </div>
              )}

              <p className="text-slate-300 text-sm leading-relaxed">
                {evalResult.feedback_to_student}
              </p>

              {/* Adaptive Remediation Section */}
              <div className="pt-4 border-t border-slate-800 space-y-4">
                <div className="flex items-center space-x-2 text-indigo-400">
                  <RefreshCw className="w-4 h-4" />
                  <h4 className="font-bold text-sm sm:text-base text-white">🔄 Adaptive Remediation Explanation</h4>
                </div>

                <p className="text-slate-300 text-sm leading-relaxed bg-indigo-950/30 p-4 rounded-xl border border-indigo-500/20">
                  {evalResult.remediation_script}
                </p>

                {evalResult.remediation_visual_url && (
                  <div className="flex justify-center bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                    <img
                      src={evalResult.remediation_visual_url}
                      alt="Remediation Diagram"
                      className="max-h-64 w-auto rounded-lg object-contain shadow-md"
                    />
                  </div>
                )}

                {evalResult.re_check_question && (
                  <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700 space-y-2">
                    <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">🎯 Targeted Re-Check Question:</h5>
                    <p className="text-sm font-medium text-white">{evalResult.re_check_question.question_text}</p>
                  </div>
                )}
              </div>

              <button
                onClick={handleAdvance}
                className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
              >
                <span>➡️ Continue to Next Concept</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

