/**
 * Share Card Generator
 * Creates a branded PNG image of user mining stats using Canvas API.
 */

import type { UserMiningStats } from '@/types/models';
import { formatCompactNumber, formatGOLD, shortenAddress } from './utils';

// Card dimensions (optimized for social sharing)
const CARD_WIDTH = 800;
const CARD_HEIGHT = 280;

// Colors matching the app theme
const COLORS = {
  background: '#0a0a0a',
  cardBg: 'rgba(255, 255, 255, 0.04)',
  cardBorder: 'rgba(255, 255, 255, 0.08)',
  amber: '#f59e0b',
  amberLight: '#fbbf24',
  amberMuted: 'rgba(245, 158, 11, 0.7)',
  white: '#ffffff',
  gray300: '#d4d4d4',
  gray400: '#a3a3a3',
  gray500: '#737373',
  gray600: '#525252',
};

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
 * Calculate percentile from rank and total
 */
function getPercentile(rank: number, total: number): string {
  if (total <= 0 || rank <= 0) return '';
  const percentile = (rank / total) * 100;
  if (percentile <= 1) return 'Top 1%';
  if (percentile <= 5) return 'Top 5%';
  if (percentile <= 10) return 'Top 10%';
  if (percentile <= 25) return 'Top 25%';
  if (percentile <= 50) return 'Top 50%';
  return '';
}

/**
 * Draw decorative grid pattern (subtle)
 */
function drawGridPattern(ctx: CanvasRenderingContext2D) {
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.015)';
  ctx.lineWidth = 1;

  const gridSize = 40;

  for (let x = gridSize; x < CARD_WIDTH; x += gridSize) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, CARD_HEIGHT);
    ctx.stroke();
  }

  for (let y = gridSize; y < CARD_HEIGHT; y += gridSize) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(CARD_WIDTH, y);
    ctx.stroke();
  }
}

/**
 * Generate a share card image from user stats
 */
