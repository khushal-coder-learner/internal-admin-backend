import axios from "axios";
import {AxiosHeaders} from "axios";
import { getAccessToken, getRefreshToken, setToken, clearToken } from "./token";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    if (!config.headers) {
      config.headers = new AxiosHeaders();
    }

    (config.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
  }
  return config;
});

type QueueItem = {
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
  original: any;
};

let queue: QueueItem[] = [];

let isRefreshing = false;

const refreshClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (!original) {
      return Promise.reject(error);
    }

    const url = String(original?.url ?? "");
    const isAuthEndpoint =
      url.includes("/auth/login") || url.includes("/auth/refresh");

    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ resolve, reject, original });
        });
      }

      original._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) throw new Error("No refresh token");

        const res = await refreshClient.post("/auth/refresh", null, {
          params: { refresh_token: refreshToken },
        });

        setToken(res.data.access_token, res.data.refresh_token);

        const newToken = res.data.access_token;

        queue.forEach(({ resolve, original }) => {
         if (!original.headers || !(original.headers instanceof AxiosHeaders)) {
            original.headers = new AxiosHeaders(original.headers);
          }

          (original.headers as AxiosHeaders).set("Authorization", `Bearer ${newToken}`);
          resolve(api(original));
        });

        queue = [];

        if (!original.headers || !(original.headers instanceof AxiosHeaders)) {
          original.headers = new AxiosHeaders(original.headers);
        }

        (original.headers as AxiosHeaders).set("Authorization", `Bearer ${newToken}`);
        return api(original);
      } catch (err) {
        queue.forEach(({ reject }) => reject(err));
        queue = [];

        clearToken();
        window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
