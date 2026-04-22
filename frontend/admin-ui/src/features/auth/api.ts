import { api } from "../../lib/api";

export async function loginRequest(email: string, password: string) {
  const res = await api.post("/auth/login", {
    email,
    password,
  });

  return res.data; // { access_token, refresh_token }
}