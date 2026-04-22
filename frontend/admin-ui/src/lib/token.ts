export function setToken(access: string, refresh: string) {
  sessionStorage.setItem("access_token", access);
  sessionStorage.setItem("refresh_token", refresh);
}

export function getAccessToken() {
  return sessionStorage.getItem("access_token");
}

export function getRefreshToken() {
  return sessionStorage.getItem("refresh_token");
}

export function clearToken() {
  sessionStorage.removeItem("access_token");
  sessionStorage.removeItem("refresh_token");
}