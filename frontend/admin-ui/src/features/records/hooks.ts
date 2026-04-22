import { useQuery, useMutation, keepPreviousData } from "@tanstack/react-query";
import { queryClient } from "../../lib/query-client";
import { message } from "antd";

import { 
  fetchRecords, 
  createRecord, 
  updateRecord, 
  changeRecordStatus, 
  assignRecord, 
  deleteRecord 
} from "./api";

export function useRecords(
  page: number,
  pageSize: number,
  search: string,
  sortBy: string,
  sortOrder: string,
  status: string | undefined,
  assignedTo?: string | undefined,
) {
  return useQuery({
    queryKey: ["records", page, pageSize, search, sortBy, sortOrder, status, assignedTo],
    queryFn: () =>
      fetchRecords({
        page,
        limit: pageSize,
        search,
        sort_by: sortBy,
        sort_order: sortOrder,
        status,
        assigned_to: assignedTo,
      }),
    placeholderData: keepPreviousData,
  });
}

export function useCreateRecord() {
  return useMutation({
    mutationFn: createRecord,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
    },
    onError: () => {
      message.error("Failed to create record");
    },
  });
}

export function useUpdateRecord() {
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { title?: string; description?: string } }) =>
      updateRecord(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
    },
    onError: () => {
      message.error("Failed to update record");
    },
  });
}

export function useChangeRecordStatus() {
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      changeRecordStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
      message.success("Status Updated")
    },
    onError: () => {
      message.error("Failed to update record status");
    },
  });
}

export function useAssignRecord() {
  return useMutation({
    mutationFn: ({ id, userId }: { id: string; userId: string | null }) =>
      assignRecord(id, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
      message.success("Assignment Updated")
    },
    onError: () => {
      message.error("Failed to assign record");
    },
  });
}

export function useDeleteRecord() {
  return useMutation({
    mutationFn: deleteRecord,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["records"] });
    },
    onError: () => {
      message.error("Failed to delete record");
    },
  });
}
