import { api } from "../../lib/api";

export async function fetchRecords(params: {
  limit: number;
  page: number;
  search?: string;
  status?: string | undefined;
  assigned_to?: string | undefined;
  sort_by?: string;
  sort_order?: string;
}) {
  const res = await api.get("/records", {
    params,
  });

  return res.data;
}

export async function createRecord(data: {
  title: string;
  description?: string;
}) {
  const res = await api.post("/records", data);
  return res.data;
}

export async function updateRecord(
  recordId: string,
  data: {
    title?: string;
    description?: string;
  }
) {
  const res = await api.patch(`/records/${recordId}`, data);
  return res.data;
}

export async function changeRecordStatus(recordId: string, status: string) {
  // Note: Backend uses POST for status transitions to keep logic explicit
  const res = await api.post(`/records/${recordId}/status`, {
    status: status,
  });
  return res.data;
}

export async function assignRecord(recordId: string, userId: string | null) {
  // Note: Payload field 'user_id' matches the RecordAssign schema in backend
  const res = await api.post(`/records/${recordId}/assign`, {
    user_id: userId,
  });
  return res.data;
}

export async function deleteRecord(recordId: string) {
  const res = await api.delete(`/records/${recordId}`);
  return res.data;
}
