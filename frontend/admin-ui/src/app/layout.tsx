import { Layout, Button } from "antd";
import { Outlet } from "react-router-dom";
import { useAuth } from "../features/auth/auth-context";
import { AppSidebar } from "./sidebar"; 

const { Header, Content } = Layout;

export function AppLayout() {
    const { logout } = useAuth();

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <AppSidebar/>

      <Layout style={{ marginLeft : 220 }}>
        <Header
          style={{
            background: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 24px",
          }}
        >
          <span />
          <h2>Internal Admin System</h2>
          <Button onClick={logout}>Logout</Button>
        </Header>

        <Content style={{ margin: "16px" }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}