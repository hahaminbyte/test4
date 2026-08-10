import { afterEach, describe, expect, test } from 'vitest';
import { cleanup, renderWithProviders, screen } from '~/mocks';
import { TopNav } from './TopNav';

afterEach(() => {
  cleanup();
});

describe('TopNav', () => {
  test('renders navigation', () => {
    renderWithProviders(<TopNav />);
    expect(screen.getByRole('button', { name: 'toggleSidebarNavigation' })).toBeInTheDocument();
  });
});
