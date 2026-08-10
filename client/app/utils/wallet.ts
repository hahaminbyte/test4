/** EIP-1193 injected browser wallet helpers (MetaMask, Coinbase, Rabby, Brave, etc.). */
export interface EthereumProvider {
  request: (args: {
    method: string;
    params?: unknown[] | Record<string, unknown>;
  }) => Promise<unknown>;
  isMetaMask?: boolean;
  isCoinbaseWallet?: boolean;
  isBraveWallet?: boolean;
  isRabby?: boolean;
  isFrame?: boolean;
  isTrust?: boolean;
  isOkxWallet?: boolean;
  providers?: EthereumProvider[];
}

export interface InjectedWallet {
  id: string;
  name: string;
  provider: EthereumProvider;
}

declare global {
  interface Window {
    ethereum?: EthereumProvider;
  }
}

function getInjectedProviders(): EthereumProvider[] {
  if (typeof window === 'undefined' || !window.ethereum) {
    return [];
  }
  const eth = window.ethereum;
  if (Array.isArray(eth.providers) && eth.providers.length > 0) {
    return eth.providers;
  }
  return [eth];
}

function detectWalletName(provider: EthereumProvider): string {
  if (provider.isRabby) return 'Rabby';
  if (provider.isCoinbaseWallet) return 'Coinbase Wallet';
  if (provider.isBraveWallet) return 'Brave Wallet';
  if (provider.isFrame) return 'Frame';
  if (provider.isTrust) return 'Trust Wallet';
  if (provider.isOkxWallet) return 'OKX Wallet';
  if (provider.isMetaMask) return 'MetaMask';
  return 'Browser Wallet';
}

/** List detected EIP-1193 wallets (deduped by name when possible). */
export function listInjectedWallets(): InjectedWallet[] {
  const seen = new Set<string>();
  const wallets: InjectedWallet[] = [];
  getInjectedProviders().forEach((provider, index) => {
    const name = detectWalletName(provider);
    const key = `${name}:${index}`;
    if (seen.has(name) && name !== 'Browser Wallet') {
      return;
    }
    seen.add(name);
    wallets.push({ id: key, name, provider });
  });
  return wallets;
}

export function hasBrowserWallet(): boolean {
  return listInjectedWallets().length > 0;
}

/** @deprecated Use hasBrowserWallet */
export function hasMetaMask(): boolean {
  return hasBrowserWallet();
}

export async function connectWallet(provider?: EthereumProvider): Promise<string> {
  const selected = provider ?? listInjectedWallets()[0]?.provider;
  if (!selected) {
    throw new Error(
      'No browser wallet found. Install MetaMask, Coinbase Wallet, Rabby, Brave Wallet, or another Web3 wallet.',
    );
  }
  const accounts = (await selected.request({
    method: 'eth_requestAccounts',
  })) as string[];
  const address = accounts?.[0];
  if (!address) {
    throw new Error('No wallet account selected.');
  }
  return address;
}

export async function personalSign(
  address: string,
  message: string,
  provider?: EthereumProvider,
): Promise<string> {
  const selected = provider ?? listInjectedWallets()[0]?.provider;
  if (!selected) {
    throw new Error(
      'No browser wallet found. Install a Web3 browser wallet extension to sign in.',
    );
  }
  const signature = (await selected.request({
    method: 'personal_sign',
    params: [message, address],
  })) as string;
  if (!signature) {
    throw new Error('Wallet did not return a signature.');
  }
  return signature;
}

export function shortenAddress(address: string): string {
  if (address.length < 10) return address;
  return `${address.slice(0, 6)}…${address.slice(-4)}`;
}
