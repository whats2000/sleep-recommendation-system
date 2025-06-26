/**
 * Main App Component with Routing
 * Symphony AI Sleep Music Recommendation System
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, Layout, Typography, Space } from 'antd';
import { SoundOutlined, GithubOutlined } from '@ant-design/icons';
import { HomePage } from './pages/HomePage';
import { ExperimentSetupPage } from './pages/RecommendationsPage';
import { ABTestPage } from './pages/ABTestPage';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

// Ant Design theme configuration
const theme = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 8,
    fontSize: 16,
  },
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          {/* Header */}
          <Header style={{
            background: '#fff',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <SoundOutlined style={{ fontSize: 24, color: '#1890ff', marginRight: 12 }} />
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Symphony AI
              </Title>
            </div>
            <Text type="secondary">睡眠音樂推薦系統</Text>
          </Header>

          {/* Main Content */}
          <Content style={{
            background: '#f0f2f5',
            minHeight: 'calc(100vh - 134px)'
          }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/experiment-setup" element={<ExperimentSetupPage />} />
              <Route path="/ab-test" element={<ABTestPage />} />
            </Routes>
          </Content>

          {/* Footer */}
          <Footer style={{
            textAlign: 'center',
            background: '#fff',
            borderTop: '1px solid #f0f0f0'
          }}>
            <Space direction="vertical" size="small">
              <Text type="secondary">
                Symphony AI Sleep Music Recommendation System ©2025
              </Text>
              <Space>
                <Text type="secondary">基於 LangGraph 多代理架構</Text>
                <GithubOutlined style={{ color: '#666' }} />
              </Space>
            </Space>
          </Footer>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
