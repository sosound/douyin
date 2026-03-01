#!/usr/bin/env node
/**
 * 生成「抖音去水印下载」快捷指令（.shortcut）
 * 快捷指令会打开解析页，在解析页粘贴链接即可获取下载地址。
 *
 * 用法：node build-shortcut.js [解析页 URL]
 * 例：  node build-shortcut.js "https://source.galaxystream.online/quick/"
 * 不传参数时使用占位 URL，导入后可手动修改。
 */
const fs = require('fs');
const path = require('path');

const { buildShortcut } = require('@joshfarrant/shortcuts-js');
const { URL, openURLs } = require('@joshfarrant/shortcuts-js/actions');

const PAGE_URL = process.argv[2] || 'https://YOUR_SERVER/quick/';
const OUT_FILE = path.join(__dirname, '抖音去水印下载.shortcut');

const actions = [
  URL({ url: PAGE_URL }),
  openURLs(),
];

const shortcutBuffer = buildShortcut(actions, {
  name: '抖音去水印下载',
  icon: { color: 4274264319, glyph: 59446 },
});

fs.writeFileSync(OUT_FILE, shortcutBuffer);
console.log('已生成:', OUT_FILE);
console.log('解析页 URL:', PAGE_URL);
