evmAsk.js:15 Uncaught TypeError: Cannot redefine property: ethereum
    at Object.defineProperty (<anonymous>)
    at r.inject (evmAsk.js:15:5093)
    at window.addEventListener.once (evmAsk.js:15:9013)
react-dom.development.js:29890 Download the React DevTools for a better development experience: https://reactjs.org/link/react-devtools
index.js:642 Uncaught Error: Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 |
  5 | export interface FooterProps {
  6 |   className?: string;

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
    at <unknown> (https://nextjs.org/docs/messages/module-not-found)
    at getNotFoundError (file://C:\Projects\copper-processing-unit\frontend\node_modules\next\dist\build\webpack\plugins\wellknown-errors-plugin\parseNotFoundError.js:140:16)
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)
    at async getModuleBuildError (file://C:\Projects\copper-processing-unit\frontend\node_modules\next\dist\build\webpack\plugins\wellknown-errors-plugin\webpackModuleError.js:103:27)
    at async (file://C:\Projects\copper-processing-unit\frontend\node_modules\next\dist\build\webpack\plugins\wellknown-errors-plugin\index.js:29:49)
    at async (file://C:\Projects\copper-processing-unit\frontend\node_modules\next\dist\build\webpack\plugins\wellknown-errors-plugin\index.js:27:21)
websocket.js:46 [HMR] connected
pages-dev-overlay-setup.js:77 ./src/components/landing/Footer.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 |
  5 | export interface FooterProps {
  6 |   className?: string;

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/Hero.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { formatCompactNumber } from '@/lib/utils';
  5 | import { ConnectButton } from '@/components/wallet/ConnectButton';
  6 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/Hero.tsx:4:1
Module not found: Can't resolve '@/lib/utils'
  2 |
  3 | import { cn } from '@/lib/cn';
> 4 | import { formatCompactNumber } from '@/lib/utils';
    | ^
  5 | import { ConnectButton } from '@/components/wallet/ConnectButton';
  6 |
  7 | export interface HeroProps {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/HowItWorks.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { Card, PixelIcon } from '@/components/ui';
  5 |
  6 | export interface HowItWorksProps {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/LiveStatsBar.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { formatCompactNumber, formatUSD } from '@/lib/utils';
  5 | import { Skeleton } from '@/components/ui';
  6 | import { useCountdown, useAnimatedNumber } from '@/hooks/useCountdown';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/LiveStatsBar.tsx:4:1
Module not found: Can't resolve '@/lib/utils'
  2 |
  3 | import { cn } from '@/lib/cn';
> 4 | import { formatCompactNumber, formatUSD } from '@/lib/utils';
    | ^
  5 | import { Skeleton } from '@/components/ui';
  6 | import { useCountdown, useAnimatedNumber } from '@/hooks/useCountdown';
  7 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/TierExplainer.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { formatMultiplier, formatDuration } from '@/lib/utils';
  5 | import { TIER_CONFIG, type TierId } from '@/types/models';
  6 | import { Card, PixelProgress } from '@/components/ui';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/landing/TierExplainer.tsx:4:1
Module not found: Can't resolve '@/lib/utils'
  2 |
  3 | import { cn } from '@/lib/cn';
> 4 | import { formatMultiplier, formatDuration } from '@/lib/utils';
    | ^
  5 | import { TIER_CONFIG, type TierId } from '@/types/models';
  6 | import { Card, PixelProgress } from '@/components/ui';
  7 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/layout/Header.tsx:5:1
Module not found: Can't resolve '@/lib/cn'
  3 | import Link from 'next/link';
  4 | import { usePathname } from 'next/navigation';
> 5 | import { cn } from '@/lib/cn';
    | ^
  6 | import { ConnectButton } from '@/components/wallet/ConnectButton';
  7 |
  8 | const NAV_LINKS = [

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/layout/PageContainer.tsx
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/layout/MobileNav.tsx:5:1
Module not found: Can't resolve '@/lib/cn'
  3 | import Link from 'next/link';
  4 | import { usePathname } from 'next/navigation';
> 5 | import { cn } from '@/lib/cn';
    | ^
  6 |
  7 | const NAV_ITEMS = [
  8 |   {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/layout/PageContainer.tsx
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/layout/PageContainer.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { Header } from './Header';
  5 | import { MobileNav } from './MobileNav';
  6 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/providers/QueryProvider.tsx:5:1
Module not found: Can't resolve '@/lib/constants'
  3 | import { FC, ReactNode, useState } from 'react';
  4 | import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
> 5 | import { DEFAULT_STALE_TIME } from '@/lib/constants';
    | ^
  6 |
  7 | interface QueryProviderProps {
  8 |   children: ReactNode;

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/providers/Providers.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/providers/WalletProvider.tsx:16:1
Module not found: Can't resolve '@/lib/constants'
  14 |   TorusWalletAdapter,
  15 | } from '@solana/wallet-adapter-wallets';
> 16 | import { SOLANA_RPC_URL } from '@/lib/constants';
     | ^
  17 |
  18 | // Import wallet adapter styles
  19 | import '@solana/wallet-adapter-react-ui/styles.css';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/providers/Providers.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/Badge.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import type { TierInfo } from '@/types/api';
  5 |
  6 | export interface BadgeProps {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/Button.tsx:4:1
Module not found: Can't resolve '@/lib/cn'
  2 |
  3 | import { forwardRef, ButtonHTMLAttributes } from 'react';
> 4 | import { cn } from '@/lib/cn';
    | ^
  5 | import { LoadingSpinner } from './LoadingSpinner';
  6 |
  7 | export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/wallet/ConnectButton.tsx
./src/components/layout/Header.tsx
./src/components/layout/PageContainer.tsx
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/Card.tsx:4:1
Module not found: Can't resolve '@/lib/cn'
  2 |
  3 | import { forwardRef, HTMLAttributes, ReactNode } from 'react';
> 4 | import { cn } from '@/lib/cn';
    | ^
  5 |
  6 | export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  7 |   /** Card title (displayed in header) */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/ConnectionIndicator.tsx:16:1
Module not found: Can't resolve '@/lib/cn'
  14 | import { useSocketContext } from '@/components/providers/SocketProvider';
  15 | import { useIsDesktop } from '@/hooks';
> 16 | import { cn } from '@/lib/cn';
     | ^
  17 |
  18 | // ============================================================================
  19 | // Types

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/EmptyState.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { Button } from './Button';
  5 |
  6 | export interface EmptyStateProps {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/ErrorDisplay.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 | import { TerminalCard } from './TerminalCard';
  5 | import { Button } from './Button';
  6 | import { getErrorMessage } from '@/lib/api';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/ErrorDisplay.tsx:6:1
Module not found: Can't resolve '@/lib/api'
  4 | import { TerminalCard } from './TerminalCard';
  5 | import { Button } from './Button';
> 6 | import { getErrorMessage } from '@/lib/api';
    | ^
  7 |
  8 | export interface ErrorDisplayProps {
  9 |   /** Error title */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/LoadingSpinner.tsx:4:1
Module not found: Can't resolve '@/lib/cn'
  2 |
  3 | import { useEffect, useState } from 'react';
> 4 | import { cn } from '@/lib/cn';
    | ^
  5 |
  6 | const ASCII_SPINNER_FRAMES = ['|', '/', '-', '\\'];
  7 | const ASCII_DOTS_FRAMES = ['.  ', '.. ', '...', '   '];

https://nextjs.org/docs/messages/module-not-found
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/PixelIcon.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 |
  5 | export interface PixelIconProps {
  6 |   /** Icon name */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/PixelProgress.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 |
  5 | export interface PixelProgressProps {
  6 |   /** Current progress value */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/Skeleton.tsx:3:1
Module not found: Can't resolve '@/lib/cn'
  1 | 'use client';
  2 |
> 3 | import { cn } from '@/lib/cn';
    | ^
  4 |
  5 | export interface SkeletonProps {
  6 |   /** Additional class names */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/TerminalCard.tsx:4:1
Module not found: Can't resolve '@/lib/cn'
  2 |
  3 | import { forwardRef, HTMLAttributes, ReactNode } from 'react';
> 4 | import { cn } from '@/lib/cn';
    | ^
  5 |
  6 | export interface TerminalCardProps extends HTMLAttributes<HTMLDivElement> {
  7 |   /** Card title (displayed in header) */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/ErrorDisplay.tsx
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/ui/Text.tsx:4:1
Module not found: Can't resolve '@/lib/cn'
  2 |
  3 | import { forwardRef, HTMLAttributes } from 'react';
> 4 | import { cn } from '@/lib/cn';
    | ^
  5 |
  6 | export interface TextProps extends HTMLAttributes<HTMLSpanElement> {
  7 |   /** Text variant */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/wallet/ConnectButton.tsx:6:1
Module not found: Can't resolve '@/lib/cn'
  4 | import { useWallet } from '@/hooks/useWallet';
  5 | import { Button } from '@/components/ui/Button';
> 6 | import { cn } from '@/lib/cn';
    | ^
  7 | import { isValidWalletIconUrl } from '@/lib/validators';
  8 |
  9 | export interface ConnectButtonProps {

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/layout/Header.tsx
./src/components/layout/PageContainer.tsx
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/components/wallet/ConnectButton.tsx:7:1
Module not found: Can't resolve '@/lib/validators'
   5 | import { Button } from '@/components/ui/Button';
   6 | import { cn } from '@/lib/cn';
>  7 | import { isValidWalletIconUrl } from '@/lib/validators';
     | ^
   8 |
   9 | export interface ConnectButtonProps {
  10 |   /** Button size */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/layout/Header.tsx
./src/components/layout/PageContainer.tsx
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useDistributions.ts:5:1
Module not found: Can't resolve '@/lib/api'
  3 | import { useQuery } from '@tanstack/react-query';
  4 | import { useMemo } from 'react';
> 5 | import { getDistributions } from '@/lib/api';
    | ^
  6 | import { formatTimeAgo } from '@/lib/utils';
  7 | import type { DistributionItem } from '@/types/api';
  8 | import type { FormattedDistribution } from '@/types/models';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useDistributions.ts:6:1
Module not found: Can't resolve '@/lib/utils'
  4 | import { useMemo } from 'react';
  5 | import { getDistributions } from '@/lib/api';
> 6 | import { formatTimeAgo } from '@/lib/utils';
    | ^
  7 | import type { DistributionItem } from '@/types/api';
  8 | import type { FormattedDistribution } from '@/types/models';
  9 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useGlobalStats.ts:4:1
Module not found: Can't resolve '@/lib/api'
  2 |
  3 | import { useQuery } from '@tanstack/react-query';
> 4 | import { getGlobalStats } from '@/lib/api';
    | ^
  5 | import { DEFAULT_REFETCH_INTERVAL } from '@/lib/constants';
  6 | import type { GlobalStatsResponse } from '@/types/api';
  7 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useGlobalStats.ts:5:1
Module not found: Can't resolve '@/lib/constants'
  3 | import { useQuery } from '@tanstack/react-query';
  4 | import { getGlobalStats } from '@/lib/api';
> 5 | import { DEFAULT_REFETCH_INTERVAL } from '@/lib/constants';
    | ^
  6 | import type { GlobalStatsResponse } from '@/types/api';
  7 |
  8 | /** Query key for global stats */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useLeaderboard.ts:5:1
Module not found: Can't resolve '@/lib/api'
  3 | import { useQuery } from '@tanstack/react-query';
  4 | import { useMemo } from 'react';
> 5 | import { getLeaderboard } from '@/lib/api';
    | ^
  6 | import type { LeaderboardEntry } from '@/types/api';
  7 | import type { LeaderboardUser } from '@/types/models';
  8 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/usePoolStatus.ts:5:1
Module not found: Can't resolve '@/lib/api'
  3 | import { useQuery } from '@tanstack/react-query';
  4 | import { useMemo } from 'react';
> 5 | import { getPoolStatus } from '@/lib/api';
    | ^
  6 | import { POOL_REFETCH_INTERVAL } from '@/lib/constants';
  7 | import { DISTRIBUTION_THRESHOLD_USD } from '@/types/models';
  8 | import type { PoolStatusResponse } from '@/types/api';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/usePoolStatus.ts:6:1
Module not found: Can't resolve '@/lib/constants'
  4 | import { useMemo } from 'react';
  5 | import { getPoolStatus } from '@/lib/api';
> 6 | import { POOL_REFETCH_INTERVAL } from '@/lib/constants';
    | ^
  7 | import { DISTRIBUTION_THRESHOLD_USD } from '@/types/models';
  8 | import type { PoolStatusResponse } from '@/types/api';
  9 | import type { PoolInfo } from '@/types/models';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useTiers.ts:4:1
Module not found: Can't resolve '@/lib/api'
  2 |
  3 | import { useQuery } from '@tanstack/react-query';
> 4 | import { getTiers } from '@/lib/api';
    | ^
  5 | import type { TierConfig } from '@/types/api';
  6 |
  7 | /** Query key for tiers */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useUserHistory.ts:4:1
Module not found: Can't resolve '@/lib/api'
  2 |
  3 | import { useQuery } from '@tanstack/react-query';
> 4 | import { getUserHistory } from '@/lib/api';
    | ^
  5 | import type { DistributionHistoryItem } from '@/types/api';
  6 |
  7 | /** Query key factory for user history */

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useUserStats.ts:5:1
Module not found: Can't resolve '@/lib/api'
  3 | import { useQuery } from '@tanstack/react-query';
  4 | import { useMemo } from 'react';
> 5 | import { getUserStats } from '@/lib/api';
    | ^
  6 | import { USER_STATS_REFETCH_INTERVAL } from '@/lib/constants';
  7 | import { calculateTierProgress } from '@/lib/utils';
  8 | import type { UserStatsResponse } from '@/types/api';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useUserStats.ts:6:1
Module not found: Can't resolve '@/lib/constants'
  4 | import { useMemo } from 'react';
  5 | import { getUserStats } from '@/lib/api';
> 6 | import { USER_STATS_REFETCH_INTERVAL } from '@/lib/constants';
    | ^
  7 | import { calculateTierProgress } from '@/lib/utils';
  8 | import type { UserStatsResponse } from '@/types/api';
  9 | import type { UserMiningStats } from '@/types/models';

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/api/useUserStats.ts:7:1
Module not found: Can't resolve '@/lib/utils'
   5 | import { getUserStats } from '@/lib/api';
   6 | import { USER_STATS_REFETCH_INTERVAL } from '@/lib/constants';
>  7 | import { calculateTierProgress } from '@/lib/utils';
     | ^
   8 | import type { UserStatsResponse } from '@/types/api';
   9 | import type { UserMiningStats } from '@/types/models';
  10 |

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/api/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/useMediaQuery.ts:4:1
Module not found: Can't resolve '@/lib/constants'
  2 |
  3 | import { useState, useEffect } from 'react';
> 4 | import { DESKTOP_BREAKPOINT } from '@/lib/constants';
    | ^
  5 |
  6 | /**
  7 |  * Hook to check if a media query matches

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/index.ts
./src/components/ui/ConnectionIndicator.tsx
./src/components/ui/index.ts
./src/components/landing/LiveStatsBar.tsx
./src/components/landing/index.ts
./src/app/page.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/useWallet.ts:6:1
Module not found: Can't resolve '@/lib/utils'
  4 | import { useWalletModal } from '@solana/wallet-adapter-react-ui';
  5 | import { useMemo, useCallback } from 'react';
> 6 | import { shortenAddress } from '@/lib/utils';
    | ^
  7 |
  8 | /**
  9 |  * Custom wallet hook

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/hooks/useWebSocket.ts
./src/components/providers/SocketProvider.tsx
./src/components/providers/Providers.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
pages-dev-overlay-setup.js:77 ./src/hooks/useWebSocket.ts:13:1
Module not found: Can't resolve '@/lib/socket'
  11 | import { useQueryClient } from '@tanstack/react-query';
  12 | import { useWalletAddress, useIsConnected } from './useWallet';
> 13 | import {
     | ^
  14 |   getSocket,
  15 |   disconnectSocket,
  16 |   subscribeToWallet,

https://nextjs.org/docs/messages/module-not-found

Import trace for requested module:
./src/components/providers/SocketProvider.tsx
./src/components/providers/Providers.tsx
nextJsHandleConsoleError @ pages-dev-overlay-setup.js:77
favicon.ico:1  Failed to load resource: the server responded with a status of 404 (Not Found)
index.js:1631 Object
