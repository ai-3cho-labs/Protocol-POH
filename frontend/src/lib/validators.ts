/**
 * Validation Utilities
 */

/**
 * Check if a URL is a valid wallet icon URL
 * Only allows specific trusted domains for wallet icons
 */
export function isValidWalletIconUrl(url: string | undefined | null): boolean {
  if (!url) return false;

  try {
    const parsed = new URL(url);

    // Allow data URIs for inline icons
    if (parsed.protocol === 'data:') {
      return url.startsWith('data:image/');
    }

    // Only allow HTTPS
    if (parsed.protocol !== 'https:') {
      return false;
    }

    // Trusted domains for wallet icons
    const trustedDomains = [
      'raw.githubusercontent.com',
      'arweave.net',
      'www.arweave.net',
      'shdw-drive.genesysgo.net',
      'cdn.jsdelivr.net',
      'assets.coingecko.com',
      'phantom.app',
      'solflare.com',
      'backpack.app',
      'glow.app',
    ];

    return trustedDomains.some(
      (domain) => parsed.hostname === domain || parsed.hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

/**
 * Validate a Solana wallet address format
 */
export function isValidSolanaAddress(address: string): boolean {
  if (!address) return false;
  // Base58 characters, typically 32-44 characters for Solana
  const base58Regex = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;
  return base58Regex.test(address);
}

/**
 * Validate an amount is positive
 */
export function isPositiveAmount(amount: number): boolean {
  return typeof amount === 'number' && !isNaN(amount) && amount > 0;
}

/**
 * Validate a redirect path is safe (no external URLs or protocol injection)
 */
export function isValidRedirectPath(path: string | undefined | null): boolean {
  if (!path) return false;

  // Must start with /
  if (!path.startsWith('/')) return false;

  // No protocol injection
  if (path.includes('://')) return false;

  // No double slashes at start (could be protocol-relative URL)
  if (path.startsWith('//')) return false;

  // No javascript: or data: schemes
  const lowered = path.toLowerCase();
  if (lowered.includes('javascript:') || lowered.includes('data:')) return false;

  return true;
}

/**
 * Validate tilemap data structure for the editor.
 * Returns true if data has the basic structure needed for loading.
 */
export function validateTilemapData(data: unknown): boolean {
  if (!data || typeof data !== 'object') return false;

  const d = data as Record<string, unknown>;

  if (typeof d.width !== 'number' || d.width <= 0) return false;
  if (typeof d.height !== 'number' || d.height <= 0) return false;
  if (typeof d.tileSize !== 'number' || d.tileSize <= 0) return false;
  if (!Array.isArray(d.layers) || d.layers.length === 0) return false;

  // Validate each layer has required properties
  for (const layer of d.layers) {
    if (!layer || typeof layer !== 'object') return false;
    if (typeof layer.id !== 'string') return false;
    if (typeof layer.name !== 'string') return false;
  }

  return true;
}
