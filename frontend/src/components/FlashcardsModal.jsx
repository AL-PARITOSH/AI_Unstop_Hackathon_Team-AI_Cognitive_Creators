import React, { useState, useEffect } from 'react';
import { X, Layers, ChevronLeft, ChevronRight, RotateCw, CheckCircle2, Sparkles } from 'lucide-react';
import axios from 'axios';

export default function FlashcardsModal({ sessionId, onClose }) {
  const [deck, setDeck] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [masteredCards, setMasteredCards] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    setError('');

    axios.get(`/api/lessons/${sessionId}/flashcards`)
      .then(res => {
        setDeck(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Flashcards fetch error:', err);
        setError('Failed to generate flashcard deck for this lesson.');
        setLoading(false);
      });
  }, [sessionId]);

  const cards = deck?.flashcards || [];
  const currentCard = cards[currentIndex];

  const handleNext = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
    }
  };

  const toggleMastered = (cardId) => {
    setMasteredCards(prev => ({
      ...prev,
      [cardId]: !prev[cardId]
    }));
  };

  const masteredCount = Object.values(masteredCards).filter(Boolean).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 flex items-center justify-center">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <span>Active Recall Flashcards</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-300 border border-sky-500/20">
                  {deck ? `${masteredCount} / ${cards.length} Mastered` : 'Loading'}
                </span>
              </h3>
              <p className="text-xs text-slate-400 truncate max-w-md">
                {deck?.lesson_title || 'Generating concept review deck...'}
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 sm:p-8 flex-1 flex flex-col items-center justify-center min-h-[380px]">
          {loading ? (
            <div className="text-center space-y-3">
              <div className="w-10 h-10 border-4 border-sky-500/20 border-t-sky-500 rounded-full animate-spin mx-auto"></div>
              <p className="text-sm text-slate-300">AI Teacher synthesizing high-yield flashcards...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm text-center">
              {error}
            </div>
          ) : !currentCard ? (
            <div className="text-slate-400 text-sm">No flashcards available.</div>
          ) : (
            <div className="w-full space-y-6 flex flex-col items-center">
              {/* Progress Bar */}
              <div className="w-full flex items-center justify-between text-xs text-slate-400 font-mono">
                <span>Card {currentIndex + 1} of {cards.length}</span>
                <span className="capitalize px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  Difficulty: {currentCard.difficulty}
                </span>
              </div>

              {/* Interactive Flip Card */}
              <div
                onClick={() => setIsFlipped(!isFlipped)}
                className={`w-full min-h-[220px] sm:min-h-[260px] p-6 sm:p-8 rounded-2xl border cursor-pointer transition-all duration-300 flex flex-col justify-between select-none ${
                  isFlipped
                    ? 'bg-slate-950/90 border-sky-500/40 shadow-xl shadow-sky-500/10'
                    : 'bg-slate-800/60 hover:bg-slate-800/80 border-slate-700 hover:border-slate-600 shadow-lg'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className={`px-2.5 py-1 rounded-full font-bold uppercase tracking-wider text-[10px] ${
                    isFlipped ? 'bg-emerald-500/20 text-emerald-300' : 'bg-sky-500/20 text-sky-300'
                  }`}>
                    {isFlipped ? '💡 Explanation & Analogy' : '❓ Question (Click to Flip)'}
                  </span>
                  <RotateCw className="w-4 h-4 text-slate-400" />
                </div>

                <div className="py-4 text-center">
                  {isFlipped ? (
                    <div className="space-y-3 animate-fadeIn">
                      <p className="text-base sm:text-lg text-white font-medium leading-relaxed">
                        {currentCard.back_explanation}
                      </p>
                      {currentCard.analogy_or_mnemonic && (
                        <div className="p-3 rounded-xl bg-sky-950/40 border border-sky-500/20 text-xs text-sky-200">
                          <strong>💡 Analogy:</strong> {currentCard.analogy_or_mnemonic}
                        </div>
                      )}
                    </div>
                  ) : (
                    <h3 className="text-lg sm:text-xl font-bold text-white leading-snug">
                      {currentCard.front_question}
                    </h3>
                  )}
                </div>

                <div className="text-[11px] text-slate-500 text-center">
                  {isFlipped ? 'Click anywhere on card to see question again' : 'Click to reveal explanation'}
                </div>
              </div>

              {/* Card Navigation Controls */}
              <div className="w-full flex items-center justify-between pt-2">
                <button
                  onClick={handlePrev}
                  disabled={currentIndex === 0}
                  className="flex items-center space-x-1 py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-semibold text-slate-300 transition"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>

                <button
                  onClick={() => toggleMastered(currentCard.id)}
                  className={`flex items-center space-x-1.5 py-2 px-4 rounded-xl text-xs font-semibold border transition ${
                    masteredCards[currentCard.id]
                      ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                      : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{masteredCards[currentCard.id] ? 'Mastered!' : 'Mark Mastered'}</span>
                </button>

                <button
                  onClick={handleNext}
                  disabled={currentIndex === cards.length - 1}
                  className="flex items-center space-x-1 py-2 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs font-semibold text-slate-300 transition"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

