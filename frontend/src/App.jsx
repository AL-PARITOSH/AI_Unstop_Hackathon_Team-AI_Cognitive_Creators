import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import AuthModal from './components/AuthModal';
import HomeTab from './components/HomeTab';
import ProfileTab from './components/ProfileTab';
import SourceTopicTab from './components/SourceTopicTab';
import LessonPlanTab from './components/LessonPlanTab';
import InteractiveLessonTab from './components/InteractiveLessonTab';
import CheckpointTab from './components/CheckpointTab';
import AssessmentTab from './components/AssessmentTab';
import ProgressDashboardTab from './components/ProgressDashboardTab';
import LearningPathTab from './components/LearningPathTab';
import SettingsTab from './components/SettingsTab';
import FlashcardsModal from './components/FlashcardsModal';
import ErrorBoundary from './components/ErrorBoundary';

function MainApp() {
  const { user, isAuthenticated, loginDemo } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [isLandingView, setIsLandingView] = useState(() => !localStorage.getItem('ai_teacher_token'));
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login');
  const [flashcardsModalOpen, setFlashcardsModalOpen] = useState(false);
  const [flashcardsSessionId, setFlashcardsSessionId] = useState(null);

  const [status, setStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [sourceMode, setSourceMode] = useState('General knowledge topic mode');
  
  // Active lesson session state
  const [sessionId, setSessionId] = useState(null);
  const [lessonPlan, setLessonPlan] = useState(null);
  const [conceptIndex, setConceptIndex] = useState(0);
  const [recentSession, setRecentSession] = useState(null);

  // Set initial landing view based on auth
  useEffect(() => {
    if (!isAuthenticated) {
      setIsLandingView(true);
    }
  }, [isAuthenticated]);

  // Initial data bootstrap
  useEffect(() => {
    // 1. Fetch system status
    axios.get('/api/status')
      .then(res => setStatus(res.data))
      .catch(err => console.error('Status fetch error:', err));

    // 2. Fetch default or user learner profile
    axios.get('/api/profile')
      .then(res => setProfile(res.data))
      .catch(err => console.error('Profile fetch error:', err));

    // 3. Fetch recent session
    axios.get('/api/sessions/recent')
      .then(res => {
        if (res.data?.session) {
          setRecentSession(res.data.session);
        }
      })
      .catch(err => console.error('Recent session fetch error:', err));
  }, [isAuthenticated]);

  const handleOpenAuth = (mode = 'login') => {
    setAuthModalMode(mode);
    setAuthModalOpen(true);
  };

  // Launch Hackathon Demo Mode
  const handleLaunchDemo = async () => {
    try {
      if (!isAuthenticated) {
        await loginDemo();
      }
      const res = await axios.post('/api/demo/ohms-law');
      setSessionId(res.data.session_id);
      setLessonPlan(res.data.state.lesson_plan);
      setConceptIndex(0);
      setSourceMode('General knowledge topic mode');
      setIsLandingView(false);
      setActiveTab('lesson');
    } catch (err) {
      console.error('Failed to launch demo:', err);
    }
  };

  // Resume recent session
  const handleResumeRecent = () => {
    if (recentSession && recentSession.plan) {
      setSessionId(recentSession.session_id);
      setLessonPlan(recentSession.plan);
      setConceptIndex(recentSession.current_concept_index || 0);
      setIsLandingView(false);
      setActiveTab('lesson');
    }
  };

  // Plan generated from topic or document
  const handlePlanGenerated = (newSessionId, state) => {
    setSessionId(newSessionId);
    setLessonPlan(state.lesson_plan);
    setConceptIndex(0);
    setIsLandingView(false);
    setActiveTab('plan');
  };

  // Regenerate plan
  const handleRegeneratePlan = async () => {
    if (!lessonPlan) return;
    try {
      const res = await axios.post('/api/lessons/plan', {
        topic: lessonPlan.lesson_title,
        source_mode: sourceMode
      });
      setSessionId(res.data.session_id);
      setLessonPlan(res.data.state.lesson_plan);
      setConceptIndex(0);
    } catch (err) {
      console.error('Failed to regenerate plan:', err);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E1A] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Sticky Top Header Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        status={status}
        profile={profile}
        sourceMode={sourceMode}
        onOpenAuth={handleOpenAuth}
        onLaunchDemo={handleLaunchDemo}
        isLandingView={isLandingView}
        setIsLandingView={setIsLandingView}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ErrorBoundary onReset={() => { setIsLandingView(true); setActiveTab('home'); }}>
          {/* Landing Page for Visitors / Marketing */}
          {isLandingView && (
            <LandingPage
              onOpenAuth={handleOpenAuth}
              onLaunchDemo={handleLaunchDemo}
            />
          )}

          {/* Authenticated Workspace Tabs */}
          {!isLandingView && (
            <>
              {activeTab === 'home' && (
                <HomeTab
                  setActiveTab={setActiveTab}
                  onLaunchDemo={handleLaunchDemo}
                  recentSession={recentSession}
                  onResumeSession={handleResumeRecent}
                />
              )}

              {activeTab === 'profile' && (
                <ProfileTab
                  profile={user || profile}
                  onUpdateProfile={(updated) => setProfile(updated)}
                />
              )}

              {activeTab === 'source' && (
                <SourceTopicTab
                  onPlanGenerated={handlePlanGenerated}
                  setSourceMode={setSourceMode}
                />
              )}

              {activeTab === 'path' && (
                <LearningPathTab
                  onStartLessonWithTopic={async (stageTopic) => {
                    setSourceMode('General knowledge topic mode');
                    try {
                      const res = await axios.post('/api/lessons/plan', {
                        topic: stageTopic,
                        source_mode: 'General knowledge topic mode'
                      });
                      handlePlanGenerated(res.data.session_id, res.data.state);
                    } catch (err) {
                      console.error('Failed to start stage lesson:', err);
                    }
                  }}
                />
              )}

              {activeTab === 'plan' && (
                <LessonPlanTab
                  lessonPlan={lessonPlan}
                  onStartLesson={() => setActiveTab('lesson')}
                  onRegeneratePlan={handleRegeneratePlan}
                />
              )}

              {activeTab === 'lesson' && (
                <InteractiveLessonTab
                  sessionId={sessionId}
                  lessonPlan={lessonPlan}
                  conceptIndex={conceptIndex}
                  setConceptIndex={setConceptIndex}
                  onProceedToCheckpoint={() => setActiveTab('checkpoint')}
                  onOpenFlashcards={(sid) => {
                    setFlashcardsSessionId(sid || sessionId);
                    setFlashcardsModalOpen(true);
                  }}
                />
              )}

              {activeTab === 'checkpoint' && (
                <CheckpointTab
                  sessionId={sessionId}
                  lessonPlan={lessonPlan}
                  conceptIndex={conceptIndex}
                  onAdvanceConcept={(nextIdx) => {
                    setConceptIndex(nextIdx);
                    setActiveTab('lesson');
                  }}
                  onGoToAssessment={() => setActiveTab('assessment')}
                />
              )}

              {activeTab === 'assessment' && (
                <AssessmentTab
                  sessionId={sessionId}
                  lessonPlan={lessonPlan}
                  onRestartLesson={() => setActiveTab('source')}
                />
              )}

              {activeTab === 'progress' && (
                <ProgressDashboardTab
                  setActiveTab={setActiveTab}
                />
              )}

              {activeTab === 'settings' && (
                <SettingsTab
                  status={status}
                />
              )}
            </>
          )}
        </ErrorBoundary>
      </main>

      {/* Active Recall Flashcards Modal (Section 18) */}
      {flashcardsModalOpen && flashcardsSessionId && (
        <FlashcardsModal
          sessionId={flashcardsSessionId}
          onClose={() => setFlashcardsModalOpen(false)}
        />
      )}

      {/* Auth Modal (Sign in / Sign up) */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authModalMode}
        onSuccess={() => {
          setIsLandingView(false);
          setActiveTab('home');
        }}
      />

      {/* Global Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-base">👩‍🏫</span>
            <span className="font-semibold text-slate-400">AI Teacher Platform</span>
            <span>&bull;</span>
            <span>FastAPI + React Vite + SQLite</span>
          </div>
          <div className="flex items-center space-x-4 text-[11px]">
            <button onClick={() => handleOpenAuth('login')} className="hover:text-slate-300">Sign In</button>
            <button onClick={() => handleOpenAuth('signup')} className="hover:text-slate-300">Create Account</button>
            <button onClick={handleLaunchDemo} className="hover:text-amber-400 text-amber-500/90 font-medium">1-Click Demo</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
