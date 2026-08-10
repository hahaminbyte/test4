import { HaztrakSite } from '~/components/Site';
import { TaskResponse, haztrakApi } from '~/store/htApi.slice';

/** The user data stored in the Redux store */
export interface HaztrakUser {
  id?: string;
  username: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  walletAddress?: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  email: string;
  firstName?: string;
  lastName?: string;
}

export interface WalletNonceRequest {
  address: string;
}

export interface WalletNonceResponse {
  address: string;
  nonce: string;
  message: string;
}

export interface WalletLoginRequest {
  address: string;
  signature: string;
  message: string;
}

export interface AuthSuccessResponse {
  user: HaztrakUser;
  created?: boolean;
}

export interface SessionResponse {
  isAuthenticated: boolean;
  user: HaztrakUser | null;
}

/**The user's RCRAInfo account data stored in the Redux store*/
export interface ProfileSlice {
  user: HaztrakUser;
  rcrainfoProfile?: RcrainfoProfile<Record<string, RcrainfoProfileSite>>;
  sites?: Record<string, HaztrakProfileSite>;
  org?: Organization | null;
  avatar?: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  rcrainfoIntegrated: boolean;
}

/** A site a user has access to in RCRAInfo and their module permissions */
export interface RcrainfoProfileSite {
  epaSiteId: string;
  permissions: RcrainfoSitePermissions;
}

export interface HaztrakProfileSite extends HaztrakSite {
  permissions: HaztrakSitePermissions;
}

export type HaztrakModulePermissions = 'viewer' | 'editor' | 'signer';

export interface HaztrakSitePermissions {
  eManifest: HaztrakModulePermissions;
}

export type RcrainfoProfileState = RcrainfoProfile<Record<string, RcrainfoProfileSite>>;

export interface RcrainfoProfile<T> {
  user: string;
  rcraAPIID?: string;
  rcraUsername?: string;
  rcraAPIKey?: string;
  apiUser?: boolean;
  rcraSites?: T;
  phoneNumber?: string;
  isLoading?: boolean;
  error?: string;
}

export interface RcrainfoSitePermissions {
  siteManagement: boolean;
  annualReport: string;
  biennialReport: string;
  eManifest: string;
  WIETS: string;
  myRCRAid: string;
}

type RcrainfoProfileResponse = RcrainfoProfile<RcrainfoProfileSite[]>;

export const userApi = haztrakApi.injectEndpoints({
  endpoints: (build) => ({
    login: build.mutation<AuthSuccessResponse, LoginRequest>({
      query: (data) => ({
        url: 'auth/login',
        method: 'POST',
        data,
      }),
      invalidatesTags: ['user', 'auth', 'profile'],
    }),
    walletNonce: build.mutation<WalletNonceResponse, WalletNonceRequest>({
      query: (data) => ({
        url: 'auth/wallet/nonce',
        method: 'POST',
        data,
      }),
    }),
    walletLogin: build.mutation<AuthSuccessResponse, WalletLoginRequest>({
      query: (data) => ({
        url: 'auth/wallet/login',
        method: 'POST',
        data,
      }),
      invalidatesTags: ['user', 'auth', 'profile'],
    }),
    register: build.mutation<AuthSuccessResponse, RegisterRequest>({
      query: (data) => ({
        url: 'auth/register',
        method: 'POST',
        data,
      }),
      invalidatesTags: ['user', 'auth', 'profile'],
    }),
    logout: build.mutation<void, void>({
      query: () => ({
        url: 'auth/logout',
        method: 'POST',
      }),
      invalidatesTags: ['user', 'auth', 'profile', 'org', 'site'],
    }),
    getSession: build.query<SessionResponse, void>({
      query: () => ({
        url: 'auth/session',
        method: 'GET',
      }),
      providesTags: ['auth'],
    }),
    getCurrentUser: build.query<HaztrakUser, void>({
      query: () => ({
        url: 'user/current-user',
        method: 'GET',
      }),
      providesTags: ['user'],
    }),
    updateUser: build.mutation<HaztrakUser, HaztrakUser>({
      query: (data) => ({
        url: 'user/current-user/update',
        method: 'PUT',
        data,
      }),
      invalidatesTags: ['user'],
    }),
    updateProfile: build.mutation<ProfileSlice, { id: string; profile: Partial<ProfileSlice> }>({
      query: ({ id, profile }) => ({
        url: `profile/${id}`,
        method: 'PATCH',
        data: profile,
      }),
      invalidatesTags: ['profile'],
    }),
    updateAvatar: build.mutation<{ avatar: string }, { id: string; avatar: FormData }>({
      query: ({ id, avatar }) => ({
        url: `profile/${id}`,
        method: 'PATCH',
        data: avatar,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }),
      invalidatesTags: ['profile'],
    }),
    getProfile: build.query<ProfileSlice, void>({
      query: () => ({
        url: 'my-profile',
        method: 'GET',
      }),
      providesTags: ['profile'],
    }),
    getRcrainfoProfile: build.query<RcrainfoProfileState, string>({
      query: (username) => ({
        url: `rcrainfo-profile/${username}`,
        method: 'GET',
      }),
      providesTags: ['rcrainfoProfile'],
      transformResponse: (response: RcrainfoProfileResponse) => {
        const rcraSites = response?.rcraSites;
        return {
          ...response,
          rcraSites: rcraSites?.reduce((obj, site) => {
            return {
              ...obj,
              [site.epaSiteId]: { epaSiteId: site.epaSiteId, permissions: site.permissions },
            };
          }, {}),
        };
      },
    }),
    updateRcrainfoProfile: build.mutation<unknown, { username: string; data: unknown }>({
      query: (data) => ({
        url: `rcrainfo-profile/${data.username}`,
        method: 'PUT',
        data: data.data,
      }),
      invalidatesTags: ['rcrainfoProfile'],
    }),
    syncRcrainfoProfile: build.mutation<TaskResponse, void>({
      query: () => ({
        url: `rcrainfo-profile/sync`,
        method: 'POST',
      }),
      invalidatesTags: ['rcrainfoProfile'],
    }),
  }),
});
