'use client';

import { useState, useCallback, useEffect } from 'react';
import type { UserMiningStats } from '@/types/models';
import { generateShareCard, downloadBlob, type ShareCardExtras } from '@/lib/shareCard';
import { cn } from '@/lib/cn';

interface ShareCardProps {
  stats: UserMiningStats | null;
  /** Total holders count for percentile calculation */
  totalHolders?: number;
  /** Lifetime earnings in $GOLD */
  lifetimeEarnings?: number;
  /** Lifetime earnings in USD */
  lifetimeEarningsUsd?: number;
  /** Pending reward in USD */
  pendingRewardUsd?: number;
  className?: string;
}

/**
 * Share button that generates a PNG stats card with preview modal.
 */
export function ShareCard({ stats, totalHolders, lifetimeEarnings, lifetimeEarningsUsd, pendingRewardUsd, className }: ShareCardProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewBlob, setPreviewBlob] = useState<Blob | null>(null);
  const [isClosing, setIsClosing] = useState(false);
  const [copied, setCopied] = useState(false);

  // Generate and show preview
  const handleShare = useCallback(async () => {
    if (!stats || isGenerating) return;

    setIsGenerating(true);
    try {
      const extras: ShareCardExtras = {
        totalHolders,
        lifetimeEarnings,
        lifetimeEarningsUsd,
        pendingRewardUsd,
      };
      const blob = await generateShareCard(stats, extras);
      const url = URL.createObjectURL(blob);
      setPreviewBlob(blob);
      setPreviewUrl(url);
    } catch (error) {
      console.error('Failed to generate share card:', error);
    } finally {
      setIsGenerating(false);
    }
  }, [stats, isGenerating, totalHolders, lifetimeEarnings]);

  // Close modal with animation
  const handleClose = useCallback(() => {
    setIsClosing(true);
    setTimeout(() => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(null);
      setPreviewBlob(null);
      setIsClosing(false);
    }, 200);
  }, [previewUrl]);

  // Download the image
  const handleDownload = useCallback(() => {
    if (!previewBlob) return;
    const filename = `cpu-stats-${Date.now()}.png`;
    downloadBlob(previewBlob, filename);
  }, [previewBlob]);

  // Copy image to clipboard
  const handleCopy = useCallback(async () => {
    if (!previewBlob) return;
    try {
      await navigator.clipboard.write([
        new ClipboardItem({ 'image/png': previewBlob })
      ]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  }, [previewBlob]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && previewUrl) {
        handleClose();
      }
    };

    if (previewUrl) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [previewUrl, handleClose]);

  // Cleanup URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  return (
    <>
      {/* Share Button */}
      <button
        onClick={handleShare}
        disabled={!stats || isGenerating}
        className={cn(
          'px-8 py-3 rounded-xl text-sm font-medium',
          'bg-amber-500/10 text-amber-400 border border-amber-500/20',
          'transition-all duration-200',
          'hover:bg-amber-500/20 hover:border-amber-500/40',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          className
        )}
      >
        {isGenerating ? 'Generating...' : 'Share'}
      </button>

      {/* Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 z-50">
          {/* Backdrop */}
          <div
            className={cn(
              'absolute inset-0 bg-black/80 backdrop-blur-sm',
              'transition-opacity duration-200',
              isClosing && 'opacity-0'
            )}
            onClick={handleClose}
          />

          {/* Modal Content */}
          <div
            className={cn(
              'absolute bg-[#0a0a0a] border border-gray-800 overflow-hidden flex flex-col rounded-2xl',
              // Mobile: near full width with padding
              'inset-x-4 top-1/2 -translate-y-1/2 max-h-[85vh]',
              // Desktop: centered with max width
              'sm:inset-x-auto sm:left-1/2 sm:-translate-x-1/2 sm:w-full sm:max-w-[480px]',
              // Animation
              isClosing ? 'animate-fade-out' : 'animate-fade-in'
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
              <h2 className="text-base font-medium text-white">Share Your Stats</h2>
              <button
                onClick={handleClose}
                className="p-2 -mr-1 text-gray-400 hover:text-white active:scale-95 transition-all rounded-lg"
                aria-label="Close"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Image Preview */}
            <div className="p-4 flex-1 overflow-auto">
              <div className="rounded-xl overflow-hidden border border-gray-800 shadow-2xl">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={previewUrl}
                  alt="Share card preview"
                  className="w-full h-auto"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="p-4 pt-0 flex gap-3">
              <button
                onClick={handleDownload}
                className={cn(
                  'flex-1 px-6 py-3 rounded-xl text-sm font-medium',
                  'bg-white/10 text-white border border-white/20',
                  'transition-all duration-200',
                  'hover:bg-white/20 hover:border-white/40',
                  'active:scale-[0.98]'
                )}
              >
                Download
              </button>
              <button
                onClick={handleCopy}
                className={cn(
                  'flex-1 px-6 py-3 rounded-xl text-sm font-medium',
                  'transition-all duration-200',
                  'active:scale-[0.98]',
                  copied
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-amber-500/20 text-amber-400 border border-amber-500/30 hover:bg-amber-500/30 hover:border-amber-500/50'
                )}
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
