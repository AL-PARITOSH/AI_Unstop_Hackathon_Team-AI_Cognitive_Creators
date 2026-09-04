import React from 'react';
import { 
  Sparkles, 
  Zap, 
  ArrowRight, 
  Video, 
  CheckCircle2, 
  BookOpen, 
  Mic, 
  RefreshCw, 
  BarChart3, 
  ShieldCheck, 
  GraduationCap,
  Play,
  Globe,
  Layers,
  Award
} from 'lucide-react';

export default function LandingPage({ onOpenAuth, onLaunchDemo }) {
  return (
    <div className="space-y-20 animate-fadeIn text-slate-100">
      {/* Hero Section */}
      <section className="relative pt-6 pb-12 overflow-hidden">
        {/* Ambient Gradient Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-600/20 via-violet-600/15 to-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-5xl mx-auto text-center relative z-10 space-y-6">
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 text-xs font-semibold shadow-inner">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <span>Next-Gen Pedagogical AI • Multilingual Video Learning</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
            Learn Anything Faster With Your Personal{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-400">
              Human AI Teacher
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            A photorealistic talking video tutor that explains complex concepts in <strong>Hinglish, Hindi, or English</strong>, 
            draws interactive whiteboard diagrams, listens to your voice, and diagnoses conceptual misconceptions in real time.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onOpenAuth('signup')}
              className="flex items-center space-x-2.5 px-8 py-4 rounded-2xl font-bold text-sm sm:text-base text-white bg-gradient-to-r from-indigo-600 via-indigo-500 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-xl shadow-indigo-600/30 transition transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>🚀 Get Started Free</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onLaunchDemo}
              className="flex items-center space-x-2.5 px-7 py-4 rounded-2xl font-bold text-sm sm:text-base text-amber-200 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 shadow-lg shadow-amber-500/10 transition transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              <span>⚡ Try 1-Click Live Demo</span>
            </button>
          </div>

          <p className="text-xs text-slate-500 pt-2">
            No credit card required • Instant demo available • Supports textbooks & slides
          </p>
        </div>

        {/* Live Classroom Preview Mockup */}
        <div className="mt-12 max-w-5xl mx-auto rounded-3xl p-2 sm:p-3 bg-gradient-to-b from-indigo-500/20 via-slate-800/40 to-slate-900/80 border border-indigo-500/30 shadow-2xl backdrop-blur-sm">
          <div className="bg-slate-950 rounded-2xl overflow-hidden border border-slate-800">
            {/* Window bar */}
            <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
                <span className="text-xs text-slate-400 ml-2 font-mono">ai-teacher.io/classroom/ohms-law</span>
              </div>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                🔴 Live Video Acting Mode
              </span>
            </div>

            {/* Split Classroom Preview */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-4 p-6 bg-slate-950">
              {/* Left 60%: Whiteboard */}
              <div className="md:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-center items-center text-center min-h-[260px]">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-3">
                  <Layers className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white mb-1">Dynamic Whiteboard Circuit Visual</h4>
                <p className="text-xs text-slate-400 max-w-xs mb-3">
                  Generates Kroki diagrams, Math formulas, and Pollinations circuit illustrations synchronized with speech.
                </p>
                <div className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-emerald-400 text-xs">
                  I = V / R &nbsp;&bull;&nbsp; (Current opposes Resistance)
                </div>
              </div>

              {/* Right 40%: AI Video Teacher Avatar */}
              <div className="md:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center text-center">
                <div className="w-24 h-24 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-600/30 mb-3 relative">
                  <span className="text-5xl">👩‍🏫</span>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-emerald-500 border-2 border-slate-900 flex items-center justify-center">
                    <Play className="w-2.5 h-2.5 text-white fill-current ml-0.5" />
                  </div>
                </div>
                <h4 className="text-sm font-bold text-white">AI Video Tutor</h4>
                <p className="text-xs text-slate-400 mt-1">
                  Synced Lip Movements &bull; Natural Head Gestures &bull; Fluent Hinglish / Hindi
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Metrics Counter Bar */}
      <section className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-sky-400">
            10,000+
          </span>
          <span className="block text-xs text-slate-400 mt-1 font-medium">Concepts Taught</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">
            98.4%
          </span>
          <span className="block text-xs text-slate-400 mt-1 font-medium">Concept Retention</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-400">
            3 Modes
          </span>
          <span className="block text-xs text-slate-400 mt-1 font-medium">Hinglish • Hindi • English</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-center">
          <span className="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-pink-400">
            0%
          </span>
          <span className="block text-xs text-slate-400 mt-1 font-medium">Hallucination (RAG Grounded)</span>
        </div>
      </section>

      {/* 4 Pillars Feature Grid */}
      <section className="max-w-6xl mx-auto space-y-12">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            Built Like a Real Classroom, Powered by Advanced AI
          </h2>
          <p className="text-slate-400 text-sm">
            Not just text on a screen. AI Teacher combines visual cognition, synthesized audio, and video acting.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 rounded-2xl p-6 space-y-3 transition">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
              <Video className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-white">Talking Video Avatar</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Synthesizes a human educator video who speaks with accurate lip-sync and natural head nodding gestures.
            </p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 hover:border-emerald-500/40 rounded-2xl p-6 space-y-3 transition">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
              <Mic className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-white">Voice Microphone Input</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Talk directly to your teacher. Integrated with Groq Whisper for instant voice transcription and evaluation.
            </p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 hover:border-amber-500/40 rounded-2xl p-6 space-y-3 transition">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <RefreshCw className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-white">Adaptive Remediation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Detects conceptual misconceptions in student answers and automatically generates intuitive water-pipe analogies.
            </p>
          </div>

          <div className="bg-slate-900/80 border border-slate-800 hover:border-sky-500/40 rounded-2xl p-6 space-y-3 transition">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-base text-white">Radar Mastery Reports</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Post-lesson quiz generates 4-KPI scores (Clarity, Application, Retention, Mastery) and a 7-day action plan.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works (1-2-3-4) */}
      <section className="max-w-5xl mx-auto bg-slate-900/50 border border-slate-800 rounded-3xl p-8 sm:p-12 space-y-10">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Simple Workflow</span>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">How Learning Works</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-2">
            <span className="text-3xl font-black text-indigo-400/40">01</span>
            <h4 className="font-bold text-sm text-white">Choose Subject</h4>
            <p className="text-xs text-slate-400">Type any concept or upload your course PDFs and lecture slides.</p>
          </div>

          <div className="space-y-2">
            <span className="text-3xl font-black text-indigo-400/40">02</span>
            <h4 className="font-bold text-sm text-white">AI Plans Syllabus</h4>
            <p className="text-xs text-slate-400">Curriculum engine designs concepts, real-world analogies, and checkpoints.</p>
          </div>

          <div className="space-y-2">
            <span className="text-3xl font-black text-indigo-400/40">03</span>
            <h4 className="font-bold text-sm text-white">Watch & Learn</h4>
            <p className="text-xs text-slate-400">Split-screen whiteboard and talking video teacher explain each module.</p>
          </div>

          <div className="space-y-2">
            <span className="text-3xl font-black text-indigo-400/40">04</span>
            <h4 className="font-bold text-sm text-white">Verify & Master</h4>
            <p className="text-xs text-slate-400">Answer checkpoints via text or mic, resolve misconceptions, and receive reports.</p>
          </div>
        </div>
      </section>

      {/* Final Call to Action Banner */}
      <section className="max-w-5xl mx-auto rounded-3xl bg-gradient-to-r from-indigo-900/60 via-slate-900 to-slate-900 border border-indigo-500/30 p-8 sm:p-12 text-center space-y-6 shadow-2xl">
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white">
          Ready to experience the future of personalized education?
        </h2>
        <p className="max-w-xl mx-auto text-sm sm:text-base text-slate-300">
          Create your account today or jump into the instant interactive Ohm's Law demo in 1 click.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={() => onOpenAuth('signup')}
            className="flex items-center space-x-2 px-8 py-3.5 rounded-xl font-bold text-sm text-white bg-indigo-600 hover:bg-indigo-500 shadow-lg shadow-indigo-600/30 transition transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <span>Create Free Account</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={() => onOpenAuth('login')}
            className="px-6 py-3.5 rounded-xl font-semibold text-sm text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
          >
            <span>Sign In to Existing Account</span>
          </button>
        </div>
      </section>
    </div>
  );
}

