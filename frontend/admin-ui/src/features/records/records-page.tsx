import { Table , Input, Select, Button, Modal, Form, message } from "antd";
import { useState } from "react";
import { useRecords, useChangeRecordStatus, useCreateRecord, useAssignRecord, useUpdateRecord } from "./hooks";
import { useDebounce } from "../../shared/hooks/use-debounce";
import { useUsers } from "../users/hooks"

export function RecordsPage() {
  const [form] = Form.useForm();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 500);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [status, setStatus] = useState<string | undefined>(undefined);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);

  const { data: usersData, error: usersError } = useUsers(1, 100, "", "created_at", "desc", "", undefined);
  
  const { mutate: changeStatus, isPending: isChangingStatus } = useChangeRecordStatus();
  const { mutate: createRecord, isPending: isCreating } = useCreateRecord();
  const { mutate: assignRecord, isPending: isAssigning } = useAssignRecord();
  const { mutate: updateRecord, isPending: isUpdating } = useUpdateRecord();

  const handleCreate = (values: { title: string; description?: string }) => {
    createRecord(values, {
      onSuccess: () => {
        message.success("Record created successfully");
        setIsModalVisible(false);
        form.resetFields();
      },
    });
  };


  const openRecord = (record: any) => {setSelectedRecord(record)}

  const { data, isLoading, error } = useRecords(page, pageSize, debouncedSearch, sortBy, sortOrder, status);
  if (usersError) return <p>Error loading data</p>;
  if (error) return <p>Error loading data</p>;
  
  const userOptions =
  usersData?.items?.map((u: any) => ({
    value: u.id,
    label: u.email,
  })) || [];

  const columns = [
          {
            title: "ID",
            dataIndex: "id",
          },
          {
            title: "Title",
            dataIndex: "title",
            sorter: true
          },
          {
            title: "Description",
            dataIndex: "description",
            ellipsis: true,
          },
          {
            title: "Status",
            dataIndex: "status",
            render: (status: string) => status?.toUpperCase(),
          },
          {
            title: "Assigned To",
            dataIndex: "assigned_to",
            render: (id?: string) => id || "Unassigned",
          },
          {
            title: "Created By",
            dataIndex: "created_by",
            render: (id?: string) => id || "Unknown",
          },
          {
            title: "Created At",
            dataIndex: "created_at",
            sorter: true,
            render: (date: string) => new Date(date).toLocaleString(),
          },
          {
            title: "Updated At",
            dataIndex: "updated_at",
            sorter: true,
            render: (date: string) => new Date(date).toLocaleString(),
          },
          {
            title: "Actions",
            render: (_: any, record: any) => (
                <Button onClick={() => openRecord(record)}>
                View
                </Button>
            ),
          }
        ]

  // if (error) return <p>Error loading users</p>;

  return (
    <div>
      <h1>Records</h1>

      <div style={{ marginBottom: 16, display: "flex", gap: 12 }}>
        <Input
          placeholder="Search by title"
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          style={{ width: 250 }}
        />

        <Select
          placeholder="Status"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => {
            setPage(1);
            setStatus(value);
          }}
          options={[
            { value: "new", label: "New" },
            { value: "open", label: "Open" },
            { value: "in_progress", label: "In Progress" },
            { value: "closed", label: "Closed" },
          ]}
        />

        <Button type="primary" onClick={() => setIsModalVisible(true)} style={{ marginLeft: "auto" }}>
          Create Record
        </Button>
      </div>

      <Table
        loading={isLoading}
        dataSource={data?.items || []}
        rowKey="id"
        columns={columns}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: data?.total || 0,
          onChange: (newPage, newPageSize) => {
            setPage(newPage);
            setPageSize(newPageSize);
          },
        }}
        onChange={(pagination, _filters, sorter: any) => {
          // 🧠 sorting logic
          if (sorter.field && sorter.order) {
            setSortBy(sorter.field);

            setSortOrder(
              sorter.order === "ascend" ? "asc" : "desc"
            );
            setPage(1);
          } else {
            // reset sorting
            setSortBy("created_at");
            setSortOrder("desc");
          }

          // pagination sync
          if (pagination.current) setPage(pagination.current);
          if (pagination.pageSize) setPageSize(pagination.pageSize);
        }}
        locale={{ emptyText: "No records found" }}
      />

      <Modal
        title="Create New Record"
        open={isModalVisible}
        onOk={() => form.submit()}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={isCreating}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: "Please enter a title" }]}
          >
            <Input placeholder="Enter record title" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Enter description (optional)" />
          </Form.Item>
        </Form>
      </Modal>
      <Modal
        title={`Record #${selectedRecord?.id}`}
        open={!!selectedRecord}
        onCancel={() => setSelectedRecord(null)}
        footer={null}
        >
        {selectedRecord && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {/* Title */}
            <div>
              <strong>Title:</strong>
              <Input
                value={selectedRecord.title}
                disabled={isUpdating}
                style={{ marginTop: 4 }}
                onChange={(e) => {
                  setSelectedRecord({
                    ...selectedRecord,
                    title: e.target.value,
                  });
                }}
                onBlur={() => {
                  updateRecord({
                    id: selectedRecord.id,
                    data: {
                    title: selectedRecord.title,
                    description: selectedRecord.description
                    }
                  });
                }}
              />
            </div>
            {/* Description */}
            <div>
              <strong>Description:</strong>
              <Input.TextArea
                value={selectedRecord.description}
                rows={3}
                disabled={isUpdating}
                style={{ marginTop: 4 }}
                onChange={(e) => {
                  setSelectedRecord({
                    ...selectedRecord,
                    description: e.target.value,
                  });
                }}
                onBlur={() => {
                  updateRecord({
                    id: selectedRecord.id,
                    data: {
                    title: selectedRecord.title,
                    description: selectedRecord.description
                    }
                  });
                }}
              />
            </div>

            {/* Status */}
            <div>
              <strong>Status:</strong>
              <Select
                value={selectedRecord.status}
                loading={isChangingStatus}
                disabled={isChangingStatus}
                style={{ width: "100%", marginTop: 4 }}
                onChange={(status) => {
                  changeStatus(
                    { id: selectedRecord.id, status },
                    {
                      onSuccess: () => {
                        setSelectedRecord((prev: object | undefined) =>
                          prev ? { ...prev, status } : prev
                        );
                      },
                    }
                  );
                }}
                options={[
                  { value: "new", label: "New" },
                  { value: "open", label: "Open" },
                  { value: "in_progress", label: "In Progress" },
                  { value: "closed", label: "Closed" },
                ]}
              />
            </div>

            {/* Assignment */}
            <div>
              <strong>Assigned To:</strong>
              <Select
                value={selectedRecord.assigned_to ?? undefined}
                placeholder="Assign user"
                loading={isAssigning}
                disabled={isAssigning}
                style={{ width: "100%", marginTop: 4 }}
                onChange={(value) => {
                  assignRecord(
                    { id: selectedRecord.id, userId: value ?? null },
                    {
                      onSuccess: () => {
                        setSelectedRecord((prev: object | undefined) =>
                          prev
                            ? { ...prev, assigned_to: value ?? null }
                            : prev
                        );
                      },
                    }
                  );
                }}
                options={userOptions}
                allowClear
              />
            </div>

            </div>
        )}
    </Modal>
    </div>
  );
}
