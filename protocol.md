import React, { useState, useEffect, useRef } from 'react';
import { 
  Pickaxe, 
  Wallet, 
  TrendingUp, 
  ArrowRightLeft, 
  Hexagon, 
  CircleDollarSign,
  Activity,
  Box,
  Cpu,
  Trophy,
  Users,
  ChevronDown,
  Hash,
  Share2
} from 'lucide-react';

/**
 * ------------------------------------------------------------------
 * CONSTANTS & CONFIGURATION
 * ------------------------------------------------------------------
 */
const CONFIG = {
  TOKEN_PRICE: 10,
  INITIAL_BALANCE: 5000,
  RATES: {
    GOLD: 0.0001,
    SILVER: 0.0015,
    COPPER: 0.0150,
  }
};

const MOCK_LEADERBOARD = [
  { id: 1, address: '0x71...9A21', holdings: 45420, minedValue: 18432.50, status: 'active' },
  { id: 2, address: '0x33...B1C9', holdings: 32100, minedValue: 12210.20, status: 'active' },
  { id: 3, address: '0xA4...E2F1', holdings: 15400, minedValue: 5100.80, status: 'idle' },
  { id: 4, address: '0x99...1D42', holdings: 8100, minedValue: 2850.40, status: 'active' },
];

/**
 * ------------------------------------------------------------------
 * SHARED UI COMPONENTS
 * ------------------------------------------------------------------
 */
const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl border border-gray-100 shadow-sm p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ children, onClick, variant = 'primary', disabled = false, className = '' }) => {
  const baseStyle = "px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm";
  const variants = {
    primary: "bg-black text-white hover:bg-gray-800 shadow-md",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
    outline: "border border-gray-200 text-gray-600 hover:border-black hover:text-black",
    ghost: "bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm"
  };
  
  return (
    <button onClick={onClick} disabled={disabled} className={`${baseStyle} ${variants[variant] || variants.primary} ${className}`}>
      {children}
    </button>
  );
};

const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full overflow-hidden animate-fade-in-up">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center">
          <h3 className="text-lg font-bold text-gray-900">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-900 text-2xl leading-none">&times;</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
};

/**
 * ------------------------------------------------------------------
 * FEATURE COMPONENTS
 * ------------------------------------------------------------------
 */

const HeroSection = ({ addressInput, setAddressInput, onInitialize }) => (
  <section className="relative h-screen flex flex-col justify-center items-center text-center px-4 overflow-hidden border-b border-gray-50">
    <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
    
    <div className="mb-8 p-4 bg-gray-50 rounded-2xl border border-gray-100 flex items-center justify-center animate-bounce">
      <Pickaxe className="w-10 h-10 text-black" />
    </div>
    
    <h1 className="text-6xl font-extrabold tracking-tight mb-6 max-w-3xl leading-tight">
      Proof of <span className="text-gray-400">Hold</span>. <br />
      Mine the Future.
    </h1>
    
    <p className="text-xl text-gray-400 mb-10 max-w-xl leading-relaxed">
      The first algorithmic resource protocol where <span className="text-black font-semibold">Holding is Mining</span>. Paste your address to access your terminal.
    </p>
    
    <div className="w-full max-w-md z-10 space-y-4">
      <form onSubmit={onInitialize} className="flex flex-col sm:flex-row gap-2 bg-white p-2 rounded-2xl border border-gray-200 shadow-sm">
        <input 
           type="text" 
           placeholder="Paste Wallet Address (0x...)" 
           className="flex-1 px-4 py-3 outline-none text-sm font-medium rounded-xl focus:bg-gray-50 transition-colors"
           value={addressInput}
           onChange={(e) => setAddressInput(e.target.value)}
        />
        <Button onClick={onInitialize} className="whitespace-nowrap py-3 px-6">
          Start Mining
          <ArrowRightLeft className="w-4 h-4" />
        </Button>
      </form>
      <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">No wallet connection required. Read-only visualization.</p>
    </div>

    <div className="absolute bottom-10 animate-pulse flex flex-col items-center text-gray-300">
        <span className="text-xs font-medium tracking-widest uppercase mb-2">Scroll to Terminal</span>
        <ChevronDown className="w-5 h-5" />
    </div>
  </section>
);

