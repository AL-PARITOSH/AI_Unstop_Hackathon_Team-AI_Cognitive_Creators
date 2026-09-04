import React, { useState, useEffect } from 'react';
import { TrendingUp, Award, CheckCircle2, Compass, ArrowRight } from 'lucide-react';
import axios from 'axios';

export default function ProgressDashboardTab({ setActiveTab }) {
  const [history, setHistory] = useState({
    total_sessions: 3,
    average_score: '85.0%',
    mastery_rate: '92%',
    mastered_topics: [
      "Ohm's Law & Circuit Analysis",
      "Newton's Laws of Motion"
    ],
    recommended_path: [
      "1. Kirchhoff's Laws (KVL/KCL)",
      "2. Series & Parallel Circuits",
      "3. AC vs DC Power"
    ]
  });

  useEffect(() => {
    axios.get('/api/progress/history')
      .then(res => setHistory(res.data))
      .catch(err => console.error('Failed to fetch history:', err));
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <TrendingUp className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Student Learning Progress & History</h2>
          <p className="text-xs text-slate-400">Track longitudinal retention, concept milestones, and personalized syllabus roadmap.</p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 text-center shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Total Sessions Completed</span>
          <span className="text-3xl sm:text-4xl font-extrabold text-indigo-400">{history.total_sessions}</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 text-center shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Average Quiz Score</span>
          <span className="text-3xl sm:text-4xl font-extrabold text-emerald-400">{history.average_score}</span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 text-center shadow-sm">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Concept Mastery Rate</span>
          <span className="text-3xl sm:text-4xl font-extrabold text-sky-400">{history.mastery_rate}</span>
        </div>
      </div>

      {/* Mastered Topics */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <Award className="w-5 h-5 text-amber-400" />
          <span>🏆 Mastered Concepts & Topics</span>
        </div>

        <div className="space-y-2">
          {history.mastered_topics.map((t, i) => (
            <div key={i} className="p-3.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs sm:text-sm text-emerald-300 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span className="font-semibold">{t}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Learning Path */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <div className="flex items-center space-x-2 text-white font-bold text-base">
          <Compass className="w-5 h-5 text-indigo-400" />
          <span>🎯 Recommended Next Learning Path</span>
        </div>

        <div className="space-y-2.5">
          {history.recommended_path.map((step, i) => (
            <div key={i} className="p-3.5 bg-slate-800/60 border border-slate-700/60 rounded-xl text-xs sm:text-sm text-slate-200 flex items-center justify-between">
              <span>{step}</span>
              <button
                onClick={() => setActiveTab('source')}
                className="text-indigo-400 hover:text-indigo-300 text-xs font-semibold flex items-center space-x-1"
              >
                <span>Teach</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

