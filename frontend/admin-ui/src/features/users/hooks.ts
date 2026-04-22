import { useQuery, useMutation, keepPreviousData } from "@tanstack/react-query";
import { fetchUsers, createUser, toggleUser, updateUser } from "./api";
import { queryClient } from "../../lib/query-client"
import { message } from "antd";


export function useUsers(
  page: number, 
  pageSize: number, 
  search: string, 
  sortBy: string, 
  sortOrder: string,
  role: string | undefined,
  isActive: boolean | undefined,
  ) {
  return useQuery({
    queryKey: ["users", page, pageSize, search, sortBy, sortOrder, role, isActive],
    queryFn: () =>
      fetchUsers({
        limit: pageSize,
        offset: (page - 1) * pageSize,
        search,
        sort_by: sortBy,
        sort_order: sortOrder,
        role,
        is_active: isActive
      }),
    placeholderData: keepPreviousData, // smooth UX
  });
}

export function useCreateUser() {

  return useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: () => {
      message.error("Failed to create user");
    },
  });
}

export function useToggleUser() {

  return useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      toggleUser(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: () => {
      message.error("Failed to update user");
    },
  });
}

export function useUpdateUser() {

  return useMutation({
    mutationFn: ({id, role}: {id: string, role: string}) =>
      updateUser(id, role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
    onError: () => {
      message.error("Failed to update user");
    },
  });
}
