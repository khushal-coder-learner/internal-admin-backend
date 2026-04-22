// features/activity/hooks.ts

import { useQuery , keepPreviousData } from "@tanstack/react-query";
import { fetchActivityLogs } from "./api";

export function useActivityLogs(
  page: number,
  pageSize: number,
  search: string,
  sortBy: string,
  sortOrder: string,
  action?: string,
  entityType?: string,
  entityId?: string,
  userId?: string
) {
  return useQuery({
    queryKey: [
      "activity",
      page,
      pageSize,
      search,
      sortBy,
      sortOrder,
      action,
      entityType,
      entityId,
      userId,
    ],
    queryFn: () =>
      fetchActivityLogs({
        page,
        limit: pageSize,
        search,
        sort_by: sortBy,
        sort_order: sortOrder,
        action,
        entity_type: entityType,
        entity_id: entityId,
        user_id: userId,
      }),
    placeholderData: keepPreviousData,
  });
}