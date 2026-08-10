import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import React, { createElement } from 'react';
import { afterAll, afterEach, beforeAll, describe, expect, test, vi } from 'vitest';
import { cleanup, renderWithProviders, screen } from '~/mocks';
import { mockUserEndpoints } from '~/mocks/handlers';
import { mockSiteEndpoints } from '~/mocks/handlers/mockSiteEndpoints';
import { Dashboard } from './Dashboard';

const API_BASE_URL = import.meta.env.VITE_HT_API_URL;

const server = setupServer(
  ...mockSiteEndpoints,
  ...mockUserEndpoints,
  http.get(`${API_BASE_URL}/api/dashboard/stats`, () => {
    return HttpResponse.json({
      byStatus: [{ name: 'Pending', value: 2, searchParam: 'pending' }],
      byMonth: [{ date: '2026-01', hazardous: 2, nonHazardous: 0 }],
      generatorStatus: [{ day: 1, haz: 1 }],
      manifestCount: 2,
    });
  })
);

beforeAll(() => {
  vi.mock('recharts', async (importOriginal) => {
    const originalModule = (await importOriginal()) as Record<string, unknown>;
    return {
      ...originalModule,
      ResponsiveContainer: () => createElement('div'),
    };
  });
  server.listen();
});
afterEach(() => {
  server.resetHandlers();
  cleanup();
  vi.resetAllMocks();
});
afterAll(() => server.close());

describe('Home', () => {
  test('renders', async () => {
    renderWithProviders(<Dashboard />);
    await waitFor(() => {
      expect(screen.queryAllByText(/status/i).length).toBeGreaterThanOrEqual(1);
    });
  });
});
