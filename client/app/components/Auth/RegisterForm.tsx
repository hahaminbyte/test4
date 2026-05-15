import React, { FormEvent, ReactElement, useState } from 'react';
import { Alert, Button, Form } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router';
import { getApiErrorMessage } from '~/utils/getApiErrorMessage';
import { useRegisterMutation } from '~/store';

export function RegisterForm(): ReactElement {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [register, { isLoading, error }] = useRegisterMutation();
  const navigate = useNavigate();

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await register({ username, email, password, firstName, lastName }).unwrap();
      navigate('/', { replace: true });
    } catch {
      // Error rendered below
    }
  };

  return (
    <Form onSubmit={onSubmit}>
      {error ? (
        <Alert variant="danger">{getApiErrorMessage(error, 'Registration failed.')}</Alert>
      ) : null}
      <Form.Group className="mb-3" controlId="registerUsername">
        <Form.Label>Username</Form.Label>
        <Form.Control
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </Form.Group>
      <Form.Group className="mb-3" controlId="registerEmail">
        <Form.Label>Email</Form.Label>
        <Form.Control
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </Form.Group>
      <Form.Group className="mb-3" controlId="registerFirstName">
        <Form.Label>First name</Form.Label>
        <Form.Control value={firstName} onChange={(e) => setFirstName(e.target.value)} />
      </Form.Group>
      <Form.Group className="mb-3" controlId="registerLastName">
        <Form.Label>Last name</Form.Label>
        <Form.Control value={lastName} onChange={(e) => setLastName(e.target.value)} />
      </Form.Group>
      <Form.Group className="mb-3" controlId="registerPassword">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
        />
      </Form.Group>
      <Button type="submit" variant="primary" className="w-100" disabled={isLoading}>
        {isLoading ? 'Creating account…' : 'Create account'}
      </Button>
      <p className="mt-3 mb-0 text-center">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </Form>
  );
}
