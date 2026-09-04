import React, { useState, useRef, useEffect } from 'react';
import { 
  Home, 
  User, 
  BookOpen, 
  ListTree, 
  GraduationCap, 
  HelpCircle, 
  BarChart3, 
  TrendingUp, 
  Settings,
  Sparkles,
  FileText,
  Globe,
  Volume2,
  LogOut,
  ChevronDown,
  Zap,
  Compass
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'profile', label: 'Learner Profile', icon: User },
  { id: 'source', label: 'Source & Topic', icon: BookOpen },
  { id: 'path', label: 'Learning Path', icon: Compass },
  { id: 'plan', label: 'Lesson Plan', icon: ListTree },
  { id: 'lesson', label: 'Interactive Lesson', icon: GraduationCap },
  { id: 'checkpoint', label: 'Checkpoints', icon: HelpCircle },
  { id: 'assessment', label: 'Assessment & Report', icon: BarChart3 },
  { id: 'progress', label: 'Progress Dashboard', icon: TrendingUp },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  status, 
  profile, 
  sourceMode, 
  onOpenAuth,
  onLaunchDemo,
  isLandingView,
  setIsLandingView
}) {
  const { user, isAuthenticated, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    setIsLandingView(true);
  };

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Brand & Top Bar */}
        <div className="flex items-center justify-between py-3 border-b border-slate-800/60">
          {/* Logo */}
          <div 
            className="flex items-center space-x-3 cursor-pointer" 
            onClick={() => {
              if (isAuthenticated) {
                setIsLandingView(false);
                setActiveTab('home');
              } else {
                setIsLandingView(true);
              }
            }}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <span className="text-2xl">👩‍🏫</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold text-white tracking-tight">AI Teacher</h1>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Full-Stack v2.0
                </span>
              </div>
              <p className="text-xs text-slate-400">Adaptive Multilingual Video Learning Platform</p>
            </div>
          </div>

          {/* Right Header Controls */}
          <div className="flex items-center space-x-3">
            {/* Status Badges for Classroom (when logged in or in workspace) */}
            {(!isLandingView && isAuthenticated) && (
              <div className="hidden lg:flex items-center space-x-2.5">
                {sourceMode === 'Document-grounded mode' ? (
                  <span className="flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <FileText className="w-3.5 h-3.5" />
                    <span>Document Grounded</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    <Globe className="w-3.5 h-3.5" />
                    <span>General Topic</span>
                  </span>
                )}

                <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                  <Volume2 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>{user?.language || profile?.language || 'Hinglish'}</span>
                </span>
              </div>
            )}

            {/* If Not Authenticated */}
            {!isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <button
                  onClick={onLaunchDemo}
                  className="hidden sm:flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 transition"
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span>Demo</span>
                </button>

                <button
                  onClick={() => onOpenAuth('login')}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition"
                >
                  Sign In
                </button>

                <button
                  onClick={() => onOpenAuth('signup')}
                  className="flex items-center space-x-1 px-4 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 shadow-md shadow-indigo-600/20 transition"
                >
                  <span>Get Started</span>
                </button>
              </div>
            ) : (
              /* Authenticated User Menu */
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center space-x-2 p-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 text-left transition"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center font-bold text-white text-xs shadow-sm">
                    {user?.display_name ? user.display_name.charAt(0).toUpperCase() : 'S'}
                  </div>
                  <div className="hidden sm:block pr-1">
                    <p className="text-xs font-semibold text-white leading-tight">{user?.display_name || 'Student'}</p>
                    <p className="text-[10px] text-slate-400 capitalize">{user?.education_level || 'Learner'}</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                </button>

                {/* Dropdown Menu */}
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl py-2 z-50 animate-fadeIn text-xs">
                    <div className="px-4 py-2 border-b border-slate-800/80">
                      <p className="font-bold text-white">{user?.display_name}</p>
                      <p className="text-slate-400 truncate text-[11px]">{user?.email || 'demo@aiteacher.io'}</p>
                    </div>

                    <button
                      onClick={() => {
                        setIsLandingView(false);
                        setActiveTab('profile');
                        setDropdownOpen(false);
                      }}
                      className="w-full flex items-center space-x-2 px-4 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800 transition text-left"
                    >
                      <User className="w-4 h-4 text-indigo-400" />
                      <span>Learner Profile</span>
                    </button>

                    <button
                      onClick={() => {
                        setIsLandingView(false);
                        setActiveTab('progress');
                        setDropdownOpen(false);
                      }}
                      className="w-full flex items-center space-x-2 px-4 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800 transition text-left"
                    >
                      <TrendingUp className="w-4 h-4 text-emerald-400" />
                      <span>Learning Progress</span>
                    </button>

                    <button
                      onClick={() => {
                        setIsLandingView(false);
                        setActiveTab('settings');
                        setDropdownOpen(false);
                      }}
                      className="w-full flex items-center space-x-2 px-4 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800 transition text-left"
                    >
                      <Settings className="w-4 h-4 text-slate-400" />
                      <span>Settings & Cache</span>
                    </button>

                    <div className="my-1 border-t border-slate-800/80"></div>

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-2 px-4 py-2.5 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 transition text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Stepper Navigation Tabs (visible when authenticated or inside classroom) */}
        {(!isLandingView || isAuthenticated) && (
          <nav className="flex space-x-1 overflow-x-auto py-2 scrollbar-none">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = !isLandingView && activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setIsLandingView(false);
                    setActiveTab(item.id);
                  }}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        )}
      </div>
    </header>
  );
}
