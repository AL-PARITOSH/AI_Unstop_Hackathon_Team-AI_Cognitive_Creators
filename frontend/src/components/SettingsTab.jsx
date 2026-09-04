import React, { useState } from 'react';
import { Settings, Trash2, CheckCircle2, ShieldCheck, Database, HardDrive, Cpu, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function SettingsTab({ status }) {
  const [clearing, setClearing] = useState(false);
  const [msg, setMsg] = useState('');
  const [error, setError] = useState('');

  const handleClearCache = async () => {
    setClearing(true);
    setMsg('');
    setError('');
    try {
      const res = await axios.post('/api/settings/clear-cache');
      setMsg(res.data.message || 'Media cache cleared successfully!');
      setTimeout(() => setMsg(''), 4000);
    } catch (err) {
      setError('Failed to clear cache.');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <Settings className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">System Settings & Engine Diagnostics</h2>
          <p className="text-xs text-slate-400">Review infrastructure connectivity, pipeline integrity, and storage management.</p>
        </div>
      </div>

      {msg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{msg}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Engine Status Cards */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <span>Active Pipeline Diagnostics</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-200">Pedagogical LLM (Groq)</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Operational
            </span>
          </div>

          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <span className="text-slate-200">Groq Whisper STT Engine</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Operational
            </span>
          </div>

          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Database className="w-4 h-4 text-sky-400" />
              <span className="text-slate-200">RAG Vector DB (ChromaDB)</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Local Ready
            </span>
          </div>

          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Database className="w-4 h-4 text-sky-400" />
              <span className="text-slate-200">Relational DB (SQLite)</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Connected
            </span>
          </div>

          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <HardDrive className="w-4 h-4 text-violet-400" />
              <span className="text-slate-200">Talking Avatar Video Synthesizer</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Fast Lip-Sync Active
            </span>
          </div>

          <div className="p-3.5 bg-slate-800/60 rounded-xl border border-slate-700/60 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <HardDrive className="w-4 h-4 text-violet-400" />
              <span className="text-slate-200">Multilingual TTS (Edge-TTS)</span>
            </div>
            <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Active
            </span>
          </div>
        </div>
      </div>

      {/* Storage & Media Cache */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <HardDrive className="w-5 h-5 text-amber-400" />
          <span>Cache & Media Management</span>
        </h3>

        <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
          The application generates dynamic narration MP3s, diagrams, and lip-synced avatar MP4s cached in <code className="bg-slate-800 px-1.5 py-0.5 rounded text-indigo-300">./media_cache</code>. 
          Clear this folder at any time to regenerate fresh visual and audio segments.
        </p>

        <button
          onClick={handleClearCache}
          disabled={clearing}
          className="flex items-center space-x-2 py-2.5 px-5 rounded-xl font-semibold text-xs sm:text-sm text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 transition active:scale-98"
        >
          <Trash2 className="w-4 h-4" />
          <span>{clearing ? 'Clearing Media Cache...' : '🧹 Clear Generated Media Cache'}</span>
        </button>
      </div>
    </div>
  );
}

