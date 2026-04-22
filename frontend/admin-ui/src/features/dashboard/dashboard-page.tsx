import { useUsers } from "../users/hooks";
import { useRecords } from "../records/hooks";
import { useJobs } from "../jobs/hooks";
import { useActivityLogs } from "../activity/hooks";

import { Button, Card, Table, Tag } from "antd";
import { useNavigate } from "react-router-dom";

type PaginatedResult<TItem> = {
  items: TItem[];
  total: number;
};

type MaybePaginatedResult<TItem> = PaginatedResult<TItem> | undefined;

type JobListItem = {
  id: string;
  type: string;
  status: string;
};

type ActivityListItem = {
  id: string;
  action: string;
  entity_type: string;
  created_at: string;
};

function Stats(props: {
  usersData: MaybePaginatedResult<unknown>;
  recordsData: MaybePaginatedResult<unknown>;
  jobsData: MaybePaginatedResult<unknown>;
}) {
  const { usersData, recordsData, jobsData } = props;

  return (
    <div style={{ display: "flex", gap: 16 }}>
      <Card title="Users" style={{ flex: 1 }}>
        {usersData?.total ?? 0}
      </Card>

      <Card title="Records" style={{ flex: 1 }}>
        {recordsData?.total ?? 0}
      </Card>

      <Card title="Jobs" style={{ flex: 1 }}>
        {jobsData?.total ?? 0}
      </Card>
    </div>
  );
}

function RecentActivity(props: { data: MaybePaginatedResult<ActivityListItem> }) {
  const { data } = props;

  return (
    <Table
      size="small"
      dataSource={data?.items ?? []}
      rowKey="id"
      pagination={false}
      columns={[
        { title: "Action", dataIndex: "action" },
        { title: "Entity", dataIndex: "entity_type" },
        {
          title: "Time",
          dataIndex: "created_at",
          render: (d: string) => new Date(d).toLocaleString(),
        },
      ]}
    />
  );
}

function RecentJobs(props: { data: MaybePaginatedResult<JobListItem> }) {
  const { data } = props;

  return (
    <Table
      size="small"
      dataSource={data?.items ?? []}
      rowKey="id"
      pagination={false}
      columns={[
        { title: "Type", dataIndex: "type" },
        {
          title: "Status",
          dataIndex: "status",
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
      ]}
    />
  );
}

function QuickActions() {
  const navigate = useNavigate();

  return (
    <div style={{ display: "flex", gap: 12 }}>
      <Button type="primary" onClick={() => navigate("/jobs")}>
        Go to Jobs
      </Button>

      <Button onClick={() => navigate("/users")}>Manage Users</Button>

      <Button onClick={() => navigate("/records")}>Manage Records</Button>
    </div>
  );
}

export function DashboardPage() {
  const { data: usersData, error: usersError } = useUsers(1, 1, "", "created_at", "desc", "staff", undefined);
  const { data: recordsData, error: recordsError } = useRecords(
    1,
    1,
    "",
    "created_at",
    "desc",
    undefined,
    undefined
  );
  const { data: jobsData, error: jobsError } = useJobs(1, 5);
  const { data: activityData, error: activityError } = useActivityLogs(1, 5, "", "created_at", "desc");

  if (usersError || recordsError || jobsError || activityError) return <p>Error loading data</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h1>Dashboard</h1>

      <Stats usersData={usersData} recordsData={recordsData} jobsData={jobsData} />

      <div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ flex: 1, minWidth: 320 }}>
          <h3>Recent Activity</h3>
          <RecentActivity data={activityData} />
        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <h3>Recent Jobs</h3>
          <RecentJobs data={jobsData as MaybePaginatedResult<JobListItem>} />
        </div>
      </div>

      <QuickActions />
    </div>
  );
}
