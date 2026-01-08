'use client';

import { useState, useEffect, useRef } from 'react';

export interface CountdownResult {
  /** Hours remaining */
  hours: number;
  /** Minutes remaining */
  minutes: number;
  /** Seconds remaining */
  seconds: number;
  /** Total seconds remaining */
  totalSeconds: number;
  /** Is countdown complete */
  isComplete: boolean;
  /** Formatted string (HH:MM:SS) */
  formatted: string;
  /** Formatted string (compact, e.g., "2h 30m") */
  formattedCompact: string;
}

/**
 * Hook for countdown timer functionality
 * @param targetHours - Hours until target (can be fractional)
 * @param onComplete - Callback when countdown completes
 */
export function useCountdown(
  targetHours: number | null,
  onComplete?: () => void
): CountdownResult {
  const [totalSeconds, setTotalSeconds] = useState(() =>
    targetHours !== null ? Math.max(0, Math.floor(targetHours * 3600)) : 0
  );
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  // Update when targetHours changes
  useEffect(() => {
    if (targetHours !== null) {
      setTotalSeconds(Math.max(0, Math.floor(targetHours * 3600)));
    }
  }, [targetHours]);

  // Countdown interval
  useEffect(() => {
    if (totalSeconds <= 0) return;

    const interval = setInterval(() => {
      setTotalSeconds((prev) => {
        const next = prev - 1;
        if (next <= 0) {
          onCompleteRef.current?.();
          return 0;
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [totalSeconds > 0]); // Only restart interval when transitioning to/from 0

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const formatted = [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    seconds.toString().padStart(2, '0'),
  ].join(':');

  const formattedCompact =
    hours > 0
      ? `${hours}h ${minutes}m`
      : minutes > 0
        ? `${minutes}m ${seconds}s`
        : `${seconds}s`;

  return {
    hours,
    minutes,
    seconds,
    totalSeconds,
    isComplete: totalSeconds <= 0,
    formatted,
    formattedCompact,
  };
}

/**
 * Hook for animated number transitions
 * @param targetValue - The target value to animate to
 * @param duration - Animation duration in ms
 */
export function useAnimatedNumber(
  targetValue: number,
  duration: number = 500
): number {
  const [displayValue, setDisplayValue] = useState(targetValue);
  const animationRef = useRef<number>();
  const startTimeRef = useRef<number>();
  const startValueRef = useRef<number>(targetValue);

  useEffect(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    startValueRef.current = displayValue;
    startTimeRef.current = undefined;

    const animate = (timestamp: number) => {
      if (!startTimeRef.current) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current =
        startValueRef.current + (targetValue - startValueRef.current) * eased;

      setDisplayValue(current);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      }
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [targetValue, duration]);

  return displayValue;
}

/**
 * Hook for a continuously ticking counter based on earning rate
 * Creates the effect of watching rewards accumulate in real-time
 * @param baseValue - The base value from API (resyncs when this changes)
 * @param ratePerHour - The rate of increase per hour
 * @param updateInterval - How often to update the display in ms (default 100ms)
 */
export function useTickingCounter(
  baseValue: number,
  ratePerHour: number | null,
  updateInterval: number = 100
): number {
  const [displayValue, setDisplayValue] = useState(baseValue);
  const baseValueRef = useRef(baseValue);
  const lastSyncTimeRef = useRef(Date.now());

  // Resync when base value changes (new API data)
  useEffect(() => {
    baseValueRef.current = baseValue;
    lastSyncTimeRef.current = Date.now();
    setDisplayValue(baseValue);
  }, [baseValue]);

  // Tick up continuously based on rate
  useEffect(() => {
    if (ratePerHour === null || ratePerHour <= 0) {
      return;
    }

    const ratePerMs = ratePerHour / 3600000; // Convert to per millisecond

    const interval = setInterval(() => {
      const elapsed = Date.now() - lastSyncTimeRef.current;
      const increment = elapsed * ratePerMs;
      setDisplayValue(baseValueRef.current + increment);
    }, updateInterval);

    return () => clearInterval(interval);
  }, [ratePerHour, updateInterval]);

  return displayValue;
}