const StatsOverview = ({ holdings, miningRate, walletBalance, formatCurrency, formatNumber, onOpenBuy }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <Card className="group relative">
      <Hexagon className="absolute top-6 right-6 w-8 h-8 text-gray-50 opacity-0 group-hover:opacity-100 transition-opacity" />
      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Protocol Holdings</p>
      <div className="flex items-baseline gap-2">
        <h2 className="text-4xl font-black text-gray-900">{formatNumber(holdings)}</h2>
        <span className="text-xs font-bold text-gray-400">PROTOCOL</span>
      </div>
      <div className="mt-6 flex gap-2">
         <Button variant="primary" className="flex-1" onClick={onOpenBuy}>Buy Tokens</Button>
         <Button variant="outline" className="px-4">Swap</Button>
      </div>
    </Card>

    <Card>
      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Mining Power</p>
      <div className="flex items-center gap-3">
         <div className={`w-3 h-3 rounded-full ${holdings > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-gray-300'}`}></div>
         <h2 className="text-4xl font-black text-gray-900 uppercase">{holdings > 0 ? 'Active' : 'Idle'}</h2>
      </div>
      <p className="mt-4 text-sm text-gray-500">
        Rate: <span className="text-black font-bold">~{formatCurrency(miningRate)} / hr</span>
      </p>
    </Card>

    <Card>
      <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Available Balance</p>
      <h2 className="text-4xl font-black text-gray-900">{formatCurrency(walletBalance)}</h2>
      <p className="mt-4 text-sm text-gray-500">Asset: <span className="text-black font-bold">USDT (Simulated)</span></p>
    </Card>
  </div>
);

const ResourceVault = ({ rewards, minedValue, formatNumber, formatCurrency, onOpenShare }) => (
  <>
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'GOLD (Au)', key: 'gold', unit: 'oz', color: 'yellow', price: '$2,032' },
          { label: 'SILVER (Ag)', key: 'silver', unit: 'oz', color: 'slate', price: '$24.50' },
          { label: 'COPPER (Cu)', key: 'copper', unit: 'lbs', color: 'orange', price: '$3.80' }
        ].map((metal) => (
          <div key={metal.key} className={`bg-white p-6 rounded-xl border border-gray-100 shadow-sm border-b-4 border-b-${metal.color}-400`}>
              <h4 className={`text-${metal.color}-600 font-bold text-xs uppercase tracking-widest mb-1`}>{metal.label}</h4>
              <div className="text-2xl font-black text-gray-900">
                  {formatNumber(rewards[metal.key])} <span className="text-xs text-gray-400 font-normal uppercase">{metal.unit}</span>
              </div>
              <div className="mt-4 text-[10px] text-gray-400 font-bold uppercase">Spot: {metal.price}</div>
          </div>
        ))}
    </div>

    <div className="bg-black rounded-2xl p-8 text-white flex flex-col md:flex-row justify-between items-center gap-6 shadow-2xl">
        <div className="text-center md:text-left">
            <div className="text-gray-500 text-xs font-bold uppercase tracking-widest mb-2">Unclaimed Vault Value</div>
            <div className="text-5xl font-black tracking-tighter">
              {formatCurrency(minedValue)}
            </div>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <Button variant="ghost" onClick={onOpenShare} className="px-4">
              <Share2 className="w-5 h-5" />
          </Button>
          <Button variant="secondary" className="w-full md:w-auto px-12 py-4 text-base font-bold">Claim All Rewards</Button>
        </div>
    </div>
  </>
);

const Leaderboard = ({ leaderboardData, currentUser, holdings, minedValue, isConnected, formatNumber, formatCurrency, truncateAddress }) => (
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
                      <th className="pb-4 text-right">Holdings</th>
                      <th className="pb-4 text-right">Mined Value</th>
                  </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                  {leaderboardData.map((miner, idx) => (
                      <tr key={miner.id} className="text-sm">
                          <td className="py-4 font-bold">0{idx + 1}</td>
                          <td className="py-4 font-mono text-gray-500">{miner.address}</td>
                          <td className="py-4 text-right font-medium">{formatNumber(miner.holdings)}</td>
                          <td className="py-4 text-right font-bold">{formatCurrency(miner.minedValue)}</td>
                      </tr>
                  ))}
                  <tr className="bg-gray-50/80 font-bold">
                      <td className="py-4 pl-2">421</td>
                      <td className="py-4 font-mono">{isConnected ? truncateAddress(currentUser) : 'YOU'}</td>
                      <td className="py-4 text-right">{formatNumber(holdings)}</td>
                      <td className="py-4 text-right text-emerald-600">{formatCurrency(minedValue)}</td>
                  </tr>
              </tbody>
          </table>
      </div>
  </Card>
);

