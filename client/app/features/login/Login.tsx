import React, { ReactElement, useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { LoginForm, WalletLoginForm } from '~/components/Auth';
import { useTitle } from '~/hooks';
import { useGetSessionQuery } from '~/store';
import logo from '/assets/img/haztrak-logos/haztrak-logo-zip-file/svg/logo-no-background.svg';

export function Login(): ReactElement {
  useTitle('Sign in');
  const navigate = useNavigate();
  const { data } = useGetSessionQuery();
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (data?.isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [data, navigate]);

  return (
    <Container className="d-flex flex-column align-items-center justify-content-center min-vh-100">
      <img src={logo} alt="Haztrak" width={180} className="mb-4" />
      <div className="w-100" style={{ maxWidth: 420 }}>
        <h1 className="h3 mb-3 text-start">Sign in</h1>
        <WalletLoginForm mode="login" />
        <hr className="my-4" />
        <button
          type="button"
          className="btn btn-link btn-sm p-0"
          onClick={() => setShowPassword((v) => !v)}
        >
          {showPassword ? 'Hide password sign-in' : 'Local demo: sign in with password'}
        </button>
        {showPassword ? (
          <div className="mt-3">
            <LoginForm />
          </div>
        ) : null}
      </div>
    </Container>
  );
}

export { Login as Component };
export default Login;
