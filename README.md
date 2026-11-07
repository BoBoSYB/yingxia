# 映匣 Yingxia 订阅

给 [映匣（Yingxia / tvbox-silicon）](https://github.com/jo32/tvbox-silicon) 用的 TVBox 订阅。
映匣 是原生 SwiftUI + AVPlayer 的播放器：**只吃标准 CMS 直连（`type:1`）、M3U/TXT 直播播单，
不跑 QuickJS / Spider.js**，Java 插件靠 dex2jar 转换。所以这份订阅刻意做到：

- 全部点播源都是 `type:1` 苹果CMS 标准接口，返回 m3u8，AVPlayer 直接能播
- `spider` 字段留空 —— 不依赖任何 jar
- 没有任何 `127.0.0.1:9978` 本地代理依赖（那是 TVBox 安卓端才有的）
- 不塞解析嗅探（`parses`），因为映匣不走那套

## 导入地址

仓库开 GitHub Pages 后，在 映匣 的 `设置 → Subscriptions → Add` 里填：

```
https://<你的用户名>.github.io/yingxia/yingxia-sub.json
```

备用（raw 直链，国内经常连不上）：

```
https://raw.githubusercontent.com/<你的用户名>/yingxia/main/yingxia-sub.json
```

GitHub Pages 走 CDN，比 `raw.githubusercontent.com` 在国内稳得多，优先用 Pages 那个。
`github://Token@github.com/...` 这种写法只用于私有仓库，公开仓库直接填 https 即可。

## 自动测活

`.github/workflows/liveness-check.yml` 每天早上 08:00（北京时）跑一次 `build.py`：

- 点播：请求 `<api>?ac=list&pg=1`，要求返回 JSON 且 `code == 1`
- 直播：拉播单，首行要以 `#EXTM3U` 开头
- **连挂 2 次才摘掉**（记在 `state.json`），避免 GitHub 美国节点遇到区域性屏蔽时误杀只服务国内的源
- 有变化就自动 commit 回 `yingxia-sub.json`

想加源自已：编辑 `sources.json` 推上去，工作流会在 `push` 时立刻重跑。

## 源清单（2026-11-07 22:50–23:00 实测，均为 code:1）

| 源 | 接口 | 量 |
|---|---|---|
| 暴风 | `bfzyapi.com/api.php/provide/vod/` | 17.1 万 |
| 量子 | `cj.lziapi.com/api.php/provide/vod/` | 16.2 万 |
| 光速 | `api.guangsuapi.com/api.php/provide/vod/` | 11.7 万 |
| 红牛 | `www.hongniuzy2.com/api.php/provide/vod/` | 11.7 万 |
| 极速 | `jszyapi.com/api.php/provide/vod/` | 11.6 万 |
| 非凡 | `ffzy.tv/api.php/provide/vod/` | 9.9 万 |
| 爱坤 | `ikunzyapi.com/api.php/provide/vod/` | 6.7 万 |
| 创享影视 | `ys.cxkjg.cn/api/provide/vod` | 主站 + 11 条线路 |

直播：咪咕（带 XMLTV EPG 与回看）、YSP IPv6、qist 的 IPv6 综合直播（后两个需要网络有 IPv6）。

## 说明

全部是社区公开接口，内容版权与可用性由源提供方负责，说失效就失效。
本项目只提供一份空壳客户端用的配置，不含任何内容。
