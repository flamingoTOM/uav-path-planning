import React from 'react';
import { Empty } from 'antd';
import { AppstoreAddOutlined } from '@ant-design/icons';

interface ReservedPanelProps {
  title: string;
}

const ReservedPanel: React.FC<ReservedPanelProps> = ({ title }) => {
  return (
    <div className="panel-container">
      <div className="panel-header">
        <h3>
          <AppstoreAddOutlined style={{ marginRight: 8 }} />
          {title}
        </h3>
      </div>
      <div className="panel-content">
        <div className="empty-panel">
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="Reserved area for future features"
          />
        </div>
      </div>
    </div>
  );
};

export default ReservedPanel;
