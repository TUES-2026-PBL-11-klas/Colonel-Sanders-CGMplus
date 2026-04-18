import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

const API_BASE_URL = Platform.OS === 'android' ? 'http://172.26.128.114:5000' : 'http://localhost:5000'; //your ip, use ip a to find it

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

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle session expiry and refresh
    if (response.status === 401 && !endpoint.includes('/auth/')) {
      const refreshToken = await getRefreshToken();
      if (refreshToken) {
        const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
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
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email.toLowerCase(),
        password: payload.password,
      }),
    });
  }

  static async login(payload: any): Promise<Response> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email.toLowerCase(),
        password: payload.password,
      }),
    });
  }

  static async getMe(): Promise<Response> {
    return this.request('/users/me');
  }

  static async changePassword(payload: any): Promise<Response> {
    return this.request('/users/me/password', {
      method: 'PATCH',
      body: JSON.stringify({
        current_password: payload.current_password,
        new_password: payload.new_password,
      }),
    });
  }

  static async deleteAccount(): Promise<Response> {
    return this.request('/users/me', {
      method: 'DELETE',
    });
  }
}

export { API, setTokens, clearTokens, getAccessToken, getRefreshToken };
