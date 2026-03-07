'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import AuthGuard from '@/components/AuthGuard';
import { getVideo, analyzeVideo, Video, ApiError } from '@/app/lib/api';

function VideoContent() {
  const params = useParams();
  const videoId = params.id as string;
  const [video, setVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const fetchVideo = useCallback(async () => {
    try {
      const data = await getVideo(videoId);
      setVideo(data);
      return data;
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
      return null;
    } finally {
      setLoading(false);
    }
  }, [videoId]);

  useEffect(() => {
    fetchVideo();
  }, [fetchVideo]);

  // Auto-polling while processing
  useEffect(() => {
    if (!video || video.status !== 'processing') return;

    const interval = setInterval(async () => {
      const updated = await fetchVideo();
      if (updated && updated.status !== 'processing') {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [video?.status, fetchVideo]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError('');
    try {
      const updated = await analyzeVideo(videoId);
      setVideo(updated);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-[#FF6B35] border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!video) {
    return (
      <div className="min-h-screen bg-zinc-950 flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-zinc-400 mb-4">Video non trovato</p>
          <Link href="/dashboard" className="text-[#FF6B35] hover:underline">
            Torna alla dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950">
      <header className="border-b border-zinc-800 px-4 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-black text-[#FF6B35]">KILTER UP</Link>
          <Link href="/dashboard" className="text-sm text-zinc-400 hover:text-white transition-colors">
            &larr; Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* File info */}
        <div className="mb-6">
          <h1 className="text-xl font-bold text-white truncate">
            {video.original_file_path?.split('/').pop() || 'Video'}
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            {new Date(video.created_at).toLocaleDateString('it-IT', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* PENDING */}
        {video.status === 'pending' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 text-center">
            <div className="text-5xl mb-4">🎬</div>
            <h2 className="text-lg font-semibold text-white mb-2">Video caricato</h2>
            <p className="text-zinc-400 mb-6">Clicca per avviare l&apos;analisi con Gemini AI</p>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="px-8 py-3 bg-[#FF6B35] hover:bg-[#ff7d4d] text-white font-bold rounded-xl transition-colors disabled:opacity-50"
            >
              {analyzing ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  Avvio analisi...
                </span>
              ) : (
                'Analizza ora'
              )}
            </button>
          </div>
        )}

        {/* PROCESSING */}
        {video.status === 'processing' && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-8 text-center">
            <div className="relative w-16 h-16 mx-auto mb-6">
              <div className="absolute inset-0 border-4 border-[#FF6B35]/20 rounded-full" />
              <div className="absolute inset-0 border-4 border-[#FF6B35] border-t-transparent rounded-full animate-spin" />
            </div>
            <h2 className="text-lg font-semibold text-white mb-2">Analisi in corso</h2>
            <p className="text-zinc-400">Gemini sta analizzando la tua tecnica...</p>
            <div className="mt-4 flex items-center justify-center gap-1.5">
              <span className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-[#FF6B35] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        {/* FAILED */}
        {video.status === 'failed' && (
          <div className="bg-zinc-900 border border-red-500/30 rounded-2xl p-8 text-center">
            <div className="text-5xl mb-4">❌</div>
            <h2 className="text-lg font-semibold text-white mb-2">Analisi fallita</h2>
            <p className="text-zinc-400 mb-6">
              Si è verificato un errore durante l&apos;analisi del video.
            </p>
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="px-8 py-3 bg-[#FF6B35] hover:bg-[#ff7d4d] text-white font-bold rounded-xl transition-colors disabled:opacity-50"
            >
              {analyzing ? 'Riprovo...' : 'Riprova'}
            </button>
          </div>
        )}

        {/* COMPLETED */}
        {video.status === 'completed' && (
          <div className="space-y-4">
            {/* Grade badge */}
            {video.grade_estimate && (
              <div className="bg-zinc-900 border border-[#FF6B35]/40 rounded-2xl p-6 text-center">
                <p className="text-sm text-zinc-400 mb-2">Grado stimato</p>
                <span className="inline-block px-6 py-3 bg-[#FF6B35] text-white text-3xl font-black rounded-xl">
                  {video.grade_estimate}
                </span>
              </div>
            )}

            {/* Form feedback */}
            {video.form_feedback && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-[#FF6B35] uppercase tracking-wide mb-3">
                  Feedback sulla tecnica
                </h3>
                <p className="text-zinc-200 leading-relaxed whitespace-pre-wrap">
                  {video.form_feedback}
                </p>
              </div>
            )}

            {/* Body position */}
            {video.body_position && Object.keys(video.body_position).length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-[#FF6B35] uppercase tracking-wide mb-3">
                  Posizione del corpo
                </h3>
                <div className="space-y-3">
                  {Object.entries(video.body_position).map(([key, value]) => (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-zinc-400 capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="text-white font-medium">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Key weaknesses */}
            {video.key_weaknesses && video.key_weaknesses.length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-[#FF6B35] uppercase tracking-wide mb-3">
                  Punti deboli
                </h3>
                <ul className="space-y-2">
                  {video.key_weaknesses.map((weakness, i) => (
                    <li key={i} className="flex items-start gap-3 text-zinc-300">
                      <span className="text-yellow-500 mt-0.5">&#9888;&#65039;</span>
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Holds analysis */}
            {video.holds_analysis && video.holds_analysis.length > 0 && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-[#FF6B35] uppercase tracking-wide mb-3">
                  Analisi prese
                </h3>
                <div className="space-y-2">
                  {video.holds_analysis.map((hold, i) => (
                    <div key={i} className="p-3 bg-zinc-800/50 rounded-xl text-zinc-300 text-sm">
                      {typeof hold === 'string' ? hold : JSON.stringify(hold)}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Notes */}
            {video.notes && (
              <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-zinc-500 uppercase tracking-wide mb-2">
                  Note
                </h3>
                <p className="text-zinc-400">{video.notes}</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default function VideoPage() {
  return (
    <AuthGuard>
      <VideoContent />
    </AuthGuard>
  );
}
