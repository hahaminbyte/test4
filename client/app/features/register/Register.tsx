import React, { ReactElement, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { useNavigate } from 'react-router';
import { WalletLoginForm } from '~/components/Auth';
import { useTitle } from '~/hooks';
import { useGetSessionQuery } from '~/store';
import logo from '/assets/img/haztrak-logos/haztrak-logo-zip-file/svg/logo-no-background.svg';

export function Register(): ReactElement {
  useTitle('Register');
  const navigate = useNavigate();
  const { data } = useGetSessionQuery();

  useEffect(() => {
    if (data?.isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [data, navigate]);

  return (
    <Container className="d-flex flex-column align-items-center justify-content-center min-vh-100 py-5">
      <img src={logo} alt="Haztrak" width={180} className="mb-4" />
      <div className="w-100" style={{ maxWidth: 420 }}>
        <h1 className="h3 mb-3 text-start">Create an account</h1>
        <WalletLoginForm mode="register" />
      </div>
    </Container>
  );
}

export { Register as Component };
export default Register;
