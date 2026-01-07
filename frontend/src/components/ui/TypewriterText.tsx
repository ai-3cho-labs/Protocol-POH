'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/cn';

export interface TypewriterTextProps {
  /** Text to animate */
  text: string;
  /** Speed in milliseconds per character */
  speed?: number;
  /** Delay before starting animation */
  delay?: number;
  /** Callback when animation completes */
  onComplete?: () => void;
  /** Show blinking cursor */
  showCursor?: boolean;
  /** Additional class names */
  className?: string;
}

/**
 * TypewriterText component
 * Animates text character by character for terminal aesthetic
 */
export function TypewriterText({
  text,
  speed = 50,
  delay = 0,
  onComplete,
  showCursor = true,
  className,
}: TypewriterTextProps) {
  const [displayText, setDisplayText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    let charIndex = 0;

    const startAnimation = () => {
      const typeNextChar = () => {
        if (charIndex < text.length) {
          setDisplayText(text.slice(0, charIndex + 1));
          charIndex++;
          timeout = setTimeout(typeNextChar, speed);
        } else {
          setIsComplete(true);
          onComplete?.();
        }
      };

      typeNextChar();
    };

    timeout = setTimeout(startAnimation, delay);

    return () => clearTimeout(timeout);
  }, [text, speed, delay, onComplete]);

  return (
    <span className={cn('font-mono', className)}>
      {displayText}
      {showCursor && !isComplete && (
        <span className="animate-blink text-white">_</span>
      )}
    </span>
  );
}

/**
 * TypewriterNumber component
 * Counts up to a number for animated stats display
 */
export function TypewriterNumber({
  value,
  duration = 1000,
  delay = 0,
  prefix = '',
  suffix = '',
  decimals = 0,
  onComplete,
  className,
}: {
  value: number;
  duration?: number;
  delay?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  onComplete?: () => void;
  className?: string;
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    let startTime: number;
    let animationFrame: number;

    const startAnimation = () => {
      startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out cubic
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = easeProgress * value;

        setDisplayValue(currentValue);

        if (progress < 1) {
          animationFrame = requestAnimationFrame(animate);
        } else {
          setDisplayValue(value);
          onComplete?.();
        }
      };

      animate();
    };

    timeout = setTimeout(startAnimation, delay);

    return () => {
      clearTimeout(timeout);
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [value, duration, delay, onComplete]);

  const formattedValue = decimals > 0
    ? displayValue.toFixed(decimals)
    : Math.floor(displayValue).toLocaleString();

  return (
    <span className={cn('font-mono tabular-nums', className)}>
      {prefix}{formattedValue}{suffix}
    </span>
  );
}
