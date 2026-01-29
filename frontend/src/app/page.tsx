'use client';

import { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import {
  Pickaxe,
  ArrowRightLeft,
  Hexagon,
  Activity,
  Trophy,
  Share2,
  ChevronDown,
  Copy,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/cn';
import { useAddressContext } from '@/contexts/AddressContext';
import {
  useUserStats,
  usePoolStatus,
  useLeaderboard,
  useUserHistory,
} from '@/hooks/api';
import { useTickingCounter } from '@/hooks/useCountdown';
import {
  formatCompactNumber,
  formatGOLD,
  formatUSD,
  calculateEarningRate,
  formatEarningRate,
} from '@/lib/utils';
import { generateShareCard, downloadBlob } from '@/lib/shareCard';
import { branding } from '@/config';

// ===========================================
// SHARED UI COMPONENTS
// ===========================================

function Card({
  children,
  className = '',
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'bg-white rounded-xl border border-gray-100 shadow-sm p-6',
        className
      )}
    >
      {children}
    </div>
  );
}

function Button({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  className = '',
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  disabled?: boolean;
  className?: string;
}) {
  const baseStyle =
    'px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm';
  const variants = {
    primary: 'bg-black text-white hover:bg-gray-800 shadow-md',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
    outline:
      'border border-gray-200 text-gray-600 hover:border-black hover:text-black',
    ghost: 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(baseStyle, variants[variant], className)}
    >
      {children}
    </button>
  );
}

