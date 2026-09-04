import React, { useState } from 'react';
import { BookOpen, Upload, FileText, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function SourceTopicTab({ onPlanGenerated, setSourceMode }) {
  const [entryMode, setEntryMode] = useState('topic'); // 'topic' or 'document'
  const [topicInput, setTopicInput] = useState("Ohm's Law & Circuit Analysis");
  const [specificFocus, setSpecificFocus] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Hackathon Round 2 Requirements
  const [timeMode, setTimeMode] = useState('20m'); // '5m', '20m', '60m', '7d'
  const [teacherPersona, setTeacherPersona] = useState('dr_sarah'); // 'dr_sarah', 'prof_aryan', 'coach_maya'
  const [selectedLanguage, setSelectedLanguage] = useState('Hinglish'); // 'English', 'Hindi', 'Hinglish'

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleGenerateFromTopic = async () => {
    if (!topicInput.trim()) return;
    setLoading(true);
    setError('');
    try {
      setSourceMode('General knowledge topic mode');
      const res = await axios.post('/api/lessons/plan', {
        topic: topicInput,
        source_mode: 'General knowledge topic mode',
        time_mode: timeMode,
        teacher_persona: teacherPersona,
        language: selectedLanguage
      });
      onPlanGenerated(res.data.session_id, res.data.state);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate lesson plan.');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadAndIndex = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    setUploadProgress('Uploading and parsing document...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (specificFocus.trim()) {
        formData.append('focus_topic', specificFocus.trim());
      }

      setUploadProgress('Extracting & indexing targeted chapter into vector database...');
      const upRes = await axios.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setUploadProgress(`Indexed ${upRes.data.chunk_count} chunks! Creating curriculum plan...`);
      setSourceMode('Document-grounded mode');

      const planTopic = specificFocus.trim() || selectedFile.name;
      const res = await axios.post('/api/lessons/plan', {
        topic: planTopic,
        source_mode: 'Document-grounded mode',
        document_name: selectedFile.name,
        time_mode: timeMode,
        teacher_persona: teacherPersona,
        language: selectedLanguage
      });

      onPlanGenerated(res.data.session_id, res.data.state);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process document and generate plan.');
    } finally {
      setLoading(false);
      setUploadProgress(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center space-x-3 pb-4 border-b border-slate-800">
        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
          <BookOpen className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">Choose Learning Source</h2>
          <p className="text-xs text-slate-400">Teach any conceptual topic or upload course materials for grounded study.</p>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Mode Selector */}
      <div className="grid grid-cols-2 gap-4 bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800">
        <button
          onClick={() => setEntryMode('topic')}
          className={`py-3 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center space-x-2 ${
            entryMode === 'topic'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>Enter Topic Directly</span>
        </button>

        <button
          onClick={() => setEntryMode('document')}
          className={`py-3 px-4 rounded-xl text-sm font-semibold transition flex items-center justify-center space-x-2 ${
            entryMode === 'document'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Upload className="w-4 h-4" />
          <span>Upload Learning Material</span>
        </button>
      </div>

      {/* Content Form */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8">
        {entryMode === 'topic' ? (
          <div className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Educational Topic
              </label>
              <input
                type="text"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                placeholder="e.g. Newton's Three Laws of Motion, Quantum Tunneling, Photosynthesis"
                className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
              />
            </div>

            {/* Adaptive Teaching Configuration */}
            <div className="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-4 sm:p-5 space-y-4">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
                <span>⚙️ Adaptive Teaching Configuration</span>
                <span className="text-[10px] text-indigo-400 font-normal">(Personalized Pedagogy)</span>
              </h4>

              {/* Time Mode (Section 7) */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Available Study Time & Depth:
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { id: '5m', label: '⚡ 5m Blitz', desc: 'Core 2 concepts' },
                    { id: '20m', label: '⏱️ 20m Standard', desc: 'Structured pedagogy' },
                    { id: '60m', label: '🎓 60m Masterclass', desc: 'Deep dive & math' },
                    { id: '7d', label: '📅 7-Day Plan', desc: 'Curriculum roadmap' }
                  ].map(m => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setTimeMode(m.id)}
                      className={`p-2.5 rounded-xl text-left border transition ${
                        timeMode === m.id
                          ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm shadow-indigo-500/20'
                          : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="text-xs font-bold">{m.label}</div>
                      <div className="text-[10px] text-slate-400">{m.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Teacher Persona (Section 18) & Language (Section 8) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Lead AI Teacher Character:
                  </label>
                  <div className="space-y-1.5">
                    {[
                      { id: 'dr_sarah', name: '👩‍🏫 Dr. Sarah', desc: 'Intuitive & Relatable' },
                      { id: 'prof_aryan', name: '👨‍🏫 Prof. Aryan', desc: 'Analytical & Technical' },
                      { id: 'coach_maya', name: '⚡ Coach Maya', desc: 'High-Energy & Exam Prep' }
                    ].map(p => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setTeacherPersona(p.id)}
                        className={`w-full p-2 rounded-xl text-left border text-xs flex items-center justify-between transition ${
                          teacherPersona === p.id
                            ? 'bg-indigo-600/20 border-indigo-500 text-white'
                            : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <span className="font-semibold">{p.name}</span>
                        <span className="text-[10px] text-slate-400">{p.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Teaching Language:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {['English', 'Hindi', 'Hinglish'].map(lang => (
                      <button
                        key={lang}
                        type="button"
                        onClick={() => setSelectedLanguage(lang)}
                        className={`py-2 px-2 rounded-xl text-center border text-xs font-semibold transition ${
                          selectedLanguage === lang
                            ? 'bg-indigo-600/20 border-indigo-500 text-white'
                            : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {lang}
                      </button>
                    ))}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                    💡 Teacher will adapt explanations, real-world examples, and visual analogies to your choices.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={handleGenerateFromTopic}
              disabled={loading || !topicInput.trim()}
              className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition disabled:opacity-50 active:scale-98"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'AI Pedagogical Engine Planning Lesson...' : '🚀 Generate Lesson Plan'}</span>
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* File Dropzone */}
            <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/70 rounded-2xl p-8 text-center transition cursor-pointer bg-slate-800/40 relative">
              <input
                type="file"
                accept=".pdf,.docx,.pptx,.txt,.md"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6" />
              </div>
              <h4 className="text-sm font-semibold text-white">
                {selectedFile ? selectedFile.name : 'Click or Drag & Drop Document Here'}
              </h4>
              <p className="text-xs text-slate-400 mt-1">Supports PDF, DOCX, PPTX, TXT, MD</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Specific Topic / Chapter Focus (Optional)
              </label>
              <input
                type="text"
                value={specificFocus}
                onChange={(e) => setSpecificFocus(e.target.value)}
                placeholder="e.g. Chapter 3: Ohm's Law and Circuit Calculations"
                className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-indigo-500 transition"
              />
            </div>

            {uploadProgress && (
              <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs flex items-center space-x-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span>
                <span>{uploadProgress}</span>
              </div>
            )}

            {/* Adaptive Teaching Configuration for Document */}
            <div className="bg-slate-800/50 border border-slate-700/60 rounded-2xl p-4 sm:p-5 space-y-4">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-2">
                <span>⚙️ Adaptive Teaching Configuration</span>
                <span className="text-[10px] text-indigo-400 font-normal">(Personalized Grounding)</span>
              </h4>

              {/* Time Mode (Section 7) */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Available Study Time & Depth:
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { id: '5m', label: '⚡ 5m Blitz', desc: 'Core 2 concepts' },
                    { id: '20m', label: '⏱️ 20m Standard', desc: 'Structured pedagogy' },
                    { id: '60m', label: '🎓 60m Masterclass', desc: 'Deep dive & math' },
                    { id: '7d', label: '📅 7-Day Plan', desc: 'Curriculum roadmap' }
                  ].map(m => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setTimeMode(m.id)}
                      className={`p-2.5 rounded-xl text-left border transition ${
                        timeMode === m.id
                          ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm shadow-indigo-500/20'
                          : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="text-xs font-bold">{m.label}</div>
                      <div className="text-[10px] text-slate-400">{m.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Teacher Persona & Language */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Lead AI Teacher Character:
                  </label>
                  <div className="space-y-1.5">
                    {[
                      { id: 'dr_sarah', name: '👩‍🏫 Dr. Sarah', desc: 'Intuitive & Relatable' },
                      { id: 'prof_aryan', name: '👨‍🏫 Prof. Aryan', desc: 'Analytical & Technical' },
                      { id: 'coach_maya', name: '⚡ Coach Maya', desc: 'High-Energy & Exam Prep' }
                    ].map(p => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setTeacherPersona(p.id)}
                        className={`w-full p-2 rounded-xl text-left border text-xs flex items-center justify-between transition ${
                          teacherPersona === p.id
                            ? 'bg-indigo-600/20 border-indigo-500 text-white'
                            : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <span className="font-semibold">{p.name}</span>
                        <span className="text-[10px] text-slate-400">{p.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Teaching Language:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {['English', 'Hindi', 'Hinglish'].map(lang => (
                      <button
                        key={lang}
                        type="button"
                        onClick={() => setSelectedLanguage(lang)}
                        className={`py-2 px-2 rounded-xl text-center border text-xs font-semibold transition ${
                          selectedLanguage === lang
                            ? 'bg-indigo-600/20 border-indigo-500 text-white'
                            : 'bg-slate-900/60 border-slate-700/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {lang}
                      </button>
                    ))}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                    💡 Document content will be grounded in vector database and taught in your chosen language.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={handleUploadAndIndex}
              disabled={loading || !selectedFile}
              className="w-full flex items-center justify-center space-x-2 py-3.5 px-6 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/25 transition disabled:opacity-50 active:scale-98"
            >
              <Upload className="w-4 h-4" />
              <span>{loading ? 'Processing & Indexing Document...' : '📥 Process & Index Document'}</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

