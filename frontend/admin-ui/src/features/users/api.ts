import { api } from "../../lib/api";

export async function fetchUsers(
  params: { 
    limit: number; 
    offset: number; 
    search?: string;
    sort_by?: string;
    sort_order?: string;
    role?: string | undefined;
    is_active?: boolean | undefined; 
  }) {
  const res = await api.get("/users", {
    params,
  });

  return res.data;
}

export async function createUser(data: {
  email: string;
  password: string;
  role: string;
}) {
  const res = await api.post("/users", data);
  return res.data;
}

export async function updateUser(
  userId: string,
  role: string
) {
  const res = await api.patch(`/users/${userId}`, {
    role: role
  });
  return res.data
}
export async function toggleUser(userId: string, isActive: boolean) {
  const res = await api.patch(`/users/${userId}/status`, {
    is_active: isActive,
  });
  return res.data;
}
