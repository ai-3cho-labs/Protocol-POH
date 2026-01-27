/**
 * Share Card Generator
 * Creates a branded PNG image of user mining stats using Canvas API.
 */

import type { UserMiningStats } from '@/types/models';
import { formatCompactNumber, formatGOLD, formatMultiplier, shortenAddress } from './utils';

// Card dimensions (optimized for social sharing)
const CARD_WIDTH = 800;
const CARD_HEIGHT = 400;

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
 * Format date as "Jan 2024" or "Jan 15, 2024"
 */
function formatMiningDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    year: 'numeric',
  });
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
  const headerY = 40;

  // CPU Logo/Brand
  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 32px Inter, system-ui, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('CPU', 40, headerY + 8);

  // Tagline
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 14px Inter, system-ui, sans-serif';
  ctx.fillText('Mining Stats', 110, headerY + 6);

  // User wallet address
  ctx.fillStyle = COLORS.amber;
  ctx.font = '600 14px Inter, system-ui, sans-serif';
  ctx.textAlign = 'right';
  ctx.fillText(shortenAddress(stats.wallet, 4), CARD_WIDTH - 40, headerY + 6);

  // === MAIN CONTENT AREA ===
  const contentY = 70;
  const contentHeight = 270;

  // Left section - Tier & Balance
  const leftWidth = 260;
  const leftX = 40;

  // Tier card background
  roundRect(ctx, leftX, contentY, leftWidth, contentHeight, 16);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  // Tier label
  ctx.textAlign = 'center';
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('TIER', leftX + leftWidth / 2, contentY + 35);

  // Tier name
  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 32px Inter, system-ui, sans-serif';
  ctx.fillText(stats.tier.name, leftX + leftWidth / 2, contentY + 75);

  // Multiplier badge
  const multBadgeWidth = 80;
  const multBadgeHeight = 30;
  const multBadgeX = leftX + (leftWidth - multBadgeWidth) / 2;
  const multBadgeY = contentY + 90;

  roundRect(ctx, multBadgeX, multBadgeY, multBadgeWidth, multBadgeHeight, 15);
  ctx.fillStyle = 'rgba(245, 158, 11, 0.12)';
  ctx.fill();
  ctx.strokeStyle = 'rgba(245, 158, 11, 0.25)';
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = COLORS.amber;
  ctx.font = 'bold 15px Inter, system-ui, sans-serif';
  ctx.fillText(formatMultiplier(stats.multiplier), leftX + leftWidth / 2, multBadgeY + 20);

  // Streak info
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 12px Inter, system-ui, sans-serif';
  const streakText = stats.streakDays >= 1
    ? `${Math.floor(stats.streakDays)}d streak`
    : `${Math.round(stats.streakHours)}h streak`;
  ctx.fillText(streakText, leftX + leftWidth / 2, contentY + 150);

  // Divider
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(leftX + 24, contentY + 170);
  ctx.lineTo(leftX + leftWidth - 24, contentY + 170);
  ctx.stroke();

  // Balance
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('BALANCE', leftX + leftWidth / 2, contentY + 200);

  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 28px Inter, system-ui, sans-serif';
  ctx.fillText(formatCompactNumber(stats.balance), leftX + leftWidth / 2, contentY + 235);

  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 13px Inter, system-ui, sans-serif';
  ctx.fillText('CPU', leftX + leftWidth / 2, contentY + 255);

  // Mining since (OG flex)
  if (stats.streakStart) {
    ctx.fillStyle = COLORS.gray600;
    ctx.font = '500 11px Inter, system-ui, sans-serif';
    ctx.fillText(`Mining since ${formatMiningDate(stats.streakStart)}`, leftX + leftWidth / 2, contentY + 285);
  }

  // === RIGHT SECTION - Stats ===
  const rightX = leftX + leftWidth + 20;
  const rightWidth = CARD_WIDTH - rightX - 40;

  // Hash Power card
  const hashCardHeight = 115;
  roundRect(ctx, rightX, contentY, rightWidth, hashCardHeight, 16);
  ctx.fillStyle = 'rgba(245, 158, 11, 0.06)';
  ctx.fill();
  ctx.strokeStyle = 'rgba(245, 158, 11, 0.15)';
  ctx.lineWidth = 1;
  ctx.stroke();

  // Hash Power label
  ctx.textAlign = 'left';
  ctx.fillStyle = COLORS.amberMuted;
  ctx.font = '600 11px Inter, system-ui, sans-serif';
  ctx.fillText('HASH POWER', rightX + 20, contentY + 30);

  // Hash Power value
  const hashValueStr = formatCompactNumber(stats.hashPower);
  ctx.font = 'bold 44px Inter, system-ui, sans-serif';
  const hashWidth = ctx.measureText(hashValueStr).width;

  ctx.fillStyle = COLORS.amber;
  ctx.fillText(hashValueStr, rightX + 20, contentY + 75);

  // H/s unit
  ctx.fillStyle = COLORS.amberMuted;
  ctx.font = '600 16px Inter, system-ui, sans-serif';
  ctx.fillText('H/s', rightX + 20 + hashWidth + 10, contentY + 75);

  // TWAB breakdown
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 11px Inter, system-ui, sans-serif';
  ctx.fillText(
    `TWAB ${formatCompactNumber(stats.twab)} × ${formatMultiplier(stats.multiplier)}`,
    rightX + 20,
    contentY + 100
  );

  // Bottom row - 3 compact cards
  const bottomRowY = contentY + hashCardHeight + 10;
  const bottomCardHeight = 72;
  const cardGap = 8;
  const bottomCardWidth = (rightWidth - cardGap * 2) / 3;

  // Card 1: Earned Rewards
  roundRect(ctx, rightX, bottomRowY, bottomCardWidth, bottomCardHeight, 10);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.textAlign = 'center';
  ctx.fillStyle = COLORS.gray500;
  ctx.font = '600 9px Inter, system-ui, sans-serif';
  ctx.fillText('EARNED', rightX + bottomCardWidth / 2, bottomRowY + 18);

  ctx.fillStyle = COLORS.amberLight;
  ctx.font = 'bold 20px Inter, system-ui, sans-serif';
  const pendingValue = stats.pendingReward >= 1
    ? `+${formatCompactNumber(Math.floor(stats.pendingReward))}`
    : `+${formatGOLD(stats.pendingReward)}`;
  ctx.fillText(pendingValue, rightX + bottomCardWidth / 2, bottomRowY + 42);

  ctx.fillStyle = COLORS.gray500;
  ctx.font = '500 10px Inter, system-ui, sans-serif';
  ctx.fillText('$GOLD', rightX + bottomCardWidth / 2, bottomRowY + 60);

  // Card 2: Rank with Percentile
  const rankCardX = rightX + bottomCardWidth + cardGap;
  roundRect(ctx, rankCardX, bottomRowY, bottomCardWidth, bottomCardHeight, 10);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  ctx.fillStyle = COLORS.gray500;
  ctx.font = '600 9px Inter, system-ui, sans-serif';
  ctx.fillText('RANK', rankCardX + bottomCardWidth / 2, bottomRowY + 18);

  ctx.fillStyle = COLORS.white;
  ctx.font = 'bold 20px Inter, system-ui, sans-serif';
  const rankDisplay = stats.rank ? `#${stats.rank}` : '-';
  ctx.fillText(rankDisplay, rankCardX + bottomCardWidth / 2, bottomRowY + 42);

  // Percentile or fallback
  if (extras?.totalHolders && stats.rank) {
    const percentile = getPercentile(stats.rank, extras.totalHolders);
    if (percentile) {
      ctx.fillStyle = COLORS.amber;
      ctx.font = '600 10px Inter, system-ui, sans-serif';
      ctx.fillText(percentile, rankCardX + bottomCardWidth / 2, bottomRowY + 60);
    } else {
      ctx.fillStyle = COLORS.gray500;
      ctx.font = '500 10px Inter, system-ui, sans-serif';
      ctx.fillText('Leaderboard', rankCardX + bottomCardWidth / 2, bottomRowY + 60);
    }
  } else {
    ctx.fillStyle = COLORS.gray500;
    ctx.font = '500 10px Inter, system-ui, sans-serif';
    ctx.fillText('Leaderboard', rankCardX + bottomCardWidth / 2, bottomRowY + 60);
  }

  // Card 3: Lifetime Earnings OR Progress
  const thirdCardX = rankCardX + bottomCardWidth + cardGap;
  roundRect(ctx, thirdCardX, bottomRowY, bottomCardWidth, bottomCardHeight, 10);
  ctx.fillStyle = COLORS.cardBg;
  ctx.fill();
  ctx.strokeStyle = COLORS.cardBorder;
  ctx.lineWidth = 1;
  ctx.stroke();

  if (extras?.lifetimeEarnings !== undefined && extras.lifetimeEarnings > 0) {
    ctx.fillStyle = COLORS.gray500;
    ctx.font = '600 9px Inter, system-ui, sans-serif';
    ctx.fillText('EARNED', thirdCardX + bottomCardWidth / 2, bottomRowY + 18);

    ctx.fillStyle = COLORS.white;
    ctx.font = 'bold 20px Inter, system-ui, sans-serif';
    ctx.fillText(formatCompactNumber(extras.lifetimeEarnings), thirdCardX + bottomCardWidth / 2, bottomRowY + 42);

    ctx.fillStyle = COLORS.gray500;
    ctx.font = '500 10px Inter, system-ui, sans-serif';
    ctx.fillText('$GOLD', thirdCardX + bottomCardWidth / 2, bottomRowY + 60);
  } else {
    ctx.fillStyle = COLORS.gray500;
    ctx.font = '600 9px Inter, system-ui, sans-serif';
    ctx.fillText('PROGRESS', thirdCardX + bottomCardWidth / 2, bottomRowY + 18);

    ctx.fillStyle = COLORS.white;
    ctx.font = 'bold 20px Inter, system-ui, sans-serif';
    ctx.fillText(`${Math.round(stats.progressToNextTier)}%`, thirdCardX + bottomCardWidth / 2, bottomRowY + 42);

    ctx.fillStyle = COLORS.gray500;
    ctx.font = '500 10px Inter, system-ui, sans-serif';
    const nextTierText = stats.nextTier ? `to ${stats.nextTier.name}` : 'Max Tier';
    ctx.fillText(nextTierText, thirdCardX + bottomCardWidth / 2, bottomRowY + 60);
  }

  // === FOOTER ===
  const footerY = CARD_HEIGHT - 40;

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
