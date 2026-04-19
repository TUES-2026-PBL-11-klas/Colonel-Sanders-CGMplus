import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const API_HOST = process.env.EXPO_PUBLIC_API_HOST || '192.168.1.109';
const API_PORT = process.env.EXPO_PUBLIC_API_PORT || '5000';
const API_PREFIX_RAW = process.env.EXPO_PUBLIC_API_PREFIX || '/api/v1';
const API_PREFIX = API_PREFIX_RAW.startsWith('/') ? API_PREFIX_RAW : `/${API_PREFIX_RAW}`;
const AUTH_BASE_PATH = `${API_PREFIX}/auth`;
const USERS_BASE_PATH = `${API_PREFIX}/users`;
const PROFILE_BASE_PATH = `${API_PREFIX}/profile`;
const OFFERS_BASE_PATH = `${API_PREFIX}/offers`;
const API_BASE_URL = (API_PORT === '80' || API_PORT === '443') 
  ? `http://${API_HOST}` 
  : `http://${API_HOST}:${API_PORT}`;

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserMeResponse {
  email: string;
}

const getAccessToken = async () => await SecureStore.getItemAsync('access_token');
const getRefreshToken = async () => await SecureStore.getItemAsync('refresh_token');

const setTokens = async (accessToken: string, refreshToken: string) => {
  await SecureStore.setItemAsync('access_token', accessToken);
  await SecureStore.setItemAsync('refresh_token', refreshToken);
};

const clearTokens = async () => {
  await SecureStore.deleteItemAsync('access_token');
  await SecureStore.deleteItemAsync('refresh_token');
};

class API {
  private static async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const accessToken = await getAccessToken();
    const headers = {
      'Content-Type': 'application/json',
      ...((options.headers as any) || {}),
    };

    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const fullUrl = `${API_BASE_URL}${endpoint}`;
    console.log(`[API] ${options.method || 'GET'} ${fullUrl}`);

    const response = await fetch(fullUrl, {
      ...options,
      headers,
    });

    console.log(`[API] Response: ${response.status} ${response.statusText}`);

    // Handle session expiry and refresh
    if (response.status === 401 && !endpoint.includes(`${AUTH_BASE_PATH}/`)) {
      const refreshToken = await getRefreshToken();
      if (refreshToken) {
        const refreshResponse = await fetch(`${API_BASE_URL}${AUTH_BASE_PATH}/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshResponse.ok) {
          const data: AuthResponse = await refreshResponse.json();
          await setTokens(data.access_token, data.refresh_token);

          // Retry original request with new token
          headers['Authorization'] = `Bearer ${data.access_token}`;
          return fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
          });
        } else {
          await clearTokens();
          // Let the calling context handle the logout (e.g. redirect to login)
        }
      }
    }

    return response;
  }

  static async register(payload: any): Promise<Response> {
    return this.request(`${AUTH_BASE_PATH}/register`, {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email.toLowerCase(),
        password: payload.password,
      }),
    });
  }

  static async login(payload: any): Promise<Response> {
    return this.request(`${AUTH_BASE_PATH}/login`, {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email.toLowerCase(),
        password: payload.password,
      }),
    });
  }

  static async getMe(): Promise<Response> {
    return this.request(`${USERS_BASE_PATH}/me`);
  }

  static async changePassword(payload: any): Promise<Response> {
    return this.request(`${USERS_BASE_PATH}/me/password`, {
      method: 'PATCH',
      body: JSON.stringify({
        current_password: payload.current_password,
        new_password: payload.new_password,
      }),
    });
  }

  static async deleteAccount(): Promise<Response> {
    return this.request(`${USERS_BASE_PATH}/me`, {
      method: 'DELETE',
    });
  }

  // Loyalty & Wallet endpoints
  static async getProfileSummary(): Promise<Response> {
    return this.request(`${PROFILE_BASE_PATH}/me`);
  }

  static async getCardDetails(): Promise<Response> {
    return this.request(`${PROFILE_BASE_PATH}/card`);
  }

  static async getActiveOffers(): Promise<Response> {
    return this.request(`${OFFERS_BASE_PATH}/`);
  }

  static async redeemOffer(offerId: number): Promise<Response> {
    return this.request(`${OFFERS_BASE_PATH}/${offerId}/redemption`, {
      method: 'POST',
    });
  }

  static async getRedemptionHistory(): Promise<Response> {
    return this.request(`${OFFERS_BASE_PATH}/redemptions`);
  }
}

export { API, setTokens, clearTokens, getAccessToken, getRefreshToken };
