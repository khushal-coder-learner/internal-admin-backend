import { Layout, Menu } from "antd";
import {
  DashboardOutlined,
  UserOutlined,
  FileTextOutlined,
  HistoryOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { useLocation, useNavigate } from "react-router-dom";

const { Sider } = Layout;

export function AppSidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    {
      key: "/",
      icon: <DashboardOutlined />,
      label: "Dashboard",
    },
    {
      key: "/users",
      icon: <UserOutlined />,
      label: "Users",
    },
    {
      key: "/records",
      icon: <FileTextOutlined />,
      label: "Records",
    },
    {
      key: "/activity-logs",
      icon: <HistoryOutlined />,
      label: "Activity Logs",
    },
    {
      key: "/jobs",
      icon: <SettingOutlined />,
      label: "Jobs",
    },
  ];

  return (
    <Sider width={220} style={{ background: "#001529", minHeight: "100vh", position: "fixed"}}>
      {/* Logo / Title */}
      <div
        style={{
          color: "white",
          fontSize: 18,
          fontWeight: 600,
          padding: "16px",
        }}
      >
        Admin Panel
      </div>

      {/* Menu */}
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={items}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  );
}