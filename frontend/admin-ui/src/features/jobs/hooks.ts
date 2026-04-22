import { useQuery, useMutation, keepPreviousData } from "@tanstack/react-query";
import { queryClient } from "../../lib/query-client";
import { fetchJobs, createExportJob, sendAnnouncement } from "./api"
import { message } from "antd";

export function useJobs(
  page: number,
  pageSize: number,
  status?: string,
  jobType?: string,
  sortOrder: string = "desc"
) {
  return useQuery({
    queryKey: ["jobs", page, pageSize, status, jobType, sortOrder],
    queryFn: () =>
      fetchJobs({
        limit: pageSize,
        offset: (page - 1) * pageSize,
        status,
        job_type: jobType,
        sort_order: sortOrder,
      }),
    refetchInterval: 3000,
    placeholderData:keepPreviousData,
  });
}

export function useCreateExport() {

  return useMutation({
    mutationFn: createExportJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
    onError: () => {
      message.error("Failed to start export");
    },
  });
}

export function useSendAnnouncement() {

  return useMutation({
    mutationFn: sendAnnouncement,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
    onError: () => {
      message.error("Failed to send announcement");
    },
  });
}

