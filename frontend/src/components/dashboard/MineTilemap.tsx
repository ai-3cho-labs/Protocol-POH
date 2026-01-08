'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { cn } from '@/lib/cn';
import { BLUE_TILES, getTileRect, CART_TILES, getCartTileRect, ORE_TILES, getOreRect, type TileMap } from './tiles-config';

// ============================================
// CONFIGURATION
// ============================================

const TILE_SIZE = 16;
const ORE_SPRITE_SRC = '/sprites/decorations/mining/ores/mining_ores.png';

// Shorthand aliases - Floor tiles
const W = BLUE_TILES.WALL_FLOOR;
const F = BLUE_TILES.FLOOR.MAIN;
const D = BLUE_TILES.DECOR;
const P = BLUE_TILES.PIT;
const WALLSHADOW = BLUE_TILES.WALLSHADOW;

// Shorthand aliases - Track tiles
const T = CART_TILES.STRAIGHT;
const TC = CART_TILES.CORNER;
const TE = CART_TILES.END;
const CART = CART_TILES.CART;

// Shorthand aliases - Ore tiles
const ORE = ORE_TILES;

const _ = null; // Empty/transparent

// ============================================
// TILEMAP LAYERS (16 × 16 tiles)
// Layer 1: Floor/Walls (base layer)
// Layer 2: Tracks (mine cart rails)
// Layer 3: Decorations (overlay)
// ============================================

// Base layer: walls and floor (6x6)
const FLOOR_LAYER: TileMap = [
  [W.TL, W.T,  W.T,  W.T,  W.T,  W.TR],
  [W.L,  W.IT, W.IT, W.IT, W.IT, W.R],
  [W.L,  F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    W.R],
  [W.BL, W.B,  W.B,  W.B,  W.B,  W.BR],
];

// Decoration layer: props on top of floor (6x6)
const DECOR_LAYER: TileMap = [
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
];

// Track layer: mine cart rails (6x6)
const TRACK_LAYER: TileMap = [
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
];

// Ore layer: mining ores from separate sprite sheet (6x6)
const ORE_LAYER: TileMap = [
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    ORE.COPPER,    _, _],
  [_,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _],
];

const MAP_COLS = FLOOR_LAYER[0]?.length ?? 16;
const MAP_ROWS = FLOOR_LAYER.length;

// Tiles that should glow
const GLOW_ORE_TILES = [D.GOLD_PILE, D.GOLD_SMALL, D.GOLD_TINY, ORE.COPPER];
const CRYSTAL_TILES = [D.CRYSTAL_BLUE, D.CRYSTAL_BLUE_SM, D.CRYSTAL_RED, D.CRYSTAL_RED_SM];

// Helper to find positions of specific tiles in a layer
function findTilePositions(tilemap: TileMap, tileIndices: number[]): { col: number; row: number }[] {
  const positions: { col: number; row: number }[] = [];
  for (let row = 0; row < tilemap.length; row++) {
    for (let col = 0; col < (tilemap[row]?.length ?? 0); col++) {
      const tile = tilemap[row]?.[col];
      if (tile !== null && tile !== undefined && tileIndices.includes(tile)) {
        positions.push({ col, row });
      }
    }
  }
  return positions;
}

// ============================================
// COMPONENT
// ============================================

interface MineTilemapProps {
  scale?: number;
  className?: string;
  children?: React.ReactNode;
  minerPosition?: { x: number; y: number };
}

