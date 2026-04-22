import { Table , Input, Select, Button, Space, Modal, Form, message } from "antd";
import { useState } from "react";
import { useUsers, useToggleUser, useCreateUser } from "./hooks";
import { useDebounce } from "../../shared/hooks/use-debounce";

export function UsersPage() {
  const [form] = Form.useForm();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 400);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [role, setRole] = useState<string | undefined>(undefined);
  const [isActive, setIsActive] = useState<boolean | undefined>(undefined);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const { mutate: toggleUser, isPending: isToggling } = useToggleUser();
  const { mutate: createUser, isPending: isCreating } = useCreateUser();

  const handleCreate = (values: { email: string; password: string; role: string }) => {
    createUser(values, {
      onSuccess: () => {
        message.success("User created successfully");
        setIsModalVisible(false);
        form.resetFields();
      },
    });
  };

  const { data, isLoading, error } = useUsers(page, pageSize, debouncedSearch, sortBy, sortOrder, role, isActive);
  if (error) return <p>Error loading data</p>;
  
  const columns = [
          {
            title: "ID",
            dataIndex: "id",
          },
          {
            title: "Email",
            dataIndex: "email",
            sorter: true
          },
          {
            title: "Role",
            dataIndex: "role",
          },
          {
            title: "Status",
            dataIndex: "is_active",
            render: (isActive: boolean) => (isActive ? "Active" : "Inactive"),
          },
          {
            title: "Actions",
            render: (_: any, user: any) => (
              <Space>
                <Button
                  loading={isToggling}
                  disabled={isToggling}
                  onClick={() =>
                    toggleUser({
                      id: user.id,
                      isActive: !user.is_active,
                    })
                  }
                >
                  Toggle
                </Button>

              </Space>
            ),
          },
        ]

  return (
    <div>
      <h1>Users</h1>

      <div style={{ marginBottom: 16, display: "flex", gap: 12 }}>
        <Input
          placeholder="Search by email"
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          style={{ width: 250 }}
        />

        <Select
          placeholder="Role"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => {
            setPage(1);
            setRole(value);
          }}
          options={[
            { value: "admin", label: "Admin" },
            { value: "staff", label: "Staff" },
          ]}
        />

        <Select
          placeholder="Status"
          allowClear
          style={{ width: 150 }}
          onChange={(value) => {
            setPage(1);
            setIsActive(value);
          }}
          options={[
            { value: true, label: "Active" },
            { value: false, label: "Inactive" },
          ]}
        />

        <Button type="primary" onClick={() => setIsModalVisible(true)} style={{ marginLeft: "auto" }}>
          Create User
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
        locale={{ emptyText: "No users found" }}
      />

      <Modal
        title="Create New User"
        open={isModalVisible}
        onOk={() => form.submit()}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={isCreating}
        destroyOnHidden
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ role: "staff" }}
        >
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { required: true, message: "Please enter an email" },
              { type: "email", message: "Please enter a valid email" },
            ]}
          >
            <Input placeholder="Enter user email" />
          </Form.Item>

          <Form.Item
            name="password"
            label="Password"
            rules={[{ required: true, message: "Please enter a password" }]}
          >
            <Input.Password placeholder="Enter password" />
          </Form.Item>

          <Form.Item
            name="role"
            label="Role"
            rules={[{ required: true, message: "Please select a role" }]}
          >
            <Select
              options={[
                { value: "admin", label: "Admin" },
                { value: "staff", label: "Staff" },
              ]}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
