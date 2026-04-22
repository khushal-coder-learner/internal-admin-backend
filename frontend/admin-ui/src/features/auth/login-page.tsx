import { Form, Input, Button, Card, Typography, message } from "antd";
import { useState } from "react";
import { useAuth } from "./auth-context";

const { Title } = Typography;

export function LoginPage() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);

  async function handleLogin(values: { email: string; password: string }) {
    if (loading) return;
    try {
      setLoading(true);
      await login(values.email, values.password);
    } catch (err: any) {
      let errorMessage = "Login failed";

      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;

        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          errorMessage = detail[0]?.msg || errorMessage;
        }
      } else if (err?.response?.status === 401) {
        errorMessage = "Invalid email or password";
      } else if (err?.response?.status === 500) {
        errorMessage = "Server error. Try again later.";
      }

      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f5f5f5",
      }}
    >
      <Card style={{ width: 350 }}>
        <Title level={3} style={{ textAlign: "center" }}>
          Login
        </Title>

        <Form layout="vertical" onFinish={handleLogin}>
          <Form.Item
            label="Email"
            name="email"
            rules={[
              { required: true, message: "Please enter your email" },
              { type: "email", message: "Enter a valid email" },
            ]}
          >
            <Input placeholder="Enter email" />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[
              { required: true, message: "Please enter your password" },
            ]}
          >
            <Input.Password placeholder="Enter password" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              disabled={loading}
              block
            >
              Login
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
