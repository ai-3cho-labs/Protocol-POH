'use client';

import { useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/cn';

// Drill sprite sheet: 3 columns × 4 rows, each frame 64×64px (192×256 total)
const FRAME_WIDTH = 64;
const FRAME_HEIGHT = 64;
const COLUMNS = 3;

// Animation rows in sprite sheet
const ANIMATION_ROWS = {
  drilling: 0,     // Drilling forward
  drillingAlt: 1,  // Drilling from different angle
  drillingDown: 2, // Drilling downward
  idle: 3,         // Idle stance with drill
} as const;

type AnimationState = keyof typeof ANIMATION_ROWS;

// Per-frame X offsets to anchor character in place (if needed for sprite drift)
const FRAME_OFFSETS: Record<AnimationState, number[]> = {
  drilling:     [0, 0, 0],
  drillingAlt:  [0, 0, 0],
  drillingDown: [0, 0, 0],
  idle:         [0, 0, 0],
};

interface PixelMinerProps {
  scale?: number;
  animation?: AnimationState;
  /** Milliseconds per frame */
  frameTime?: number;
  className?: string;
  /** Flip horizontally */
  flipX?: boolean;
}

// Sprite layer paths (drill animation)
const SPRITE_LAYERS = [
  '/sprites/character/tools_drill/character_body/character_tools_drill_body_light_with_specs.png',
  '/sprites/character/tools_drill/clothes/full_body/overhalls/character_tools_drill_clothes_fullbody_overhalls_blue.png',
  '/sprites/character/tools_drill/hairstyles/radical_curve/character_tools_drill_hairstyles_radical_curve_brown_dark.png',
];

/**
 * Canvas-based animated pixel miner.
 * Uses requestAnimationFrame for smooth, frame-perfect animation.
 */
export function PixelMiner({
  scale = 2,
  animation = 'drilling',
  frameTime = 150, // 150ms per frame (~7 FPS for drill vibration effect)
  className,
  flipX = false,
}: PixelMinerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const frameRef = useRef(0);
  const lastFrameTimeRef = useRef(0);
  const animationIdRef = useRef<number>(0);

  // Sprite size
  const spriteWidth = Math.floor(FRAME_WIDTH * scale);
  const spriteHeight = Math.floor(FRAME_HEIGHT * scale);

  // Canvas size (add padding to center sprite)
  const padding = Math.floor(8 * scale); // 8px padding on each side
  const width = spriteWidth + padding * 2;
  const height = spriteHeight + padding * 2;

  const row = ANIMATION_ROWS[animation];

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const images = imagesRef.current;
    if (!canvas || images.length < SPRITE_LAYERS.length) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Disable smoothing for pixel art
    ctx.imageSmoothingEnabled = false;

    const frame = frameRef.current;
    const srcX = frame * FRAME_WIDTH;
    const srcY = row * FRAME_HEIGHT;

    // Get per-frame offset to prevent sliding
    const frameOffsetX = (FRAME_OFFSETS[animation]?.[frame] ?? 0) * scale;

    // Center position (sprite drawn in middle of canvas)
    const destX = padding + frameOffsetX;
    const destY = padding;

    // Handle flip
    if (flipX) {
      ctx.save();
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }

    // Draw each layer in order (body, overalls, hair)
    for (const img of images) {
      if (img.complete && img.naturalWidth > 0) {
        ctx.drawImage(
          img,
          srcX, srcY, FRAME_WIDTH, FRAME_HEIGHT,  // source
          destX, destY, spriteWidth, spriteHeight  // destination (centered)
        );
      }
    }

    if (flipX) {
      ctx.restore();
    }
  }, [width, height, spriteWidth, spriteHeight, padding, row, flipX, animation, scale]);

  const animate = useCallback((timestamp: number) => {
    // Calculate time since last frame
    const elapsed = timestamp - lastFrameTimeRef.current;

    if (elapsed >= frameTime) {
      // Advance frame
      frameRef.current = (frameRef.current + 1) % COLUMNS;
      lastFrameTimeRef.current = timestamp - (elapsed % frameTime);
      render();
    }

    animationIdRef.current = requestAnimationFrame(animate);
  }, [frameTime, render]);

  // Load sprite images
  useEffect(() => {
    let mounted = true;

    const loadImage = (src: string): Promise<HTMLImageElement> => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
      });
    };

    Promise.all(SPRITE_LAYERS.map(loadImage))
      .then((loadedImages) => {
        if (mounted) {
          imagesRef.current = loadedImages;
          render(); // Initial render
        }
      })
      .catch((err) => {
        console.error('Failed to load miner sprites:', err);
      });

    return () => {
      mounted = false;
    };
  }, [render]);

  // Start animation loop
  useEffect(() => {
    lastFrameTimeRef.current = performance.now();
    animationIdRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
    };
  }, [animate]);

  // Re-render when animation state changes
  useEffect(() => {
    frameRef.current = 0; // Reset to first frame
    render();
  }, [animation, render]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className={cn('pointer-events-none', className)}
      style={{
        imageRendering: 'pixelated',
        // Debug: red border shows canvas bounds
        // border: '1px solid red',
      }}
      role="img"
      aria-label={`Animated pixel miner - ${animation}`}
    />
  );
}

// Export types for external use
export type { AnimationState, PixelMinerProps };
