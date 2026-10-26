'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Check, Copy, X } from 'lucide-react';

interface CopyButtonProps {
  text: string;
  isDark: boolean;
  className?: string;
}

type CopyStatus = 'idle' | 'copied' | 'failed';

const FEEDBACK_MS = 1500;

/**
 * Copy-to-clipboard button with click feedback: it presses in when clicked,
 * then briefly turns green with a check mark ("Copied!"), or red if the
 * clipboard write fails. Animations respect prefers-reduced-motion.
 */
export const CopyButton: React.FC<CopyButtonProps> = ({ text, isDark, className = '' }) => {
  const [status, setStatus] = useState<CopyStatus>('idle');
  const resetTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(resetTimer.current), []);

  const handleClick = async (e: React.MouseEvent) => {
    // The button sits inside a clickable card that selects the query
    e.stopPropagation();

    let copied = true;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      copied = false;
    }

    setStatus(copied ? 'copied' : 'failed');
    clearTimeout(resetTimer.current);
    resetTimer.current = setTimeout(() => setStatus('idle'), FEEDBACK_MS);
  };

  const colors =
    status === 'copied'
      ? isDark ? 'bg-green-600 text-white' : 'bg-green-500 text-white'
      : status === 'failed'
        ? isDark ? 'bg-red-600 text-white' : 'bg-red-500 text-white'
        : isDark ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white';

  const Icon = status === 'copied' ? Check : status === 'failed' ? X : Copy;
  const label = status === 'copied' ? 'Copied!' : status === 'failed' ? 'Failed' : 'Copy';

  return (
    <button
      onClick={handleClick}
      title="Copy query"
      aria-live="polite"
      className={`flex items-center justify-center gap-1 px-2 py-1 rounded text-xs font-medium transition duration-150 motion-safe:active:scale-90 ${colors} ${className}`}
    >
      {/* key remounts the icon so the pop animation replays on each change */}
      <Icon key={status} size={12} className={status === 'idle' ? '' : 'motion-safe:animate-pop'} />
      {label}
    </button>
  );
};
