import React, { useState } from 'react';
import { User, Save, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

export default function ProfileTab({ profile, onUpdateProfile }) {
  const [formData, setFormData] = useState({
    display_name: profile?.display_name || 'Learner',
    education_level: profile?.education_level || 'beginner',
    prior_knowledge: profile?.prior_knowledge || 'basic',
    learning_goal: profile?.learning_goal || 'Understand core principles and pass exam',
    preferred_style: profile?.preferred_style || 'visual-first',
    language: profile?.language || 'Hinglish',
    voice_preference: profile?.voice_preference || 'female',
    duration_minutes: profile?.duration_minutes || 20,
    desired_depth: profile?.desired_depth || 'standard lesson'
  });

  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    try {
      const res = await axios.post('/api/profile', formData);
      if (res.data.status === 'success') {
        onUpdateProfile(res.data.profile);
        setSuccessMsg('Profile preferences saved successfully!');
        setTimeout(() => setSuccessMsg(''), 4000);
      }
    } catch (err) {
      console.error('Failed to save profile:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <User className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Learner Profile & Personalization</h2>
          <p className="text-xs text-slate-400">Customize the AI Teacher's pacing, language, analogies, and voice persona.</p>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Display Name */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Display Name</label>
            <input
              type="text"
              value={formData.display_name}
              onChange={(e) => handleChange('display_name', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
              required
            />
          </div>

          {/* Education Level */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Education Level</label>
            <select
              value={formData.education_level}
              onChange={(e) => handleChange('education_level', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            >
              <option value="beginner">Beginner</option>
              <option value="class_8">Class 8th / Middle School</option>
              <option value="class_10">Class 10th / Secondary</option>
              <option value="class_12">Class 12th / High School</option>
              <option value="college">College / Undergraduate</option>
              <option value="interview_prep">Job Interview Preparation</option>
            </select>
          </div>

          {/* Prior Knowledge */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Prior Knowledge</label>
            <select
              value={formData.prior_knowledge}
              onChange={(e) => handleChange('prior_knowledge', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            >
              <option value="none">No prior background</option>
              <option value="basic">Basic familiarity</option>
              <option value="moderate">Moderate understanding</option>
              <option value="strong">Strong grasp (advanced review)</option>
            </select>
          </div>

          {/* Preferred Style */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Teaching Style</label>
            <select
              value={formData.preferred_style}
              onChange={(e) => handleChange('preferred_style', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            >
              <option value="visual-first">Visual-First (Diagrams & Charts)</option>
              <option value="analogy-first">Analogy-First (Real-World Metaphors)</option>
              <option value="step-by-step">Step-by-Step (Mathematical Derivations)</option>
              <option value="technical-deep">Technical Deep-Dive</option>
            </select>
          </div>

          {/* Language */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Teaching Language</label>
            <select
              value={formData.language}
              onChange={(e) => handleChange('language', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            >
              <option value="Hinglish">Hinglish (Natural conversational Hindi + English)</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="English">English</option>
            </select>
          </div>

          {/* Voice Persona */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Teacher Voice Persona</label>
            <select
              value={formData.voice_preference}
              onChange={(e) => handleChange('voice_preference', e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            >
              <option value="female">Female (Natural Educator Persona)</option>
              <option value="male">Male (Deep Resonant Voice)</option>
            </select>
          </div>
        </div>

        {/* Primary Learning Goal */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Primary Learning Goal</label>
          <input
            type="text"
            value={formData.learning_goal}
            onChange={(e) => handleChange('learning_goal', e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
            placeholder="e.g. Master Ohm's Law and solve numerical problems"
          />
        </div>

        {/* Duration Slider */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Target Lesson Duration</label>
            <span className="text-sm font-bold text-indigo-400">{formData.duration_minutes} minutes</span>
          </div>
          <input
            type="range"
            min="5"
            max="60"
            step="5"
            value={formData.duration_minutes}
            onChange={(e) => handleChange('duration_minutes', parseInt(e.target.value))}
            className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-[11px] text-slate-500 mt-1">
            <span>5 mins (Quick)</span>
            <span>20 mins (Standard)</span>
            <span>60 mins (Deep Dive)</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full flex items-center justify-center space-x-2 py-3 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/20 transition disabled:opacity-50 active:scale-98"
        >
          <Save className="w-4 h-4" />
          <span>{saving ? 'Saving Preferences...' : 'Save Profile Preferences'}</span>
        </button>
      </form>
    </div>
  );
}

