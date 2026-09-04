import React from 'react';
import { Sparkles, Zap, ArrowRight, BookOpen, Clock, CheckCircle2, Play } from 'lucide-react';

export default function HomeTab({ setActiveTab, onLaunchDemo, recentSession, onResumeSession }) {
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/70 via-slate-900 to-slate-900 border border-indigo-500/20 p-8 shadow-xl">
        <div className="relative z-10 max-w-3xl">
          <span className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Multi-Sensory Video Learning Experience</span>
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Meet Your Personal <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-400">AI Teacher</span>
          </h2>
          <p className="mt-3 text-slate-300 text-sm sm:text-base leading-relaxed">
            Generate personalized, voice-narrated educational lessons with interactive whiteboard visuals 
            and a photorealistic human AI Teacher video avatar. Learn any subject or upload your textbooks, lecture notes, and research slides.
          </p>
        </div>
        <div className="absolute right-6 top-1/2 -translate-y-1/2 hidden lg:block opacity-30 pointer-events-none">
          <span className="text-9xl">👩‍🏫</span>
        </div>
      </div>

      {/* Two Column Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Start Lesson & Demo */}
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-sm hover:border-slate-700 transition">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-4">
              <BookOpen className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Start New Learning Session</h3>
            <p className="text-slate-400 text-xs sm:text-sm mt-1.5 leading-relaxed">
              Enter any academic topic or upload PDF slides, lecture notes, and textbooks for grounded learning.
            </p>
            <button
              onClick={() => setActiveTab('source')}
              className="mt-5 w-full flex items-center justify-center space-x-2 px-5 py-3 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition transform active:scale-98"
            >
              <span>✨ Create New Lesson</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="bg-gradient-to-br from-amber-500/10 via-slate-900 to-slate-900 border border-amber-500/20 rounded-2xl p-6 shadow-sm hover:border-amber-500/40 transition">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-4">
              <Zap className="w-5 h-5" />
            </div>
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">Instant Hackathon Demo</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30">
                1-Click Ready
              </span>
            </div>
            <p className="text-slate-400 text-xs sm:text-sm mt-1.5 leading-relaxed">
              Launch pre-configured Ohm's Law session with circuit diagrams, synchronized voice avatar, and misconception evaluation.
            </p>
            <button
              onClick={onLaunchDemo}
              className="mt-5 w-full flex items-center justify-center space-x-2 px-5 py-3 rounded-xl font-semibold text-sm text-amber-200 bg-amber-600/30 hover:bg-amber-600/40 border border-amber-500/40 transition transform active:scale-98"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              <span>⚡ Launch Ohm's Law Demo Scenario</span>
            </button>
          </div>
        </div>

        {/* Right Column: Recent Sessions & Highlights */}
        <div className="space-y-6">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center space-x-2 text-slate-300 mb-4">
              <Clock className="w-4 h-4 text-indigo-400" />
              <h3 className="text-base font-semibold text-white">Recent Session</h3>
            </div>

            {recentSession ? (
              <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-white text-sm sm:text-base">{recentSession.topic}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">Status: <span className="text-indigo-400 font-mono font-medium">{recentSession.current_state}</span></p>
                  </div>
                  <span className="px-2 py-1 rounded-md text-xs font-medium bg-indigo-500/10 text-indigo-300">
                    Concept #{recentSession.current_concept_index + 1}
                  </span>
                </div>

                <button
                  onClick={onResumeSession}
                  className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold transition"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Resume Last Session</span>
                </button>
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 text-xs sm:text-sm">
                No paused session found. Start a new lesson or try the demo!
              </div>
            )}

            <div className="mt-6 pt-6 border-t border-slate-800/80 space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Features Included</h4>
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Split Video & Whiteboard</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Lip-Synced Motion Avatar</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Multilingual Voice (Edge-TTS)</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Voice Microphone Input</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Adaptive Misconception Fix</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Radar Assessment Reports</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

