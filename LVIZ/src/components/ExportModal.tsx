/**
 * ExportModal — 图像导出对话框
 * 支持导出主视图 / 俯视图 / 飞行剖面为 PNG / JPEG / WebP
 */
import React, { useState } from 'react';
import {
  Modal, Form, Select, Slider, Radio, Button, Divider,
  Typography, Space, message, Row, Col,
} from 'antd';
import { DownloadOutlined, PictureOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface ExportModalProps {
  open: boolean;
  onClose: () => void;
}

interface ExportSource {
  label: string;
  canvasId: string;
  hint?: string;
}

const SOURCES: ExportSource[] = [
  { label: '主视图', canvasId: 'main-display-canvas', hint: '含地形、路径、多边形叠加层' },
  { label: '俯视图', canvasId: 'topview-canvas',      hint: '等高线地形俯视图' },
  { label: '飞行剖面', canvasId: 'profile-canvas',   hint: '高度-距离折线图' },
];

const FORMATS = [
  { label: 'PNG（无损，透明支持）', value: 'png' },
  { label: 'JPEG（有损，体积小）',  value: 'jpeg' },
  { label: 'WebP（有损/无损）',     value: 'webp' },
];

function getTimestamp() {
  const d = new Date();
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0'),
    '_',
    String(d.getHours()).padStart(2, '0'),
    String(d.getMinutes()).padStart(2, '0'),
  ].join('');
}

const ExportModal: React.FC<ExportModalProps> = ({ open, onClose }) => {
  const [format, setFormat] = useState<'png' | 'jpeg' | 'webp'>('png');
  const [quality, setQuality] = useState(92);
  const [source, setSource] = useState('main-display-canvas');
  const [exporting, setExporting] = useState(false);

  const handleExport = () => {
    setExporting(true);
    try {
      const canvas = document.getElementById(source) as HTMLCanvasElement | null;
      if (!canvas || canvas.tagName !== 'CANVAS') {
        message.warning('未找到画布，请确认对应视图已加载数据');
        return;
      }

      const mime = `image/${format}`;
      const q = format === 'png' ? undefined : quality / 100;
      const dataUrl = canvas.toDataURL(mime, q);

      const srcInfo = SOURCES.find(s => s.canvasId === source);
      const ext = format === 'jpeg' ? 'jpg' : format;
      const filename = `LVIZ_${srcInfo?.label ?? 'export'}_${getTimestamp()}.${ext}`;

      const a = document.createElement('a');
      a.download = filename;
      a.href = dataUrl;
      a.click();

      message.success(`已导出：${filename}`);
      onClose();
    } catch (e: any) {
      message.error(`导出失败：${e.message}`);
    } finally {
      setExporting(false);
    }
  };

  const srcInfo = SOURCES.find(s => s.canvasId === source);

  return (
    <Modal
      title={<><PictureOutlined style={{ marginRight: 8 }} />导出图像</>}
      open={open}
      onCancel={onClose}
      footer={null}
      width={440}
    >
      <Form layout="vertical" size="small">

        {/* 导出来源 */}
        <Form.Item label="导出视图" style={{ marginBottom: 12 }}>
          <Radio.Group
            value={source}
            onChange={e => setSource(e.target.value)}
            style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}
          >
            {SOURCES.map(s => (
              <Radio.Button key={s.canvasId} value={s.canvasId} style={{ flex: 1 }}>
                {s.label}
              </Radio.Button>
            ))}
          </Radio.Group>
          {srcInfo?.hint && (
            <Text type="secondary" style={{ fontSize: 11, marginTop: 4, display: 'block' }}>
              {srcInfo.hint}
            </Text>
          )}
        </Form.Item>

        {/* 格式 */}
        <Form.Item label="文件格式" style={{ marginBottom: 12 }}>
          <Select
            value={format}
            onChange={v => setFormat(v as typeof format)}
            options={FORMATS}
            style={{ width: '100%' }}
          />
        </Form.Item>

        {/* 质量（仅 JPEG / WebP） */}
        {format !== 'png' && (
          <Form.Item
            label={
              <Space>
                <span>图像质量</span>
                <Text code style={{ fontSize: 11 }}>{quality}%</Text>
              </Space>
            }
            style={{ marginBottom: 12 }}
          >
            <Slider
              min={50} max={100} step={2}
              value={quality}
              onChange={setQuality}
              marks={{ 50: '50%', 75: '75%', 92: '92%', 100: '100%' }}
            />
          </Form.Item>
        )}

        <Divider style={{ margin: '8px 0 12px' }} />

        {/* 文件名预览 */}
        <Row align="middle" style={{ marginBottom: 12 }}>
          <Col flex="auto">
            <Text type="secondary" style={{ fontSize: 11 }}>
              文件名：LVIZ_{srcInfo?.label}_{getTimestamp()}.{format === 'jpeg' ? 'jpg' : format}
            </Text>
          </Col>
        </Row>

        {/* 操作按钮 */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <Button onClick={onClose}>取消</Button>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExport}
            loading={exporting}
          >
            导出
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

export default ExportModal;
