import React, { ReactElement, useState } from 'react';
import { Alert, Button, Form } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router';
import { getApiErrorMessage } from '~/utils/getApiErrorMessage';
import { useLoginMutation } from '~/store';

/** Local/demo username+password fallback (seeded accounts). */
export function LoginForm(): ReactElement {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [login, { isLoading, error }] = useLoginMutation();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/';

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await login({ username, password }).unwrap();
      navigate(from, { replace: true });
    } catch {
      // Error rendered below
    }
  };

  return (
    <Form onSubmit={(e) => void onSubmit(e)}>
      {error ? <Alert variant="danger">{getApiErrorMessage(error, 'Login failed.')}</Alert> : null}
      <Form.Group className="mb-3" controlId="loginUsername">
        <Form.Label>Username</Form.Label>
        <Form.Control
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </Form.Group>
      <Form.Group className="mb-3" controlId="loginPassword">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </Form.Group>
      <Button type="submit" variant="outline-secondary" className="w-100" disabled={isLoading}>
        {isLoading ? 'Signing in…' : 'Sign in with password'}
      </Button>
    </Form>
  );
}

// history-step 4: Integrated login functionality with API

// history-step 8: Added error handling for authentication
