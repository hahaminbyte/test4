import { http, HttpResponse } from 'msw';
import { createMockHaztrakUser } from '~/mocks/fixtures';
import {
  createMockProfileResponse,
  createMockRcrainfoProfileResponse,
  createMockServerTask,
} from '~/mocks/fixtures/mockUser';
import { HaztrakUser } from '~/store/userApi/userApi';

/** mock Rest API*/
const API_BASE_URL = import.meta.env.VITE_HT_API_URL;
export const mockUserEndpoints = [
  /** GET User */
  http.get(`${API_BASE_URL}/api/user/current-user`, () => {
    return HttpResponse.json({ ...createMockHaztrakUser() }, { status: 200 });
  }),
  /** Update User */
  http.put(`${API_BASE_URL}/api/user/current-user/update`, (info) => {
    const user: HaztrakUser = { ...createMockHaztrakUser() };
    return HttpResponse.json({ ...user, ...info.request.body }, { status: 200 });
  }),
  /** Auth session */
  http.get(`${API_BASE_URL}/api/auth/session`, () => {
    return HttpResponse.json(
      { isAuthenticated: true, user: createMockHaztrakUser() },
      { status: 200 }
    );
  }),
  http.post(`${API_BASE_URL}/api/auth/login`, () => {
    return HttpResponse.json({ user: createMockHaztrakUser() }, { status: 200 });
  }),
  http.post(`${API_BASE_URL}/api/auth/register`, () => {
    return HttpResponse.json({ user: createMockHaztrakUser() }, { status: 201 });
  }),
  http.post(`${API_BASE_URL}/api/auth/logout`, () => {
    return new HttpResponse(null, { status: 204 });
  }),
  /** GET Profile */
  http.get(`${API_BASE_URL}/api/my-profile`, () => {
    return HttpResponse.json({ ...createMockProfileResponse() }, { status: 200 });
  }),
  /** GET RCRAInfo profile */
  http.get(`${API_BASE_URL}/api/rcrainfo-profile/:username`, (info) => {
    const { username } = info.params;
    if (typeof username !== 'string') {
      return HttpResponse.json({}, { status: 404 });
    }
    const rcrainfoProfile = createMockRcrainfoProfileResponse({ user: username });
    return HttpResponse.json(
      {
        ...rcrainfoProfile,
      },
      { status: 200 }
    );
  }),
  /** POST RCRAInfo profile Sync*/
  http.post(`${API_BASE_URL}/api/rcrainfo-profile/sync`, () => {
    const mockTask = createMockServerTask();
    return HttpResponse.json(
      {
        ...mockTask,
      },
      { status: 200 }
    );
  }),
  /** PUT RCRAInfo profile */
  http.put(`${API_BASE_URL}/api/rcrainfo-profile/:username`, (info) => {
    const { username } = info.params;
    if (typeof username !== 'string') {
      return HttpResponse.json({}, { status: 404 });
    }
    const rcrainfoProfile = createMockRcrainfoProfileResponse({
      user: username,
      ...info.request.body,
    });
    return HttpResponse.json(
      {
        ...rcrainfoProfile,
      },
      { status: 200 }
    );
  }),
];