function Modal({
  isOpen,
  onClose,
  title,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full overflow-hidden animate-fade-slide-in">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-900 text-2xl leading-none"
          >
            &times;
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}

// ===========================================
// HERO SECTION
// ===========================================

const CONTRACT_ADDRESS = '2UGL8evhUzGkHPxkFVB1BwFocchLVmzxHGKVc6GLpump';

function HeroSection({
  addressInput,
  setAddressInput,
  onInitialize,
}: {
  addressInput: string;
  setAddressInput: (value: string) => void;
  onInitialize: (e?: React.FormEvent) => void;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopyCA = useCallback(() => {
    navigator.clipboard.writeText(CONTRACT_ADDRESS);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  return (
    <section className="relative h-screen flex flex-col justify-center items-center text-center px-4 overflow-hidden border-b border-gray-50">
      <div
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(#000 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      <div className="mb-8 p-4 bg-gray-50 rounded-2xl border border-gray-100 flex items-center justify-center animate-bounce">
        <Pickaxe className="w-10 h-10 text-black" />
      </div>

      <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-6 max-w-3xl leading-tight">
        Proof of <span className="text-gray-400">Hold</span>. <br />
        Mine the Future.
      </h1>

      <p className="text-lg sm:text-xl text-gray-400 mb-10 max-w-xl leading-relaxed">
        The first algorithmic resource protocol where{' '}
        <span className="text-black font-semibold">Holding is Mining</span>.
        Paste your address to access your terminal.
      </p>

      <div className="w-full max-w-md z-10 space-y-4">
        <form
          onSubmit={onInitialize}
          className="flex flex-col sm:flex-row gap-2 bg-white p-2 rounded-2xl border border-gray-200 shadow-sm"
        >
          <input
            type="text"
            placeholder="Paste Wallet Address..."
            className="flex-1 px-4 py-3 outline-none text-sm font-medium rounded-xl focus:bg-gray-50 transition-colors"
            value={addressInput}
            onChange={(e) => setAddressInput(e.target.value)}
          />
          <Button onClick={() => onInitialize()} className="whitespace-nowrap py-3 px-6">
            Start Mining
            <ArrowRightLeft className="w-4 h-4" />
          </Button>
        </form>
        <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">
          No wallet connection required. Read-only visualization.
        </p>

        <a
          href={branding.buyTokenUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-50 border border-gray-200 hover:border-black hover:bg-white transition-all group"
        >
          <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">CA:</span>
          <span className="font-mono text-xs text-gray-600 group-hover:text-black transition-colors">
            {CONTRACT_ADDRESS.slice(0, 6)}...{CONTRACT_ADDRESS.slice(-4)}
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleCopyCA();
            }}
            className="p-1 rounded-md hover:bg-gray-200 transition-colors"
            title="Copy contract address"
          >
            {copied ? (
              <Check className="w-3 h-3 text-emerald-500" />
            ) : (
              <Copy className="w-3 h-3 text-gray-400" />
            )}
          </button>
        </a>
      </div>

      <div className="absolute bottom-10 animate-pulse flex flex-col items-center text-gray-300">
        <span className="text-xs font-medium tracking-widest uppercase mb-2">
          Scroll to Terminal
        </span>
        <ChevronDown className="w-5 h-5" />
      </div>
    </section>
  );
}

// ===========================================
// STATS OVERVIEW
// ===========================================

function StatsOverview({
  holdings,
  miningRate,
  poolSharePercent,
  onOpenBuy,
}: {
  holdings: number;
  miningRate: number | null;
  poolSharePercent: number;
  onOpenBuy: () => void;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card className="group relative">
        <Hexagon className="absolute top-6 right-6 w-8 h-8 text-gray-50 opacity-0 group-hover:opacity-100 transition-opacity" />
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
          Protocol Holdings
        </p>
        <div className="flex items-baseline gap-2">
          <h2 className="text-4xl font-black text-gray-900">
            {formatCompactNumber(holdings)}
          </h2>
          <span className="text-xs font-bold text-gray-400">POH</span>
        </div>
        <div className="mt-6 flex gap-2">
          <Button variant="primary" className="flex-1" onClick={onOpenBuy}>
            Buy Tokens
          </Button>
          <Button variant="outline" className="px-4">
            Swap
          </Button>
        </div>
      </Card>

      <Card>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
          Mining Power
        </p>
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'w-3 h-3 rounded-full',
              holdings > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'
            )}
          />
          <h2 className="text-4xl font-black text-gray-900 uppercase">
            {holdings > 0 ? 'Active' : 'Idle'}
          </h2>
        </div>
        <p className="mt-4 text-sm text-gray-500">
          Rate:{' '}
          <span className="text-black font-bold">
            {miningRate !== null
              ? (() => {
                  const formatted = formatEarningRate(miningRate);
                  return formatted.startsWith('<') ? formatted : `~${formatted}`;
                })()
              : '$0/hr'}
          </span>
        </p>
      </Card>

      <Card>
        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
          Pool Share
        </p>
        <h2 className="text-4xl font-black text-gray-900">
          {poolSharePercent < 0.01 && poolSharePercent > 0
            ? '<0.01'
            : poolSharePercent.toFixed(2)}
          %
        </h2>
      </Card>
    </div>
  );
}

// ===========================================
// RESOURCE VAULT
// ===========================================

function ResourceVault({
  pendingReward,
  lifetimeEarnings,
  totalClaimedUsd,
  onOpenShare,
}: {
  pendingReward: number;
  lifetimeEarnings: number;
  totalClaimedUsd: number;
  onOpenShare: () => void;
}) {
  return (
    <>
      {/* Single GOLD Card */}
      <div className="grid grid-cols-1 gap-4">
        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm border-b-4 border-b-yellow-400">
          <h4 className="text-yellow-600 font-bold text-xs uppercase tracking-widest mb-1">
            GOLD Rewards
          </h4>
          <div className="text-2xl font-black text-gray-900">
            +{formatGOLD(pendingReward)}{' '}
            <span className="text-xs text-gray-400 font-normal uppercase">
              pending
            </span>
          </div>
          <div className="mt-4 text-[10px] text-gray-400 font-bold uppercase">
            Lifetime: {formatGOLD(lifetimeEarnings)} GOLD
          </div>
        </div>
      </div>

      {/* Total Claimed Value Bar */}
      <div className="bg-black rounded-2xl p-8 text-white flex flex-col md:flex-row justify-between items-center gap-6 shadow-2xl">
        <div className="text-center md:text-left">
          <div className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-2">
            Total Claimed Value
          </div>
          <div className="text-5xl font-black tracking-tighter">
            {formatUSD(totalClaimedUsd)}
          </div>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <Button variant="ghost" onClick={onOpenShare} className="px-4">
            <Share2 className="w-5 h-5" />
          </Button>
          <Button
            variant="secondary"
            className="w-full md:w-auto px-12 py-4 text-base font-bold"
            disabled
          >
            Auto-Distributes
          </Button>
        </div>
      </div>
    </>
  );
}

// ===========================================
// LEADERBOARD
// ===========================================

function Leaderboard({
  entries,
  currentUser,
  userRank,
  userHoldings,
  isConnected,
}: {
  entries: Array<{
    wallet: string;
    walletShort: string;
    totalEarned: number;
    rank: number;
  }>;
  currentUser: string;
  userRank: number | null;
  userHoldings: number;
  isConnected: boolean;
}) {
  const truncateAddress = (addr: string) =>
    addr.length > 12 ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : addr;

  return (
    <Card>
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Trophy className="w-6 h-6 text-black" />
          <h3 className="text-xl font-bold">Network Rankings</h3>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="text-[10px] text-gray-400 font-bold uppercase tracking-widest border-b border-gray-50">
            <tr>
              <th className="pb-4">Rank</th>
              <th className="pb-4">Address</th>
              <th className="pb-4 text-right">Earned</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {entries.map((miner, idx) => (
              <tr key={miner.wallet} className="text-sm">
                <td className="py-4 font-bold">
                  {String(idx + 1).padStart(2, '0')}
                </td>
                <td className="py-4 font-mono text-gray-500">
                  {miner.walletShort}
                </td>
                <td className="py-4 text-right font-medium">
                  {formatCompactNumber(miner.totalEarned)}
                </td>
              </tr>
            ))}
            {userRank && (
              <tr className="bg-gray-50/80 font-bold">
                <td className="py-4 pl-2">{userRank}</td>
                <td className="py-4 font-mono">
                  {isConnected ? truncateAddress(currentUser) : 'YOU'}
                </td>
                <td className="py-4 text-right">
                  {formatCompactNumber(userHoldings)}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ===========================================
// ACTIVITY LOG
// ===========================================

function ActivityLog({
  logs,
}: {
  logs: Array<{ id: string; time: string; msg: string }>;
}) {
  return (
    <Card className="h-full min-h-[400px] flex flex-col bg-gray-50/50 border-dashed border-2">
      <div className="flex items-center gap-2 mb-8">
        <Activity className="w-4 h-4 text-gray-400" />
        <h3 className="text-sm font-bold uppercase tracking-widest text-gray-500">
          Live Telemetry
        </h3>
      </div>
      <div className="flex-1 space-y-6">
        {logs.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-20 uppercase tracking-widest">
            Awaiting Stake...
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className="flex flex-col gap-1 border-l-2 border-black pl-4 animate-fade-in-right"
            >
              <span className="text-[10px] text-gray-400 font-mono font-bold uppercase">
                {log.time}
              </span>
              <span className="text-xs font-bold text-gray-800">{log.msg}</span>
            </div>
          ))
        )}
      </div>
    </Card>
  );
}

// ===========================================
// FOOTER
// ===========================================

function Footer() {
  return (
    <footer className="py-20 text-center border-t border-gray-100">
      <div className="flex items-center justify-center gap-2 mb-4">
        <Pickaxe className="w-5 h-5 text-black" />
        <span className="font-black tracking-tighter text-xl">PROTOCOL</span>
      </div>
      <p className="text-sm text-gray-400">
        © 2026 Resource Digitization Network. All rights reserved.
      </p>
    </footer>
  );
}

// ===========================================
// MAIN PAGE
// ===========================================

export default function HomePage() {
  const dashboardRef = useRef<HTMLElement>(null);
  const { address, setAddress } = useAddressContext();

  // State
  const [addressInput, setAddressInput] = useState('');
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [isGeneratingCard, setIsGeneratingCard] = useState(false);

  const isConnected = !!address;

  // API hooks
  const { data: stats } = useUserStats(address);
  const { data: pool } = usePoolStatus();
  const { data: leaderboard } = useLeaderboard(10, address);
  const { data: history } = useUserHistory(address, 20);

  // Computed values
  const earningRate = calculateEarningRate(
    stats?.pendingReward ?? 0,
    pool?.hoursSinceLast ?? null
  );
  const tickingReward = useTickingCounter(stats?.pendingReward ?? 0, earningRate);

  const lifetimeEarnings = useMemo(() => {
    if (!history || history.length === 0) return 0;
    return history.reduce((sum, item) => sum + item.amount_received, 0);
  }, [history]);

  const totalClaimedUsd = useMemo(() => {
    if (!lifetimeEarnings || !pool?.goldPriceUsd) return 0;
    return lifetimeEarnings * pool.goldPriceUsd;
  }, [lifetimeEarnings, pool?.goldPriceUsd]);

  // Transform history to logs
  const miningLogs = useMemo(() => {
    if (!history || history.length === 0) return [];
    return history.slice(0, 5).map((item, idx) => {
      const date = new Date(item.executed_at);
      return {
        id: `${item.distribution_id}-${idx}`,
        time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        msg: `Received ${formatGOLD(item.amount_received)} GOLD`,
      };
    });
  }, [history]);

  // Handlers
  const handleInitialize = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!addressInput) return;

    setAddress(addressInput);

    setTimeout(() => {
      dashboardRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleOpenBuy = () => {
    window.open(branding.buyTokenUrl, '_blank');
  };

  const handleDownloadShareCard = async () => {
    if (!stats || !address) return;

    setIsGeneratingCard(true);
    try {
      const blob = await generateShareCard(
        { ...stats, pendingReward: tickingReward },
        {
          totalHolders: leaderboard?.length ?? 0,
          lifetimeEarnings,
          lifetimeEarningsUsd: totalClaimedUsd,
          pendingRewardUsd: tickingReward * (pool?.goldPriceUsd ?? 0),
        }
      );
      const filename = `${branding.holdToken.symbol.toLowerCase()}-stats-${Date.now()}.png`;
      downloadBlob(blob, filename);
    } catch (error) {
      console.error('Failed to generate share card:', error);
    } finally {
      setIsGeneratingCard(false);
    }
  };

  const truncateAddress = (addr: string) =>
    addr.length > 12 ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : addr;

  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans selection:bg-gray-100 scroll-smooth">
      {/* 1. HERO */}
      <HeroSection
        addressInput={addressInput}
        setAddressInput={setAddressInput}
        onInitialize={handleInitialize}
      />

      {/* 2. DASHBOARD */}
      <section
        ref={dashboardRef}
        className={cn(
          'transition-all duration-700 py-20 bg-gray-50/50',
          isConnected
            ? 'opacity-100'
            : 'opacity-40 grayscale pointer-events-none'
        )}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          {/* Header Area */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">
                Mining Terminal
              </h2>
              <p className="text-gray-500 font-mono text-sm">
                {isConnected
                  ? `Tracking: ${truncateAddress(address!)}`
                  : 'Enter an address above to begin.'}
              </p>
            </div>
            {!isConnected && (
              <div className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium animate-pulse">
                Address Required
              </div>
            )}
          </div>

          {/* Stats Overview */}
          <StatsOverview
            holdings={stats?.balance ?? 0}
            miningRate={earningRate}
            poolSharePercent={stats?.poolSharePercent ?? 0}
            onOpenBuy={handleOpenBuy}
          />

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <ResourceVault
                pendingReward={tickingReward}
                lifetimeEarnings={lifetimeEarnings}
                totalClaimedUsd={totalClaimedUsd}
                onOpenShare={() => setIsShareModalOpen(true)}
              />

              <Leaderboard
                entries={leaderboard ?? []}
                currentUser={address ?? ''}
                userRank={stats?.rank ?? null}
                userHoldings={stats?.balance ?? 0}
                isConnected={isConnected}
              />
            </div>

            <div className="lg:col-span-1">
              <ActivityLog logs={miningLogs} />
            </div>
          </div>
        </div>
      </section>

      <Footer />

      {/* Share Modal */}
      <Modal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        title="Share Achievement"
      >
        <div className="space-y-6">
          <div className="bg-black text-white p-8 rounded-xl relative overflow-hidden shadow-2xl border border-gray-800">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <Pickaxe className="w-32 h-32" />
            </div>

            <div className="relative z-10 space-y-6">
              <div className="flex items-center gap-2 mb-8">
                <div className="bg-white text-black p-1.5 rounded-lg">
                  <Pickaxe className="w-4 h-4" />
                </div>
                <span className="font-bold tracking-tight text-sm">
                  PROTOCOL TERMINAL
                </span>
              </div>

              <div>
                <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">
                  Total Claimed
                </p>
                <h2 className="text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-600">
                  {formatUSD(totalClaimedUsd)}
                </h2>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/10">
                <div>
                  <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest">
                    Miner
                  </p>
                  <p className="font-mono text-sm">
                    {truncateAddress(address || '0x00...0000')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest">
                    Holdings
                  </p>
                  <p className="font-mono text-sm">
                    {formatCompactNumber(stats?.balance ?? 0)} POH
                  </p>
                </div>
              </div>
            </div>
          </div>

          <Button
            onClick={handleDownloadShareCard}
            disabled={isGeneratingCard || !stats}
            className="w-full py-4 font-bold"
          >
            {isGeneratingCard ? 'Generating...' : 'Download Card Image'}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