const ActivityLog = ({ logs }) => (
  <Card className="h-full min-h-[400px] flex flex-col bg-gray-50/50 border-dashed border-2">
     <div className="flex items-center gap-2 mb-8">
       <Activity className="w-4 h-4 text-gray-400" />
       <h3 className="text-sm font-bold uppercase tracking-widest text-gray-500">Live Telemetry</h3>
     </div>
     <div className="flex-1 space-y-6">
        {logs.length === 0 ? (
          <div className="text-xs text-gray-400 text-center py-20 uppercase tracking-widest">Awaiting Stake...</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="flex flex-col gap-1 border-l-2 border-black pl-4 animate-fade-in-right">
               <span className="text-[10px] text-gray-400 font-mono font-bold uppercase">{log.time}</span>
               <span className="text-xs font-bold text-gray-800">{log.msg}</span>
            </div>
          ))
        )}
     </div>
  </Card>
);

const Footer = () => (
  <footer className="py-20 text-center border-t border-gray-100">
     <div className="flex items-center justify-center gap-2 mb-4">
        <Pickaxe className="w-5 h-5 text-black" />
        <span className="font-black tracking-tighter text-xl">PROTOCOL</span>
     </div>
     <p className="text-sm text-gray-400">© 2026 Resource Digitization Network. All rights reserved.</p>
  </footer>
);

/**
 * ------------------------------------------------------------------
 * MAIN APPLICATION CONTAINER
 * ------------------------------------------------------------------
 */
