import { Table, Button, Tag, Select, Progress, Modal, Form, Input } from "antd";
import { useState } from "react";
import { useJobs, useCreateExport, useSendAnnouncement } from "./hooks";

export function JobsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const [status, setStatus] = useState<string | undefined>();
  const [jobType, setJobType] = useState<string | undefined>();
  const [exportType, setExportType] = useState("users");
  const [sortOrder, setSortOrder] = useState("desc");

  const { data, isLoading, error } = useJobs(
    page,
    pageSize,
    status,
    jobType,
    sortOrder
  );

  const { mutate: createExport, isPending: creating } =
    useCreateExport();

  const [open, setOpen] = useState(false);
  const [form] = Form.useForm();

  const { mutate: sendAnnouncement, isPending: sendingAnnouncement } =
    useSendAnnouncement();

  if (error) return <p>Error loading data</p>;

  const columns = [
    {
      title: "ID",
      dataIndex: "id",
      width: 360,
    },
    {
      title: "Type",
      dataIndex: "type",
    },
    {
      title: "Status",
      dataIndex: "status",
      sorter: true,
      render: (status: string) => {
        const color =
          status === "completed"
            ? "green"
            : status === "failed"
            ? "red"
            : status === "processing"
            ? "blue"
            : "default";

        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: "Progress",
      width: 220,
      render: (_: any, record: any) => {
        if (record.payload?.progress != null) {
          const percent = Number(record.payload.progress);
          const safePercent = Number.isFinite(percent) ? percent : 0;
          const rowsProcessed = record.payload.rows_processed;
          const totalRows = record.payload.total_rows;

          const bulkProcessed = record.payload.processed_recipients;
          const bulkTotal = record.payload.total_recipients;

          const format = () => {
            if (
              rowsProcessed != null &&
              totalRows != null &&
              Number(totalRows) >= 0
            ) {
              return `${safePercent}% (${rowsProcessed}/${totalRows})`;
            }

            if (
              bulkProcessed != null &&
              bulkTotal != null &&
              Number(bulkTotal) >= 0
            ) {
              return `${safePercent}% (${bulkProcessed}/${bulkTotal})`;
            }

            return `${safePercent}%`;
          };

          return (
            <div>
            <Progress
              percent={safePercent}
              size="small"
            />
            <div style={{ fontSize: 12, marginTop: 4 , color: "green"}}>
            {format()}
            </div>
            </div>
          );
        }

        // fallback
        if (record.status === "completed") return "Done";
        if (record.status === "failed") return "Failed";

        return "—";
      },
    },
    {
      title: "Created",
      dataIndex: "created_at",
      sorter: true,
      render: (d: string) => new Date(d).toLocaleString(),
    },
    {
      title: "Actions",
      width: 140,
      render: (_: any, record: any) => {
        if (record.status === "completed" && record.download_url) {
          return (
            <Button
              type="link"
              onClick={() => {
                const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

                const url = record.download_url.startsWith("http")
                  ? record.download_url
                  : `${base}${record.download_url}`;

                window.open(url, "_blank");}}
            >
              Download
            </Button>
          );
        }

        return "—";
      },
    },
  ];

  return (
    <div>
      <h1>Jobs</h1>

      {/* Actions + Filters */}
      <div
        style={{
          marginBottom: 16,
          display: "flex",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        {/* Create job */}

        <div style={{ display: "flex", gap: 12 }}>
          <Select
            value={exportType}
            style={{ width: 200 }}
            onChange={(value) => setExportType(value)}
            options={[
              { value: "users", label: "Users" },
              { value: "records", label: "Records" },
              { value: "activity_logs", label: "Activity Logs" },
            ]}
          />

          <Button
            type="primary"
            loading={creating}
            disabled={creating}
            onClick={() => {
              if (creating) return;
              createExport(exportType);
            }}
          >
            Export
          </Button>
        </div>

        <Button type="primary" onClick={() => setOpen(true)}>
          Send Announcement
        </Button>

        {/* Status filter */}
        <Select
          placeholder="Status"
          allowClear
          style={{ width: 160 }}
          onChange={(value) => {
            setPage(1);
            setStatus(value);
          }}
          options={[
            { value: "pending", label: "Pending" },
            { value: "processing", label: "Processing" },
            { value: "completed", label: "Completed" },
            { value: "failed", label: "Failed" },
          ]}
        />

        {/* Job type filter */}
        <Select
          placeholder="Job Type"
          allowClear
          style={{ width: 200 }}
          onChange={(value) => {
            setPage(1);
            setJobType(value);
          }}
          options={[
            { value: "export", label: "Export" },
            { value: "send_email", label: "Send Email" },
            {
              value: "bulk_user_email_dispatch",
              label: "Bulk Email",
            },
          ]}
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
          if (sorter.order) {
            setSortOrder(
              sorter.order === "ascend" ? "asc" : "desc"
            );
            setPage(1);
          } else {
            setSortOrder("desc");
          }

          if (pagination.current) setPage(pagination.current);
          if (pagination.pageSize) setPageSize(pagination.pageSize);
        }}
        locale={{ emptyText: "No jobs found" }}
      />

      <Modal
        title="Send Announcement"
        open={open}
        onCancel={() => setOpen(false)}
        onOk={() => {
          if (sendingAnnouncement) return;
          form.validateFields().then((values) => {
            sendAnnouncement(values);
            setOpen(false);
            form.resetFields();
          });
        }}
        confirmLoading={sendingAnnouncement}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="subject"
            label="Subject"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="body"
            label="Message"
            rules={[{ required: true }]}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
