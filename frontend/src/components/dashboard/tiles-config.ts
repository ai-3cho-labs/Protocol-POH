// tiles-config.ts
// BLUE/PURPLE PALETTE - Rows 1-14
// walls_floors.png | 42 cols × 61 rows | 16px tiles

const COLS = 42;
const TILE_SIZE = 16;

export const idx = (row: number, col: number) => row * COLS + col;

export const getTileRect = (index: number) => ({
  x: (index % COLS) * TILE_SIZE,
  y: Math.floor(index / COLS) * TILE_SIZE,
  w: TILE_SIZE,
  h: TILE_SIZE,
});

// ============================================
// BLUE PALETTE TILE MAPPINGS
// ============================================

export const BLUE_TILES = {

  // ----------------------------------------
  // WALL / FLOOR EDGES
  // Creates bordered floor with depth effect
  // TL-T-TR = top edge, L-R = sides, BL-B-BR = bottom
  // IT = inner top (shadow/depth row below top edge)
  // ----------------------------------------
  WALL_FLOOR: {
    TL: 86,   // Top-left corner
    T:  255,  // Top edge
    TR: 215,  // Top-right corner
    L:  132,  // Left wall
    IT: 297,  // Inner top edge (depth/shadow)
    R:  127,  // Right wall
    BL: 213,  // Bottom-left corner
    B:  45,   // Bottom edge
    BR: 215,  // Bottom-right corner
  },

  // ----------------------------------------
  // FLAT WALKABLE FLOOR
  // Simple ground tiles - no depth edge
  // ----------------------------------------
  FLOOR: {
    MAIN: 59,     // idx(1, 17) ← User confirmed
    ALT1: 60,     // idx(1, 18)
    ALT2: 101,    // idx(2, 17)
    ALT3: 102,    // idx(2, 18)
  },

  // ----------------------------------------
  // CROSS CONNECTOR (4-way intersection)
  // Cols 7-9, Rows 1-3
  // ----------------------------------------
  CROSS: {
    T:  50,   // idx(1, 8)
    L:  91,   // idx(2, 7)
    C:  92,   // idx(2, 8)
    R:  93,   // idx(2, 9)
    B:  134,  // idx(3, 8)
  },

  // ----------------------------------------
  // SMALL FLOOR PIECES
  // Row 4
  // ----------------------------------------
  FLOOR_SMALL: {
    A: 170,   // idx(4, 2)
    B: 171,   // idx(4, 3)
  },

  // ----------------------------------------
  // PIT / HOLE (3×3)
  // Dark pit showing depth DOWN
  // Cols 13-15, Rows 5-7
  // ----------------------------------------
  PIT: {
    TL: 137,  // idx(5, 13)
    T:  138,  // idx(5, 14)
    TR: 141,  // idx(5, 15)
    L:  263,  // idx(6, 13)
    C:  266,  // idx(6, 14) - Deep center
    R:  267,  // idx(6, 15)
    BL: 305,  // idx(7, 13)
    B:  308,  // idx(7, 14)
    BR: 309,  // idx(7, 15)
  },

  // ----------------------------------------
  // LARGE POOL / WATER (circular)
  // Cols 26-30, Rows 1-5
  // ----------------------------------------
  POOL: {
    TL: 68,   // idx(1, 26)
    T:  69,   // idx(1, 27)
    TR: 72,   // idx(1, 30)
    L:  110,  // idx(2, 26)
    C:  111,  // idx(2, 27) - Water center
    R:  114,  // idx(2, 30)
    BL: 236,  // idx(5, 26)
    B:  237,  // idx(5, 27)
    BR: 240,  // idx(5, 30)
  },

  // ----------------------------------------
  // SCATTERED DEBRIS / TRANSITION
  // Small detail pieces
  // ----------------------------------------
  DEBRIS: {
    A: 55,    // idx(1, 13)
    B: 56,    // idx(1, 14)
    C: 97,    // idx(2, 13)
    D: 98,    // idx(2, 14)
  },

  WALLSHADOW: {
    A: 339,
  },
  // ----------------------------------------
  // DECORATIONS (Column 37-38)
  // Props that sit ON floors
  // ----------------------------------------
  DECOR: {
    ROCKS_LARGE:     76,   // Gray rocks
    ROCKS_SMALL:     121,  // idx(2, 37)
    PEBBLES:         122,  // idx(2, 38)

    BUSH:            163,  // idx(3, 37) - Green moss/plant

    CRYSTAL_BLUE:    331,  // idx(4, 37) - Blue crystal
    CRYSTAL_BLUE_SM: 332,  // idx(5, 37)

    CRYSTAL_RED:     457,  // idx(6, 37) - Red crystal
    CRYSTAL_RED_SM:  458,  // idx(7, 37)

    GOLD_PILE:       583,  // idx(8, 37) - ★ COPPER ORE
    GOLD_SMALL:      584,  // idx(8, 38)
    GOLD_TINY:       416,  // idx(9, 38)

    ROCKS_ALT:       457,  // idx(10, 37)
    PEBBLES_ALT:     499,  // idx(11, 37)
  },
};

// ============================================
// QUICK ACCESS
// ============================================

