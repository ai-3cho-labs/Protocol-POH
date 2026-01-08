# Sprite Animation System

Documentation for the pixel miner sprite animation in the dashboard.

## Sprite Sheet Structure

The miner uses layered sprite sheets located in `/public/sprites/character/tools_drill/`:

| Layer | File | Purpose |
|-------|------|---------|
| 1 | `character_body/character_tools_drill_body_light.png` | Base body |
| 2 | `clothes/full_body/overhalls/character_tools_drill_clothes_fullbody_overhalls_blue.png` | Clothing |
| 3 | `hairstyles/radical_curve/character_tools_drill_hairstyles_radical_curve_brown_dark.png` | Hair |

All three layers are composited together on a single canvas.

## Frame Dimensions

**Critical:** Frame dimensions must match the actual sprite sheet.

To calculate frame size:
```
Frame Width  = Sprite Sheet Width  ÷ Number of Columns
Frame Height = Sprite Sheet Height ÷ Number of Rows
```

Current sprite sheets are **192×256 pixels** with a **3×4 grid**:
- Frame Width: 192 ÷ 3 = **64px**
- Frame Height: 256 ÷ 4 = **64px**

```typescript
// PixelMiner.tsx
const FRAME_WIDTH = 64;
const FRAME_HEIGHT = 64;
const COLUMNS = 3;
```

**Warning:** Incorrect frame dimensions will cause the character to "slide" during animation because the wrong portion of each frame is extracted.

## Animation Rows

The sprite sheet contains 4 animation states (one per row):

| Row | Animation | Description |
|-----|-----------|-------------|
| 0 | `drilling` | Drilling forward (default) |
| 1 | `drillingAlt` | Drilling from alternate angle |
| 2 | `drillingDown` | Drilling downward |
| 3 | `idle` | Idle stance with drill |

Each row has 3 frames that cycle for the animation.

## Component Usage

```tsx
import { PixelMiner } from './PixelMiner';

<PixelMiner
  scale={1.5}           // Size multiplier (default: 2)
  animation="drilling"  // Animation state (default: "drilling")
  frameTime={150}       // Ms per frame (default: 150, ~7 FPS)
  flipX={false}         // Mirror horizontally (default: false)
/>
```

## Frame Offsets

If sprites have inconsistent character positioning between frames (causing sliding), use `FRAME_OFFSETS` to compensate:

```typescript
const FRAME_OFFSETS: Record<AnimationState, number[]> = {
  drilling:     [0, 0, 0],  // [frame0, frame1, frame2] pixel offsets
  drillingAlt:  [0, 0, 0],
  drillingDown: [0, 0, 0],
  idle:         [0, 0, 0],
};
```

Negative values shift left, positive values shift right.

## Integration with Tilemap

The `MineTilemap` component positions the miner using tile coordinates:

```tsx
<MineTilemap scale={1.5} minerPosition={{ x: 2, y: 3 }}>
  <PixelMiner scale={1.5} animation="drilling" />
</MineTilemap>
```

- Tilemap uses 16px base tiles
- Scale multiplies both tile size and sprite size
- `minerPosition` is in tile coordinates, not pixels

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Character slides | Wrong `FRAME_WIDTH`/`FRAME_HEIGHT` | Check sprite sheet dimensions and recalculate |
| Animation too fast/slow | `frameTime` value | Adjust ms per frame (higher = slower) |
| Sprite blurry | Image smoothing | Ensure `imageSmoothingEnabled = false` and CSS `image-rendering: pixelated` |
| Layers misaligned | Different sprite sheet sizes | All layers must have identical dimensions |
