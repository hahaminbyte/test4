import React, { ReactElement, useState } from 'react';
import { Alert, Button } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router';
import { getApiErrorMessage } from '~/utils/getApiErrorMessage';
import {
  connectWallet,
  hasBrowserWallet,
  listInjectedWallets,
  personalSign,
  shortenAddress,
  type EthereumProvider,
} from '~/utils/wallet';
import { useWalletLoginMutation, useWalletNonceMutation } from '~/store';

interface WalletLoginFormProps {
  mode?: 'login' | 'register';
}

/** Browser wallet connect + personal_sign auth (any EIP-1193 wallet; creates account on first use). */
export function WalletLoginForm({ mode = 'login' }: WalletLoginFormProps): ReactElement {
  const [walletNonce] = useWalletNonceMutation();
  const [walletLogin, { isLoading, error }] = useWalletLoginMutation();
  const [localError, setLocalError] = useState<string | null>(null);
  const [connectedAddress, setConnectedAddress] = useState<string | null>(null);
  const [pendingWallet, setPendingWallet] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/';

  const wallets = listInjectedWallets();

  const onConnect = async (provider?: EthereumProvider, walletName?: string) => {
    setLocalError(null);
    setPendingWallet(walletName ?? 'Wallet');
    try {
      if (!hasBrowserWallet()) {
        setLocalError(
          'No browser wallet found. Install MetaMask, Coinbase Wallet, Rabby, Brave Wallet, or another Web3 wallet.',
        );
        return;
      }
      const address = await connectWallet(provider);
      setConnectedAddress(address);
      const challenge = await walletNonce({ address }).unwrap();
      const signature = await personalSign(challenge.address, challenge.message, provider);
      await walletLogin({
        address: challenge.address,
        message: challenge.message,
        signature,
      }).unwrap();
      navigate(from, { replace: true });
    } catch (err) {
      const message =
        err && typeof err === 'object' && 'data' in err
          ? getApiErrorMessage(err, 'Wallet sign-in failed.')
          : err instanceof Error
            ? err.message
            : 'Wallet sign-in failed.';
      if (typeof message === 'string' && /reject|denied|cancel/i.test(message)) {
        setLocalError('Signature request was rejected in your wallet.');
        return;
      }
      setLocalError(message);
    } finally {
      setPendingWallet(null);
    }
  };

  const hint =
    mode === 'register'
      ? 'Connect any browser wallet to create a Haztrak account. First connection registers you automatically.'
      : 'Connect any browser wallet and approve the sign-in message. No blockchain transaction or gas fee.';

  const busy = isLoading || pendingWallet !== null;

  return (
    <div>
      {(localError || error) && (
        <Alert variant="danger">
          {localError || getApiErrorMessage(error, 'Wallet sign-in failed.')}
        </Alert>
      )}
      <p className="text-muted">{hint}</p>
      {connectedAddress ? (
        <p className="small mb-3">
          Connected: <code>{shortenAddress(connectedAddress)}</code>
        </p>
      ) : null}

      {wallets.length > 1 ? (
        <div className="d-grid gap-2">
          {wallets.map((wallet) => (
            <Button
              key={wallet.id}
              type="button"
              variant="primary"
              disabled={busy}
              onClick={() => void onConnect(wallet.provider, wallet.name)}
            >
              {pendingWallet === wallet.name
                ? `Waiting for ${wallet.name}…`
                : mode === 'register'
                  ? `Create account with ${wallet.name}`
                  : `Sign in with ${wallet.name}`}
            </Button>
          ))}
        </div>
      ) : (
        <Button
          type="button"
          variant="primary"
          className="w-100"
          disabled={busy}
          onClick={() => void onConnect(wallets[0]?.provider, wallets[0]?.name)}
        >
          {busy
            ? `Waiting for ${pendingWallet ?? 'wallet'}…`
            : mode === 'register'
              ? 'Create account with wallet'
              : 'Sign in with wallet'}
        </Button>
      )}

      {!hasBrowserWallet() ? (
        <p className="mt-3 mb-0 text-center small text-muted">
          Supported examples:{' '}
          <a href="https://metamask.io/download/" target="_blank" rel="noreferrer">
            MetaMask
          </a>
          {', '}
          <a href="https://www.coinbase.com/wallet" target="_blank" rel="noreferrer">
            Coinbase Wallet
          </a>
          {', '}
          <a href="https://rabby.io/" target="_blank" rel="noreferrer">
            Rabby
          </a>
          {', Brave Wallet, and other EIP-1193 wallets.'}
        </p>
      ) : null}

      <p className="mt-3 mb-0 text-center">
        {mode === 'register' ? (
          <>
            Already have a wallet account? <Link to="/login">Sign in</Link>
          </>
        ) : (
          <>
            New here? <Link to="/register">Register with wallet</Link>
          </>
        )}
      </p>
    </div>
  );
}