export const QUICK = {
  // Floors
  FLOOR: BLUE_TILES.FLOOR.MAIN,           // 59 - Flat walkable

  // Wall edges
  WALL_TL: BLUE_TILES.WALL_FLOOR.TL,      // 86
  WALL_T:  BLUE_TILES.WALL_FLOOR.T,       // 255
  WALL_TR: BLUE_TILES.WALL_FLOOR.TR,      // 215
  WALL_L:  BLUE_TILES.WALL_FLOOR.L,       // 132
  WALL_IT: BLUE_TILES.WALL_FLOOR.IT,      // 297 - Inner top (depth)
  WALL_R:  BLUE_TILES.WALL_FLOOR.R,       // 127
  WALL_BL: BLUE_TILES.WALL_FLOOR.BL,      // 213
  WALL_B:  BLUE_TILES.WALL_FLOOR.B,       // 45
  WALL_BR: BLUE_TILES.WALL_FLOOR.BR,      // 215

  // Features
  PIT: BLUE_TILES.PIT.C,                  // 266
  POOL: BLUE_TILES.POOL.C,                // 111

  // Decorations
  COPPER_ORE: BLUE_TILES.DECOR.GOLD_PILE, // 373 ★
  ROCKS: BLUE_TILES.DECOR.ROCKS_LARGE,    // 79
  CRYSTAL: BLUE_TILES.DECOR.CRYSTAL_BLUE, // 205
};

// ============================================
// MINE CART TRACKS
// mine_carts.png | 16 cols × 11 rows | 16px tiles
// ============================================

const CART_COLS = 16;

export const cartIdx = (row: number, col: number) => row * CART_COLS + col;

export const getCartTileRect = (index: number) => ({
  x: (index % CART_COLS) * TILE_SIZE,
  y: Math.floor(index / CART_COLS) * TILE_SIZE,
  w: TILE_SIZE,
  h: TILE_SIZE,
});

export const CART_TILES = {
  // ----------------------------------------
  // LARGE LOOP (4×4) - Top left
  // Rows 0-3, Cols 0-3
  // ----------------------------------------
  LOOP: {
    TL: 0,    // cartIdx(0, 0)
    T1: 1,    // cartIdx(0, 1)
    T2: 2,    // cartIdx(0, 2)
    TR: 3,    // cartIdx(0, 3)
    L1: 16,   // cartIdx(1, 0)
    L2: 32,   // cartIdx(2, 0)
    R1: 19,   // cartIdx(1, 3)
    R2: 35,   // cartIdx(2, 3)
    BL: 48,   // cartIdx(3, 0)
    B1: 49,   // cartIdx(3, 1)
    B2: 50,   // cartIdx(3, 2)
    BR: 51,   // cartIdx(3, 3)
  },

  // ----------------------------------------
  // STRAIGHT TRACKS
  // ----------------------------------------
  STRAIGHT: {
    H: 81,    // Horizontal rail - cartIdx(5, 1)
    V: 64,    // Vertical rail - cartIdx(4, 0)
  },

  // ----------------------------------------
  // CORNERS (small 1×1)
  // ----------------------------------------
  CORNER: {
    TL: 96,   // cartIdx(6, 0) - curves from top to left
    TR: 97,   // cartIdx(6, 1) - curves from top to right
    BL: 112,  // cartIdx(7, 0) - curves from bottom to left
    BR: 113,  // cartIdx(7, 1) - curves from bottom to right
  },

  // ----------------------------------------
  // INTERSECTION / CROSS
  // Cols 4-5, Rows 0-1
  // ----------------------------------------
  CROSS: {
    TL: 4,    // cartIdx(0, 4)
    TR: 5,    // cartIdx(0, 5)
    BL: 20,   // cartIdx(1, 4)
    BR: 21,   // cartIdx(1, 5)
  },

  // ----------------------------------------
  // T-JUNCTIONS
  // ----------------------------------------
  T_JUNCTION: {
    UP: 98,    // cartIdx(6, 2) - T pointing up
    DOWN: 114, // cartIdx(7, 2) - T pointing down
    LEFT: 99,  // cartIdx(6, 3) - T pointing left
    RIGHT: 115,// cartIdx(7, 3) - T pointing right
  },

  // ----------------------------------------
  // TRACK ENDS / BUMPERS
  // ----------------------------------------
  END: {
    TOP: 80,    // cartIdx(5, 0)
    BOTTOM: 82, // cartIdx(5, 2)
    LEFT: 83,   // cartIdx(5, 3)
    RIGHT: 84,  // cartIdx(5, 4)
  },

  // ----------------------------------------
  // MINE CARTS
  // ----------------------------------------
  CART: {
    EMPTY: 69,      // cartIdx(4, 5) - Empty cart
    ORE: 70,        // cartIdx(4, 6) - Cart with ore
    GOLD: 71,       // cartIdx(4, 7) - Cart with gold
    FULL: 85,       // cartIdx(5, 5) - Full cart
  },

  // ----------------------------------------
  // DECORATIVE TRACK PIECES
  // ----------------------------------------
  DECOR: {
    RAIL_BROKEN: 86,   // cartIdx(5, 6)
    WHEEL: 87,         // cartIdx(5, 7)
    CONNECTOR: 88,     // cartIdx(5, 8)
  },
};

// ============================================
// TILEMAP TYPES
// ============================================

export type TileMap = (number | null)[][];

export const createEmptyMap = (width: number, height: number): TileMap =>
  Array(height).fill(null).map(() => Array(width).fill(null));

// ============================================
// MINING ORES (separate sprite sheet)
// mining_ores.png | 18 cols × 9 rows | 16px tiles
// ============================================

const ORE_COLS = 18;

export const oreIdx = (row: number, col: number) => row * ORE_COLS + col;

export const getOreRect = (index: number) => ({
  x: (index % ORE_COLS) * TILE_SIZE,
  y: Math.floor(index / ORE_COLS) * TILE_SIZE,
  w: TILE_SIZE,
  h: TILE_SIZE,
});

export const ORE_TILES = {
  // 8th column, 3rd row (copper ore)
  COPPER: oreIdx(2, 7),      // Row 2 (0-indexed), Col 7 (0-indexed) = 8th col, 3rd row
  COPPER_SMALL: oreIdx(3, 7),
};
