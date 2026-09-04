import React, { useState } from 'react';
import { ListTree, Play, RefreshCw, ChevronDown, ChevronUp, CheckCircle2, Clock, Sparkles } from 'lucide-react';
import axios from 'axios';

export default function LessonPlanTab({ lessonPlan, onStartLesson, onRegeneratePlan }) {
  const [expandedIndex, setExpandedIndex] = useState(0);
  const [regenerating, setRegenerating] = useState(false);

  if (!lessonPlan || !lessonPlan.concepts || lessonPlan.concepts.length === 0) {
    return (
      <div className="max-w-3xl mx-auto py-12 text-center space-y-4">
        <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto">
          <ListTree className="w-7 h-7" />
        </div>
        <h3 className="text-xl font-bold text-white">No Lesson Plan Available Yet</h3>
        <p className="text-slate-400 text-sm">Please create a lesson plan from the "Source & Topic" tab or launch the Demo scenario.</p>
      </div>
    );
  }

  const toggleExpand = (idx) => {
    setExpandedIndex(expandedIndex === idx ? -1 : idx);
  };

  const handleRegen = async () => {
    setRegenerating(true);
    await onRegeneratePlan();
    setRegenerating(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      {/* Title & Metadata Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
            {lessonPlan.source_mode || 'General knowledge'}
          </span>
          <span className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Estimated Duration: <strong className="text-white">{lessonPlan.total_duration_minutes} mins</strong></span>
          </span>
        </div>

        <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          {lessonPlan.lesson_title}
        </h2>

        {/* Learning Objectives */}
        {lessonPlan.learning_objectives && lessonPlan.learning_objectives.length > 0 && (
          <div className="pt-2">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Learning Objectives</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {lessonPlan.learning_objectives.map((obj, i) => (
                <div key={i} className="flex items-start space-x-2 text-xs text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>{obj}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Concepts Timeline */}
      <div className="space-y-4">
        <h3 className="text-base font-bold text-white flex items-center space-x-2">
          <span>Concepts Breakdown Timeline</span>
          <span className="text-xs text-slate-400">({lessonPlan.concepts.length} modules)</span>
        </h3>

        {lessonPlan.concepts.map((concept, idx) => {
          const isExpanded = expandedIndex === idx;
          return (
            <div
              key={idx}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden transition hover:border-slate-700"
            >
              <button
                onClick={() => toggleExpand(idx)}
                className="w-full flex items-center justify-between p-5 text-left"
              >
                <div className="flex items-center space-x-3">
                  <span className="w-8 h-8 rounded-xl bg-indigo-600/20 text-indigo-400 text-xs font-bold flex items-center justify-center border border-indigo-500/20">
                    #{idx + 1}
                  </span>
                  <div>
                    <h4 className="font-semibold text-white text-sm sm:text-base">{concept.title}</h4>
                    <p className="text-xs text-slate-400 capitalize">Difficulty: {concept.difficulty} • {concept.estimated_minutes || 5} mins</p>
                  </div>
                </div>

                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-slate-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-slate-400" />
                )}
              </button>

              {isExpanded && (
                <div className="px-5 pb-5 pt-2 border-t border-slate-800/60 space-y-4 text-xs sm:text-sm text-slate-300">
                  <div>
                    <strong className="text-indigo-300 block mb-1">Simple Real-World Analogy:</strong>
                    <p className="text-slate-300 bg-slate-800/50 p-3 rounded-xl border border-slate-700/50">{concept.simple_analogy}</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <strong className="text-slate-400 block mb-1">Visual Diagram Type:</strong>
                      <code className="bg-slate-800 px-2 py-1 rounded text-emerald-300 text-xs">
                        {concept.visual?.visual_type || 'diagram'}
                      </code>
                      <p className="text-xs text-slate-400 mt-1">{concept.visual?.title}</p>
                    </div>

                    <div>
                      <strong className="text-slate-400 block mb-1">Checkpoint Question Preview:</strong>
                      <p className="text-xs text-slate-300">{concept.checkpoint_question?.question_text}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-4 pt-2">
        <button
          onClick={onStartLesson}
          className="flex-1 flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-lg shadow-indigo-600/30 transition transform active:scale-98"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>▶️ Start Interactive Lesson</span>
        </button>

        <button
          onClick={handleRegen}
          disabled={regenerating}
          className="flex items-center space-x-2 py-3.5 px-5 rounded-xl font-semibold text-sm text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition active:scale-98"
        >
          <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
          <span>Regenerate Plan</span>
        </button>
      </div>
    </div>
  );
}

