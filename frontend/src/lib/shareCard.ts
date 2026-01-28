/**
 * Share Card Generator
 * Creates a branded PNG image of user mining stats using Canvas API.
 * Matches the modal preview design.
 */

import type { UserMiningStats } from '@/types/models';
import { branding } from '@/config';
import { formatCompactNumber, shortenAddress } from './utils';

// Card dimensions (optimized for social sharing)
const CARD_WIDTH = 400;
const CARD_HEIGHT = 280;
const PADDING = 32;
const BORDER_RADIUS = 16;

/** Additional data for richer share cards */
export interface ShareCardExtras {
  /** Total number of holders (for percentile calculation) */
  totalHolders?: number;
  /** Lifetime earnings in $GOLD */
  lifetimeEarnings?: number;
  /** Lifetime earnings in USD */
  lifetimeEarningsUsd?: number;
  /** Pending reward in USD */
  pendingRewardUsd?: number;
}

/**
 * Draw a rounded rectangle path
 */
function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
}

/**
 * Draw a pickaxe icon (Lucide Pickaxe using actual SVG paths)
 */
function drawPickaxe(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  color: string,
  fill = false
) {
  ctx.save();
  ctx.translate(x, y);

  const scale = size / 24; // Lucide icons are 24x24
  ctx.scale(scale, scale);

  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  // Path 1: Handle
  const p1 = new Path2D('m14 13-8.381 8.38a1 1 0 0 1-3.001-3L11 9.999');
  // Path 2: Left curve
  const p2 = new Path2D('M15.973 4.027A13 13 0 0 0 5.902 2.373c-1.398.342-1.092 2.158.277 2.601a19.9 19.9 0 0 1 5.822 3.024');
  // Path 3: Right curve
  const p3 = new Path2D('M16.001 11.999a19.9 19.9 0 0 1 3.024 5.824c.444 1.369 2.26 1.676 2.603.278A13 13 0 0 0 20 8.069');
  // Path 4: Head rectangle
  const p4 = new Path2D('M18.352 3.352a1.205 1.205 0 0 0-1.704 0l-5.296 5.296a1.205 1.205 0 0 0 0 1.704l2.296 2.296a1.205 1.205 0 0 0 1.704 0l5.296-5.296a1.205 1.205 0 0 0 0-1.704z');

  if (fill) {
    ctx.fill(p1);
    ctx.fill(p2);
    ctx.fill(p3);
    ctx.fill(p4);
  }
  ctx.stroke(p1);
  ctx.stroke(p2);
  ctx.stroke(p3);
  ctx.stroke(p4);

  ctx.restore();
}

/**
 * Format USD value
 */
function formatUSD(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Generate a share card image from user stats
 * Matches the modal preview design
 */
export async function generateShareCard(
  stats: UserMiningStats,
  extras?: ShareCardExtras
): Promise<Blob> {
  const canvas = document.createElement('canvas');
  canvas.width = CARD_WIDTH;
  canvas.height = CARD_HEIGHT;
  const ctx = canvas.getContext('2d')!;

  // === BLACK BACKGROUND WITH ROUNDED CORNERS ===
  ctx.fillStyle = '#000000';
  roundRect(ctx, 0, 0, CARD_WIDTH, CARD_HEIGHT, BORDER_RADIUS);
  ctx.fill();

  // === DECORATIVE PICKAXE (top right, faded) ===
  drawPickaxe(ctx, CARD_WIDTH - 140, 20, 120, 'rgba(255, 255, 255, 0.08)');

  // === HEADER: Logo + "PROTOCOL TERMINAL" ===
  const headerY = PADDING + 8;

  // Small white box with pickaxe icon
  ctx.fillStyle = '#ffffff';
  roundRect(ctx, PADDING, PADDING, 28, 28, 6);
  ctx.fill();
  drawPickaxe(ctx, PADDING + 4, PADDING + 4, 20, '#000000');

  // "PROTOCOL TERMINAL" text
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 14px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('PROTOCOL TERMINAL', PADDING + 40, headerY + 10);

  // === MAIN CONTENT: "TOTAL CLAIMED" + USD VALUE ===
  const mainY = 90;

  // Label
  ctx.fillStyle = '#9ca3af'; // gray-400
  ctx.font = 'bold 11px Inter, system-ui, sans-serif';
  ctx.fillText('TOTAL CLAIMED', PADDING, mainY);

  // USD Value (gold gradient effect - simulate with solid gold)
  const totalUsd = extras?.lifetimeEarningsUsd ?? 0;
  ctx.fillStyle = '#fbbf24'; // yellow-400/gold
  ctx.font = 'bold 48px Inter, system-ui, sans-serif';
  ctx.fillText(formatUSD(totalUsd), PADDING, mainY + 55);

  // === FOOTER: Miner + Holdings ===
  const footerY = CARD_HEIGHT - 70;

  // Divider line
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(PADDING, footerY);
  ctx.lineTo(CARD_WIDTH - PADDING, footerY);
  ctx.stroke();

  // Two columns
  const col1X = PADDING;
  const col2X = CARD_WIDTH / 2 + 10;
  const labelY = footerY + 24;
  const valueY = footerY + 44;

  // Column 1: Miner
  ctx.fillStyle = '#6b7280'; // gray-500
  ctx.font = 'bold 10px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('MINER', col1X, labelY);

  ctx.fillStyle = '#ffffff';
  ctx.font = '500 14px monospace';
  ctx.fillText(shortenAddress(stats.wallet, 4), col1X, valueY);

  // Column 2: Holdings
  ctx.fillStyle = '#6b7280';
  ctx.font = 'bold 10px Inter, system-ui, sans-serif';
  ctx.fillText('HOLDINGS', col2X, labelY);

  ctx.fillStyle = '#ffffff';
  ctx.font = '500 14px monospace';
  const holdingsText = `${formatCompactNumber(stats.balance)} ${branding.holdToken.symbol}`;
  ctx.fillText(holdingsText, col2X, valueY);

  // Convert to blob
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error('Failed to create image blob'));
        }
      },
      'image/png',
      1.0
    );
  });
}

/**
 * Download a blob as a file
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Share using Web Share API (mobile) or download (desktop)
 */
export async function shareOrDownload(blob: Blob): Promise<void> {
  const filename = `${branding.holdToken.symbol.toLowerCase()}-stats-${Date.now()}.png`;

  const nav = typeof window !== 'undefined' ? window.navigator : null;
  if (nav && typeof nav.share === 'function' && typeof nav.canShare === 'function') {
    try {
      const file = new File([blob], filename, { type: 'image/png' });
      const shareData = { files: [file] };

      if (nav.canShare(shareData)) {
        await nav.share(shareData);
        return;
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }
    }
  }

  downloadBlob(blob, filename);
}
