// tilemap-16x16.ts
// Saved 16x16 tilemap configuration

import { BLUE_TILES, CART_TILES, type TileMap } from './tiles-config';

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

const _ = null;

// Base layer: walls and floor (16x16)
export const FLOOR_LAYER_16x16: TileMap = [
  // Row 0: Top wall edge
  [W.TL, W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.T,  W.TR],
  // Row 1: Inner top edge (depth/shadow)
  [W.L,  W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.IT, W.R],
  // Row 2-14: Floor with walls
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  [W.L,  F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    F,    W.R],
  // Row 15: Bottom wall edge
  [W.BL, W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.B,  W.BR],
];

// Decoration layer (16x16)
export const DECOR_LAYER_16x16: TileMap = [
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, WALLSHADOW.A, _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    P.TL, P.T,  P.TR, _,    _,    _,    _,    _,    _,    D.CRYSTAL_BLUE, _, _, _],
  [_,    _,    _,    P.L,  P.C,  P.R,  _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    P.BL, P.B,  P.BR, _,    _,    _,    _,    _,    _,    _,    _,    D.GOLD_PILE, _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    D.GOLD_PILE, _, _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    D.PEBBLES, _, _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    D.ROCKS_SMALL, _, _,    _,    _],
  [_,    _,    D.CRYSTAL_BLUE_SM, _, _, _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    D.PEBBLES, _, _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    D.ROCKS_SMALL, _, _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
];

// Track layer (16x16)
export const TRACK_LAYER_16x16: TileMap = [
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,  TE.LEFT, T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H,  T.H, TE.RIGHT, _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
  [_,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _,    _],
];