export default function App() {
  const dashboardRef = useRef(null);
  
  // -- STATE --
  const [isConnected, setIsConnected] = useState(false);
  const [userAddress, setUserAddress] = useState('');
  const [addressInput, setAddressInput] = useState('');
  
  const [walletBalance, setWalletBalance] = useState(CONFIG.INITIAL_BALANCE);
  const [holdings, setHoldings] = useState(0);
  const [myMinedValue, setMyMinedValue] = useState(0);
  const [rewards, setRewards] = useState({ gold: 0, silver: 0, copper: 0 });
  const [miningRate, setMiningRate] = useState(0);
  
  const [isBuyModalOpen, setIsBuyModalOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [buyAmount, setBuyAmount] = useState('');
  const [miningLog, setMiningLog] = useState([]);

  // -- MINING ENGINE --
  useEffect(() => {
    if (!isConnected || holdings === 0) {
      setMiningRate(0);
      return;
    }

    const timer = setInterval(() => {
      // Logic: More holdings = multiplier boost
      const boost = 1 + (holdings / 100); 
      
      const newGold = holdings * CONFIG.RATES.GOLD * boost;
      const newSilver = holdings * CONFIG.RATES.SILVER * boost;
      const newCopper = holdings * CONFIG.RATES.COPPER * boost;

      setRewards(prev => ({
        gold: prev.gold + newGold,
        silver: prev.silver + newSilver,
        copper: prev.copper + newCopper
      }));

      // 2032, 24.5, 3.8 are spot prices
      setMyMinedValue(prev => prev + (newGold * 2032) + (newSilver * 24.5) + (newCopper * 3.8));
      
      // Calculate Rate per Hour
      setMiningRate((newGold * 60 * 2032) + (newSilver * 60 * 24.5) + (newCopper * 60 * 3.8));

      // Random Logs
      if (Math.random() > 0.85) {
        const metals = ['Gold', 'Silver', 'Copper'];
        const metal = metals[Math.floor(Math.random() * metals.length)];
        setMiningLog(prev => [{ id: Date.now(), msg: `Extracted ${metal} Ore`, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 5));
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [isConnected, holdings]);

  // -- HANDLERS --
  const handleInitialize = (e) => {
    if (e) e.preventDefault();
    if (!addressInput) return;
    
    setUserAddress(addressInput);
    setIsConnected(true);
    setMiningLog([{ id: 1, msg: `Terminal authorized for ${addressInput.slice(0, 6)}...${addressInput.slice(-4)}`, time: new Date().toLocaleTimeString() }]);
    
    setTimeout(() => {
        dashboardRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleBuy = () => {
    const cost = Number(buyAmount) * CONFIG.TOKEN_PRICE;
    if (cost > walletBalance) return;
    setWalletBalance(prev => prev - cost);
    setHoldings(prev => prev + Number(buyAmount));
    setIsBuyModalOpen(false);
    setBuyAmount('');
  };

  // -- FORMATTERS --
  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  const formatNumber = (val) => new Intl.NumberFormat('en-US', { maximumFractionDigits: 4 }).format(val);
  const truncateAddress = (addr) => addr.length > 12 ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : addr;

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
        className={`transition-all duration-700 py-20 bg-gray-50/50 ${isConnected ? 'opacity-100' : 'opacity-40 grayscale pointer-events-none'}`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          
          {/* Header Area */}
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Mining Terminal</h2>
              <p className="text-gray-500 font-mono text-sm">{isConnected ? `Tracking: ${userAddress}` : 'Enter an address above to begin.'}</p>
            </div>
            {!isConnected && (
                <div className="bg-black text-white px-4 py-2 rounded-lg text-sm font-medium animate-pulse">
                    Address Required
                </div>
            )}
          </div>

          {/* Stats Component */}
          <StatsOverview 
            holdings={holdings}
            miningRate={miningRate}
            walletBalance={walletBalance}
            formatCurrency={formatCurrency}
            formatNumber={formatNumber}
            onOpenBuy={() => setIsBuyModalOpen(true)}
          />

          {/* Main Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <ResourceVault 
                rewards={rewards}
                minedValue={myMinedValue}
                formatNumber={formatNumber}
                formatCurrency={formatCurrency}
                onOpenShare={() => setIsShareModalOpen(true)}
              />
              
              <Leaderboard 
                leaderboardData={MOCK_LEADERBOARD}
                currentUser={userAddress}
                holdings={holdings}
                minedValue={myMinedValue}
                isConnected={isConnected}
                formatNumber={formatNumber}
                formatCurrency={formatCurrency}
                truncateAddress={truncateAddress}
              />
            </div>

            <div className="lg:col-span-1">
              <ActivityLog logs={miningLog} />
            </div>
          </div>
        </div>
      </section>

      <Footer />

      {/* -- MODALS -- */}
      
      {/* Buy Modal */}
      <Modal 
        isOpen={isBuyModalOpen} 
        onClose={() => setIsBuyModalOpen(false)} 
        title="Purchase Protocol Units"
      >
        <div className="space-y-6">
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl">
             <div>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Rate</p>
                <p className="font-bold">{formatCurrency(CONFIG.TOKEN_PRICE)}</p>
             </div>
             <div className="text-right">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">USDT Bal</p>
                <p className="font-bold">{formatCurrency(walletBalance)}</p>
             </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Token Amount</label>
            <input 
              type="number" 
              value={buyAmount}
              onChange={(e) => setBuyAmount(e.target.value)}
              className="block w-full rounded-xl border-gray-200 bg-white border p-4 font-bold text-lg focus:ring-0 focus:border-black transition-all outline-none"
              placeholder="0.00"
            />
          </div>

          <Button 
            onClick={handleBuy} 
            disabled={!buyAmount || (buyAmount * CONFIG.TOKEN_PRICE) > walletBalance} 
            className="w-full py-4 text-base font-bold"
          >
            Authorize Stake
          </Button>
        </div>
      </Modal>

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
                        <span className="font-bold tracking-tight text-sm">PROTOCOL TERMINAL</span>
                    </div>

                    <div>
                        <p className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Total Mined Value</p>
                        <h2 className="text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-yellow-400 to-yellow-600">
                            {formatCurrency(myMinedValue)}
                        </h2>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-6 border-t border-white/10">
                        <div>
                            <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest">Miner</p>
                            <p className="font-mono text-sm">{truncateAddress(userAddress || '0x00...0000')}</p>
                        </div>
                        <div>
                            <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest">Holdings</p>
                            <p className="font-mono text-sm">{formatNumber(holdings)} PROTOCOL</p>
                        </div>
                    </div>
                </div>
            </div>

            <Button onClick={() => alert('Screenshot captured! (Simulation)')} className="w-full py-4 font-bold">
                Download Card Image
            </Button>
         </div>
      </Modal>

      <style>{`
        @keyframes fade-in-up {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade-in-right {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-fade-in-up { animation: fade-in-up 0.3s ease-out; }
        .animate-fade-in-right { animation: fade-in-right 0.3s ease-out; }
      `}</style>
    </div>
  );
}