export async function generateShareCard(
  stats: UserMiningStats,
  extras?: ShareCardExtras
): Promise<Blob> {
  const canvas = document.createElement('canvas');
  canvas.width = CARD_WIDTH;
  canvas.height = CARD_HEIGHT;
  const ctx = canvas.getContext('2d')!;

  // === BACKGROUND ===
  ctx.fillStyle = COLORS.background;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // Subtle gradient
  const bgGradient = ctx.createLinearGradient(0, 0, CARD_WIDTH, CARD_HEIGHT);
  bgGradient.addColorStop(0, 'rgba(245, 158, 11, 0.02)');
  bgGradient.addColorStop(1, 'transparent');
  ctx.fillStyle = bgGradient;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // Grid pattern
  drawGridPattern(ctx);

  // === HEADER ===
  const headerY = 36;

  // CPU Logo/Brand
  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 28px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('CPU', 40, headerY + 6);

  // Tagline
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 13px Inter, system-ui, sans-serif';
  ctx.fillText('Mining Stats', 100, headerY + 4);

  // User wallet address
  ctx.fillStyle = COLORS.amber;
  ctx.font = '600 13px Inter, system-ui, sans-serif';
  ctx.textAlign = 'right';
  ctx.fillText(shortenAddress(stats.wallet, 4), CARD_WIDTH - 40, headerY + 4);

  // === MAIN CONTENT - 3 Stat Cards ===
  const cardY = 70;
  const cardHeight = 130;
  const cardGap = 16;
  const totalWidth = CARD_WIDTH - 80; // 40px padding each side
  const cardWidth = (totalWidth - cardGap * 2) / 3;
  const startX = 40;

  // Card 1: Pending Rewards (amber glow)
  roundRect(ctx, startX, cardY, cardWidth, cardHeight, 16);
  ctx.fillStyle = 'rgba(245, 158, 11, 0.08)';
  ctx.fill();
  ctx.strokeStyle = 'rgba(245, 158, 11, 0.2)';
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.textAlign = 'center';
  ctx.fillStyle = COLORS.gray400;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('PENDING REWARDS', startX + cardWidth / 2, cardY + 28);

  ctx.fillStyle = COLORS.amberLight;
  ctx.font = 'bold 32px Inter, system-ui, sans-serif';
  const pendingValue = stats.pendingReward >= 1
    ? `+${formatCompactNumber(Math.floor(stats.pendingReward))}`
    : `+${formatGOLD(stats.pendingReward)}`;
  ctx.fillText(pendingValue, startX + cardWidth / 2, cardY + 70);

  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 13px Inter, system-ui, sans-serif';
  ctx.fillText('$GOLD', startX + cardWidth / 2, cardY + 92);

  ctx.fillStyle = COLORS.gray400;
  ctx.font = '600 14px Inter, system-ui, sans-serif';
  const pendingUsdText = extras?.pendingRewardUsd !== undefined
    ? `$${extras.pendingRewardUsd.toFixed(2)}`
    : '$0.00';
  ctx.fillText(pendingUsdText, startX + cardWidth / 2, cardY + 114);

  // Card 2: Rank
  const rankCardX = startX + cardWidth + cardGap;
  roundRect(ctx, rankCardX, cardY, cardWidth, cardHeight, 16);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = COLORS.gray400;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('RANK', rankCardX + cardWidth / 2, cardY + 28);

  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 32px Inter, system-ui, sans-serif';
  const rankDisplay = stats.rank ? `#${stats.rank}` : '-';
  ctx.fillText(rankDisplay, rankCardX + cardWidth / 2, cardY + 70);

  // Percentile badge
  if (extras?.totalHolders && stats.rank) {
    const percentile = getPercentile(stats.rank, extras.totalHolders);
    if (percentile) {
      ctx.fillStyle = COLORS.amber;
      ctx.font = '600 14px Inter, system-ui, sans-serif';
      ctx.fillText(percentile, rankCardX + cardWidth / 2, cardY + 100);
    } else {
      ctx.fillStyle = COLORS.gray500;
      ctx.font = '500 13px Inter, system-ui, sans-serif';
      ctx.fillText('Leaderboard', rankCardX + cardWidth / 2, cardY + 100);
    }
  } else {
    ctx.fillStyle = COLORS.gray500;
    ctx.font = '500 13px Inter, system-ui, sans-serif';
    ctx.fillText('Leaderboard', rankCardX + cardWidth / 2, cardY + 100);
  }

  // Card 3: Total Mined
  const thirdCardX = rankCardX + cardWidth + cardGap;
  roundRect(ctx, thirdCardX, cardY, cardWidth, cardHeight, 16);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = COLORS.gray400;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('TOTAL MINED', thirdCardX + cardWidth / 2, cardY + 28);

  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 32px Inter, system-ui, sans-serif';
  const totalMinedGold = extras?.lifetimeEarnings !== undefined && extras.lifetimeEarnings > 0
    ? formatCompactNumber(extras.lifetimeEarnings)
    : '0.00';
  ctx.fillText(totalMinedGold, thirdCardX + cardWidth / 2, cardY + 70);

  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 13px Inter, system-ui, sans-serif';
  ctx.fillText('$GOLD', thirdCardX + cardWidth / 2, cardY + 92);

  ctx.fillStyle = COLORS.gray400;
  ctx.font = '600 14px Inter, system-ui, sans-serif';
  const totalMinedUsd = extras?.lifetimeEarningsUsd !== undefined && extras.lifetimeEarningsUsd > 0
    ? `$${extras.lifetimeEarningsUsd.toFixed(2)}`
    : '$0.00';
  ctx.fillText(totalMinedUsd, thirdCardX + cardWidth / 2, cardY + 114);

  // === FOOTER ===
  const footerY = CARD_HEIGHT - 36;

  // Divider line
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(40, footerY);
  ctx.lineTo(CARD_WIDTH - 40, footerY);
  ctx.stroke();

  // Footer content
  ctx.fillStyle = COLORS.gray600;
  ctx.font = '500 12px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('https://cpu-mine.xyz/', 40, footerY + 24);

  // Timestamp
  ctx.textAlign = 'right';
  const now = new Date();
  const timestamp = now.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
  ctx.fillText(timestamp, CARD_WIDTH - 40, footerY + 24);

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
  const filename = `cpu-stats-${Date.now()}.png`;

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
