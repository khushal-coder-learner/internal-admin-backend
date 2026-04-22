import { api } from "../../lib/api";

export async function fetchActivityLogs(params: {
  page: number;
  limit: number;
  search?: string;
  action?: string;
  entity_type?: string;
  entity_id?: string,
  user_id?: string;
  sort_by?: string;
  sort_order?: string;
}) {
  const res = await api.get("/activity-logs", {
    params,
  });

  return res.data; // { items, total }
}