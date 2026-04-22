import { api } from "../../lib/api";

export async function fetchJobs(params: {
  limit: number;
  offset: number;
  status?: string;
  job_type?: string;
  sort_order?: string;
}) {
  const res = await api.get("/jobs/me", {params});

  return res.data; // { items, total }
}

export async function createExportJob(exportType: string) {
  const res = await api.post("/jobs/export", null, {
    params: { export_type: exportType },
  });
  return res.data;
}

export async function sendAnnouncement(data: {
  subject: string;
  body: string;
}) {
  const res = await api.post("/jobs/send-announcement", null, {
    params: data,
  });
  return res.data;
}