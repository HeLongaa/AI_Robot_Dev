import express from 'express';
import fs from 'fs';
import path from 'path';
import cors from 'cors';

const app = express();
const port = 3000;

app.use(cors());

const __dirname = path.dirname(new URL(import.meta.url).pathname);

app.get('/api/system-info', (req, res) => {
    fs.readFile(path.join(__dirname, 'System.log'), 'utf-8', (err, data) => {
        if (err) {
            return res.status(500).send('无法读取文件');
        }

        try {
            // 清除多余的转义字符
            const cleanedData = data.replace(/\"/g, '"');

            // 解析清理后的 JSON 数据
            const systemInfo = JSON.parse(cleanedData);

            res.json(systemInfo);
        } catch (error) {
            console.error('JSON 解析失败:', error);
            res.status(500).send('JSON 解析失败');
        }
    });
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
