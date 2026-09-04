import React, { useState } from 'react';
import { 
  BarChart3, 
  CheckCircle2, 
  AlertCircle, 
  Award, 
  Calendar, 
  ArrowRight, 
  Sparkles,
  TrendingUp,
  BookOpen
} from 'lucide-react';
import axios from 'axios';
import confetti from 'canvas-confetti';

export default function AssessmentTab({ sessionId, lessonPlan, onRestartLesson }) {
  const [selectedOption, setSelectedOption] = useState("Halved (1/2x)");
  const [submitting, setSubmitting] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [error, setError] = useState('');

  const handleSubmitQuiz = async () => {
    setSubmitting(true);
    setError('');
    try {
      const res = await axios.post(`/api/lessons/${sessionId || 'demo'}/assessment/submit`, {
        selected_option: selectedOption
      });
      setReportData(res.data);
      if (res.data.score_pct >= 75) {
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.6 }
        });
      }
    } catch (err) {
      console.error('Quiz submit error:', err);
      setError('Failed to submit assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  const options = [
    "Doubled (2x)",
    "Halved (1/2x)",
    "Quadrupled (4x)",
    "Unchanged"
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <BarChart3 className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Final Comprehensive Assessment</h2>
          <p className="text-xs text-slate-400">Evaluate holistic mastery, application ability, and generate personalized performance report.</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Quiz Section */}
      {!reportData ? (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-xl">
          <div className="space-y-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Application & Numerical Problem
            </span>
            <h3 className="text-lg sm:text-xl font-bold text-white leading-relaxed">
              If Resistance R is doubled under constant Voltage V, the new Current I will be:
            </h3>
          </div>

          <div className="space-y-3">
            {options.map((opt, i) => (
              <label
                key={i}
                className={`flex items-center space-x-3 p-4 rounded-xl border cursor-pointer transition ${
                  selectedOption === opt
                    ? 'bg-indigo-600/15 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-800/60 border-slate-700/60 text-slate-300 hover:bg-slate-800'
                }`}
              >
                <input
                  type="radio"
                  name="quiz_option"
                  value={opt}
                  checked={selectedOption === opt}
                  onChange={(e) => setSelectedOption(e.target.value)}
                  className="w-4 h-4 text-indigo-600 focus:ring-indigo-500 border-slate-600 bg-slate-700"
                />
                <span className="text-sm font-medium">{opt}</span>
              </label>
            ))}
          </div>

          <button
            onClick={handleSubmitQuiz}
            disabled={submitting}
            className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition disabled:opacity-50 active:scale-98"
          >
            <Award className="w-4 h-4" />
            <span>{submitting ? 'Evaluating Performance...' : 'Submit Final Quiz & Generate Report'}</span>
          </button>
        </div>
      ) : (
        /* Comprehensive Mastery & Performance Report View */
        <div className="space-y-6 animate-fadeIn">
          {/* Radar Metrics Card Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Overall Mastery</span>
              <span className="text-2xl sm:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-emerald-400">
                {Math.round((reportData.metrics?.mastery_score || 0.8) * 100)}%
              </span>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Conceptual Clarity</span>
              <span className="text-2xl sm:text-3xl font-extrabold text-sky-400">
                {Math.round((reportData.metrics?.clarity_score || 0.85) * 100)}%
              </span>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Application Skill</span>
              <span className="text-2xl sm:text-3xl font-extrabold text-violet-400">
                {Math.round((reportData.metrics?.application_score || 0.75) * 100)}%
              </span>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Retention Index</span>
              <span className="text-2xl sm:text-3xl font-extrabold text-teal-400">
                {Math.round((reportData.metrics?.retention_score || 0.90) * 100)}%
              </span>
            </div>
          </div>

          {/* Strengths & Targeted Improvements */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="bg-slate-900/80 border border-emerald-500/20 rounded-2xl p-6 space-y-3">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Demonstrated Strengths</span>
              </div>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                {(reportData.report?.strong_areas || ["Voltage & Current Definitions", "V = I * R Formula Application"]).map((s, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-900/80 border border-amber-500/20 rounded-2xl p-6 space-y-3">
              <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>Targeted Areas for Improvement</span>
              </div>
              <ul className="space-y-2 text-xs sm:text-sm text-slate-300">
                {(reportData.report?.weak_areas && reportData.report.weak_areas.length > 0 
                  ? reportData.report.weak_areas 
                  : ["Edge case boundary conditions", "Complex circuit network reduction"]).map((w, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-amber-400 font-bold">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Action Plan */}
          {reportData.report?.action_plan && reportData.report.action_plan.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-3">
              <div className="flex items-center space-x-2 text-indigo-400 font-bold text-sm">
                <Calendar className="w-4 h-4" />
                <span>Personalized 7-Day Action Plan</span>
              </div>
              <div className="space-y-2">
                {reportData.report.action_plan.map((plan, i) => (
                  <div key={i} className="p-3 bg-slate-800/50 rounded-xl text-xs sm:text-sm text-slate-300 flex items-start space-x-2">
                    <span className="text-indigo-400 font-semibold">{i + 1}.</span>
                    <span>{plan}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Next Topic & Restart */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-slate-900 border border-indigo-500/20 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="text-xs text-slate-400 block mb-1">Recommended Next Topic</span>
              <h4 className="text-base font-bold text-white">
                {reportData.report?.next_topic || "Kirchhoff's Voltage and Current Laws (KVL & KCL)"}
              </h4>
            </div>

            <button
              onClick={onRestartLesson}
              className="flex items-center space-x-2 py-3 px-6 rounded-xl font-semibold text-sm text-white bg-indigo-600 hover:bg-indigo-500 shadow-md transition active:scale-98"
            >
              <span>🚀 Start Next Lesson</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