export function MineTilemap({
  scale = 3,
  className,
  children,
  minerPosition = { x: 2, y: 3 }, // Tile coordinates (center of 6x6 map)
}: MineTilemapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [imagesLoaded, setImagesLoaded] = useState(false);
  const imageRef = useRef<HTMLImageElement | null>(null);
  const trackImageRef = useRef<HTMLImageElement | null>(null);
  const oreImageRef = useRef<HTMLImageElement | null>(null);

  const tileScaled = TILE_SIZE * scale;
  const width = MAP_COLS * tileScaled;
  const height = MAP_ROWS * tileScaled;

  const renderTilemap = useCallback(() => {
    const canvas = canvasRef.current;
    const img = imageRef.current;
    const trackImg = trackImageRef.current;
    const oreImg = oreImageRef.current;
    if (!canvas || !img || !trackImg || !oreImg || !imagesLoaded) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.imageSmoothingEnabled = false;

    // Clear with dark cave background
    ctx.fillStyle = '#0d0a14';
    ctx.fillRect(0, 0, width, height);

    // Draw floor layer first
    for (let row = 0; row < MAP_ROWS; row++) {
      for (let col = 0; col < MAP_COLS; col++) {
        const tileIndex = FLOOR_LAYER[row]?.[col];

        if (tileIndex !== null && tileIndex !== undefined) {
          const rect = getTileRect(tileIndex);
          ctx.drawImage(
            img,
            rect.x, rect.y, rect.w, rect.h,
            col * tileScaled, row * tileScaled,
            tileScaled, tileScaled
          );
        }
      }
    }

    // Draw track layer (mine cart rails)
    for (let row = 0; row < MAP_ROWS; row++) {
      for (let col = 0; col < MAP_COLS; col++) {
        const tileIndex = TRACK_LAYER[row]?.[col];

        if (tileIndex !== null && tileIndex !== undefined) {
          const rect = getCartTileRect(tileIndex);
          ctx.drawImage(
            trackImg,
            rect.x, rect.y, rect.w, rect.h,
            col * tileScaled, row * tileScaled,
            tileScaled, tileScaled
          );
        }
      }
    }

    // Draw decoration layer on top
    for (let row = 0; row < MAP_ROWS; row++) {
      for (let col = 0; col < MAP_COLS; col++) {
        const tileIndex = DECOR_LAYER[row]?.[col];

        if (tileIndex !== null && tileIndex !== undefined) {
          const rect = getTileRect(tileIndex);
          ctx.drawImage(
            img,
            rect.x, rect.y, rect.w, rect.h,
            col * tileScaled, row * tileScaled,
            tileScaled, tileScaled
          );
        }
      }
    }

    // Draw ore layer (from separate sprite sheet)
    for (let row = 0; row < MAP_ROWS; row++) {
      for (let col = 0; col < MAP_COLS; col++) {
        const tileIndex = ORE_LAYER[row]?.[col];

        if (tileIndex !== null && tileIndex !== undefined) {
          const rect = getOreRect(tileIndex);
          ctx.drawImage(
            oreImg,
            rect.x, rect.y, rect.w, rect.h,
            col * tileScaled, row * tileScaled,
            tileScaled, tileScaled
          );
        }
      }
    }

    // Add glow effects for ore (orange/copper glow)
    const orePositions = [
      ...findTilePositions(DECOR_LAYER, GLOW_ORE_TILES),
      ...findTilePositions(ORE_LAYER, GLOW_ORE_TILES),
    ];
    orePositions.forEach(({ col, row }) => {
      const gradient = ctx.createRadialGradient(
        (col + 0.5) * tileScaled, (row + 0.5) * tileScaled, 0,
        (col + 0.5) * tileScaled, (row + 0.5) * tileScaled, tileScaled * 1.5
      );
      gradient.addColorStop(0, 'rgba(255, 180, 50, 0.25)');
      gradient.addColorStop(0.5, 'rgba(255, 140, 30, 0.1)');
      gradient.addColorStop(1, 'rgba(255, 100, 0, 0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(
        (col - 1) * tileScaled, (row - 1) * tileScaled,
        tileScaled * 3, tileScaled * 3
      );
    });

    // Add glow effects for crystals (blue glow)
    const crystalPositions = findTilePositions(DECOR_LAYER, CRYSTAL_TILES);
    crystalPositions.forEach(({ col, row }) => {
      const gradient = ctx.createRadialGradient(
        (col + 0.5) * tileScaled, (row + 0.5) * tileScaled, 0,
        (col + 0.5) * tileScaled, (row + 0.5) * tileScaled, tileScaled * 1.2
      );
      gradient.addColorStop(0, 'rgba(100, 150, 255, 0.25)');
      gradient.addColorStop(0.5, 'rgba(80, 120, 255, 0.1)');
      gradient.addColorStop(1, 'rgba(60, 100, 255, 0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(
        (col - 1) * tileScaled, (row - 1) * tileScaled,
        tileScaled * 3, tileScaled * 3
      );
    });

  }, [imagesLoaded, width, height, tileScaled]);

  // Load sprite sheets
  useEffect(() => {
    let loadedCount = 0;
    const totalImages = 3;

    const checkAllLoaded = () => {
      loadedCount++;
      if (loadedCount === totalImages) {
        setImagesLoaded(true);
      }
    };

    // Load floor tiles
    const img = new Image();
    img.onload = checkAllLoaded;
    img.src = '/sprites/walls_and_floors/walls_floors.png';
    imageRef.current = img;

    // Load track tiles
    const trackImg = new Image();
    trackImg.onload = checkAllLoaded;
    trackImg.src = '/sprites/decorations/mine_carts/mine_carts.png';
    trackImageRef.current = trackImg;

    // Load ore tiles
    const oreImg = new Image();
    oreImg.onload = checkAllLoaded;
    oreImg.src = ORE_SPRITE_SRC;
    oreImageRef.current = oreImg;

    return () => {
      img.onload = null;
      trackImg.onload = null;
      oreImg.onload = null;
    };
  }, []);

  // Render when loaded
  useEffect(() => {
    if (imagesLoaded) {
      renderTilemap();
    }
  }, [imagesLoaded, renderTilemap]);

  return (
    <div className={cn('relative', className)} style={{ width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="absolute inset-0"
        style={{ imageRendering: 'pixelated' }}
      />
      {/* Miner overlay */}
      {children && (
        <div
          className="absolute"
          style={{
            left: minerPosition.x * tileScaled,
            top: minerPosition.y * tileScaled - tileScaled,
            zIndex: 10,
          }}
        >
          {children}
        </div>
      )}
    </div>
  );
}

