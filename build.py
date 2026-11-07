#!/usr/bin/env python3
"""从 sources.json 探测每个源是否活着，生成 yingxia-sub.json（给映匣 Yingxia / TVBox 用）。

规则：
  - 点播：请求 <api>?ac=list&pg=1，要求返回 JSON 且 code == 1
  - 直播：请求播单，要求首行以 #EXTM3U 开头（TXT 播单退化为“能取到内容”）
  - 连挂 2 次才摘掉，避免 GitHub 美国节点被区域性屏蔽导致误杀
只依赖标准库，GitHub Actions 里直接跑。
"""
import json
import os
import urllib.parse
import urllib.request

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
}
TIMEOUT = 25
DEAD_LIMIT = 2
OUT = "yingxia-sub.json"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read(500000)


def probe_vod(api):
    sep = "&" if "?" in api else "?"
    body = fetch(api + sep + "ac=list&pg=1").decode("utf-8", "ignore")
    data = json.loads(body)
    if data.get("code") != 1:
        return False, "code=%s" % data.get("code")
    return True, "total=%s" % data.get("total")


def probe_live(url):
    head = fetch(url)[:200].decode("utf-8", "ignore").lstrip()
    if head.startswith("#EXTM3U"):
        return True, "m3u"
    if head:
        return True, "txt"
    return False, "empty"


def main():
    src = json.load(open("sources.json", encoding="utf-8"))
    state_path = os.path.join(os.path.dirname(__file__), "state.json")
    state = json.load(open(state_path, encoding="utf-8")) if os.path.exists(state_path) else {}

    sites, lives, report = [], [], []

    for s in src["sites"]:
        try:
            ok, detail = probe_vod(s["api"])
        except Exception as exc:  # 网络错误/超时/非 JSON
            ok, detail = False, type(exc).__name__
        streak = 0 if ok else state.get(s["key"], 0) + 1
        state[s["key"]] = streak
        mark = "OK " if ok else ("DEAD" if streak >= DEAD_LIMIT else "WARN")
        report.append("%-5s %-14s streak=%d %s" % (mark, s["name"], streak, detail))
        if streak >= DEAD_LIMIT:
            continue
        sites.append({
            "key": s["key"],
            "name": s["name"],
            "type": 1,
            "api": s["api"],
            "searchable": 1,
            "quickSearch": 1,
            "filterable": 1,
            "changeable": 1,
            "playerType": 1,
        })

    for s in src["lives"]:
        try:
            ok, detail = probe_live(s["url"])
        except Exception as exc:
            ok, detail = False, type(exc).__name__
        streak = 0 if ok else state.get(s["url"], 0) + 1
        state[s["url"]] = streak
        mark = "OK " if ok else ("DEAD" if streak >= DEAD_LIMIT else "WARN")
        report.append("%-5s %-14s streak=%d %s" % (mark, s["name"], streak, detail))
        if streak >= DEAD_LIMIT:
            continue
        entry = {"name": s["name"], "type": 0, "url": s["url"], "playerType": 1, "timeout": 20}
        if s.get("epg"):
            entry["epg"] = s["epg"]
        if s.get("logo"):
            entry["logo"] = s["logo"]
        lives.append(entry)

    sub = {"spider": "", "wallpaper": "", "sites": sites, "lives": lives,
           "parses": [], "dex": []}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(sub, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(state_path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("生成 %s：%d 个点播源 / %d 个直播播单" % (OUT, len(sites), len(lives)))
    for line in report:
        print(line)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("## 映匣订阅测活\n\n%d 个点播源 / %d 个直播播单在线\n\n```\n%s\n```\n"
                     % (len(sites), len(lives), "\n".join(report)))


if __name__ == "__main__":
    main()
