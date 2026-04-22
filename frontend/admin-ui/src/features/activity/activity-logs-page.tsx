import { Table, Input, Select } from "antd";
import { useState } from "react";
import { useDebounce } from "../../shared/hooks/use-debounce";
import { useActivityLogs } from "./hooks";

export function isUUID(value: string) {
  return /^[0-9a-fA-F-]{36}$/.test(value);
}

export function ActivityLogsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 400);

  const [action, setAction] = useState<string | undefined>();
  const [entityType, setEntityType] = useState<string | undefined>();
  const [entityId, setEntityId] = useState<string>("");

  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const validEntityId = isUUID(entityId) ? entityId : undefined;

  const { data, isLoading, error } = useActivityLogs(
    page,
    pageSize,
    debouncedSearch,
    sortBy,
    sortOrder,
    action,
    entityType,
    validEntityId
  );
  if (error) return <p>Error loading data</p>;

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
    },
    {
      title: "User",
      dataIndex: "performed_by",
    },
    {
      title: "Action",
      dataIndex: "action",
      render: (action: string) => action.toUpperCase(),
    },
    {
      title: "Entity",
      dataIndex: "entity_type",
    },
    {
      title: "Entity ID",
      dataIndex: "entity_id",
    },
    {
      title: "Created At",
      dataIndex: "created_at",
      sorter: true,
      render: (date: string) =>
        new Date(date).toLocaleString(),
    },
  ];

  return (
    <div>
      <h1>Activity Logs</h1>

      {/* Filters */}
      <div
        style={{
          marginBottom: 16,
          display: "flex",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        {/* Search */}
        <Input
          placeholder="Search..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          style={{ width: 200 }}
        />

        {/* Action */}
        <Select
          placeholder="Action"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => {
            setPage(1);
            setAction(value);
          }}
          options={[
            { value: "create", label: "Create" },
            { value: "update", label: "Update" },
            { value: "delete", label: "Delete" },
            { value: "assign", label: "Assign" },
            { value: "status_change" , label: "Status Change" }
          ]}
        />

        {/* Entity Type */}
        <Select
          placeholder="Entity"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => {
            setPage(1);
            setEntityType(value);
          }}
          options={[
            { value: "user", label: "User" },
            { value: "record", label: "Record" },
            { value: "job", label: "Job" },
          ]}
        />

        {/* Entity ID */}
        <Input
          placeholder="Entity ID"
          value={entityId}
          onChange={(e) => {
            setPage(1);
            setEntityId(e.target.value);
          }}
          style={{ width: 250 }}
        />
      </div>

      {/* Table */}
      <Table
        loading={isLoading}
        dataSource={data?.items || []}
        rowKey="id"
        columns={columns}
        pagination={{
          current: page,
          pageSize,
          total: data?.total || 0,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
        onChange={(pagination, _filters, sorter: any) => {
          // sorting
          if (sorter.field && sorter.order) {
            setSortBy(sorter.field);
            setSortOrder(
              sorter.order === "ascend" ? "asc" : "desc"
            );
            setPage(1);
          } else {
            setSortBy("created_at");
            setSortOrder("desc");
          }

          // pagination sync
          if (pagination.current) setPage(pagination.current);
          if (pagination.pageSize) setPageSize(pagination.pageSize);
        }}
        locale={{ emptyText: "No activity found" }}
      />
    </div>
  );
}
