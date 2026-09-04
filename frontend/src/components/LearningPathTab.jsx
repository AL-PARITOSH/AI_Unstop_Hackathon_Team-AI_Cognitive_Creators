import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  ArrowRight, 
  BookOpen, 
  Layers, 
  Award, 
  ChevronRight,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';

export default function LearningPathTab({ onStartLessonWithTopic }) {
  const [broadTopic, setBroadTopic] = useState('Machine Learning from Scratch');
  const [educationLevel, setEducationLevel] = useState('beginner');
  const [language, setLanguage] = useState('Hinglish');
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [savedPaths, setSavedPaths] = useState({});

  useEffect(() => {
    // Fetch saved paths
    axios.get('/api/learning-paths')
      .then(res => setSavedPaths(res.data))
      .catch(err => console.error('Failed to load saved learning paths:', err));
  }, []);

  const handleGeneratePath = async () => {
    if (!broadTopic.trim()) return;
    setLoading(true);
    setError('');

    try {
      const res = await axios.post('/api/learning-paths/generate', {
        topic: broadTopic.trim(),
        education_level: educationLevel,
        language: language
      });
      setLearningPath(res.data);
    } catch (err) {
      console.error('Error generating learning path:', err);
      setError(err.response?.data?.detail || 'Failed to generate structured learning path.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartStage = (stageTitle) => {
    const fullTopic = `${broadTopic}: ${stageTitle}`;
    if (onStartLessonWithTopic) {
      onStartLessonWithTopic(fullTopic);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-11 h-11 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
              <span>Structured Learning Paths</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                Section 15 Architecture
              </span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Transform broad subjects into progressive, unlockable multi-stage curriculum roadmaps.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Generator Form Card */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5 shadow-xl">
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider">
            Broad Domain or Career Subject:
          </label>
          <input
            type="text"
            value={broadTopic}
            onChange={(e) => setBroadTopic(e.target.value)}
            placeholder="e.g. Machine Learning, Full Stack Web Development, Organic Chemistry, System Design"
            className="w-full px-4 py-3.5 rounded-2xl bg-slate-800/80 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition placeholder:text-slate-500"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Target Difficulty Level:</label>
            <div className="grid grid-cols-3 gap-2">
              {['beginner', 'intermediate', 'advanced'].map(lvl => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setEducationLevel(lvl)}
                  className={`py-2 px-3 rounded-xl text-center border text-xs font-semibold capitalize transition ${
                    educationLevel === lvl
                      ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400 hover:text-white'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Curriculum Language:</label>
            <div className="grid grid-cols-3 gap-2">
              {['English', 'Hindi', 'Hinglish'].map(lang => (
                <button
                  key={lang}
                  type="button"
                  onClick={() => setLanguage(lang)}
                  className={`py-2 px-3 rounded-xl text-center border text-xs font-semibold transition ${
                    language === lang
                      ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400 hover:text-white'
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleGeneratePath}
          disabled={loading || !broadTopic.trim()}
          className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-2xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-lg shadow-indigo-600/25 transition disabled:opacity-50 active:scale-98"
        >
          <Sparkles className="w-4 h-4" />
          <span>{loading ? 'Synthesizing Progressive Curriculum Roadmap...' : '🗺️ Generate AI Learning Path'}</span>
        </button>
      </div>

      {/* Generated Roadmap Timeline */}
      {learningPath && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 flex flex-wrap items-center justify-between gap-4">
            <div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                {learningPath.target_audience} Level
              </span>
              <h3 className="text-xl sm:text-2xl font-extrabold text-white mt-2">
                {learningPath.topic} Roadmap
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Complete {learningPath.total_stages} progressive milestones to achieve domain mastery.
              </p>
            </div>

            <div className="flex items-center space-x-6 text-center">
              <div className="bg-slate-800/60 border border-slate-700 px-4 py-2.5 rounded-2xl">
                <div className="text-lg font-bold text-white">{learningPath.total_stages}</div>
                <div className="text-[11px] text-slate-400">Total Stages</div>
              </div>
              <div className="bg-slate-800/60 border border-slate-700 px-4 py-2.5 rounded-2xl">
                <div className="text-lg font-bold text-indigo-400">{learningPath.total_hours} hrs</div>
                <div className="text-[11px] text-slate-400">Est. Time</div>
              </div>
            </div>
          </div>

          {/* Stepper Milestones */}
          <div className="space-y-4">
            {learningPath.stages.map((stage, idx) => (
              <div
                key={idx}
                className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 sm:p-6 transition flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 group"
              >
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 rounded-2xl bg-indigo-600/20 text-indigo-400 font-bold text-sm flex items-center justify-center border border-indigo-500/30 flex-shrink-0 mt-0.5">
                    #{stage.stage_number}
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-base font-bold text-white group-hover:text-indigo-300 transition">
                        {stage.title}
                      </h4>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400 capitalize">
                        {stage.difficulty}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
                      {stage.description}
                    </p>
                    <div className="flex flex-wrap items-center gap-1.5 pt-2">
                      <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold mr-1">Skills:</span>
                      {stage.key_skills.map((skill, si) => (
                        <span key={si} className="px-2 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-[11px] text-slate-300">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 sm:flex-col sm:items-end sm:space-x-0 sm:space-y-2 w-full sm:w-auto justify-between pt-3 sm:pt-0 border-t sm:border-t-0 border-slate-800">
                  <div className="flex items-center space-x-1 text-xs text-slate-400">
                    <Clock className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{stage.estimated_hours}h</span>
                  </div>

                  <button
                    onClick={() => handleStartStage(stage.title)}
                    className="flex items-center space-x-1.5 py-2 px-4 rounded-xl font-semibold text-xs text-white bg-indigo-600 hover:bg-indigo-500 shadow-md shadow-indigo-600/20 transition active:scale-95 whitespace-nowrap"
                  >
                    <span>Start Stage</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Preset Domain Roadmaps */}
      <div className="space-y-4 pt-4">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          🔥 Popular Curriculum Accelerators:
        </h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { title: 'Machine Learning from Scratch', level: 'Beginner to Advanced', stages: '8 Modules' },
            { title: 'Full Stack Modern Web Architecture', level: 'Intermediate', stages: '7 Modules' },
            { title: 'Digital Electronics & VLSI Fundamentals', level: 'College Engineering', stages: '6 Modules' }
          ].map((preset, i) => (
            <button
              key={i}
              onClick={() => {
                setBroadTopic(preset.title);
                handleGeneratePath();
              }}
              className="p-4 rounded-2xl bg-slate-900/60 hover:bg-slate-800/60 border border-slate-800 hover:border-slate-700 text-left transition space-y-1 group"
            >
              <div className="text-xs font-bold text-white group-hover:text-indigo-300 transition">
                {preset.title}
              </div>
              <div className="flex items-center justify-between text-[11px] text-slate-500">
                <span>{preset.level}</span>
                <span className="text-indigo-400 font-semibold">{preset.stages}</span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

