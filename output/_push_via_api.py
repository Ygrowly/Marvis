# -*- coding: utf-8 -*-
"""git push 被网络通道卡死时的兜底：用 GitHub Git Data API 重放本地未推送的提交。

跑法：python output/_push_via_api.py
原理：对 origin/main..HEAD 的每个提交，按原样建成 blob → tree → commit → 最后更新分支 ref。
      author / committer / date / message 全部照抄本地提交，所以新 commit 的 SHA 与本地一致，
      fetch 之后两边完全对齐，不需要 reset。

坑：路径必须用 -z（NUL 分隔），否则中文路径会被 git 转义成八进制字符串，ls-tree 认不出来。
"""
import base64
import datetime
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "Ygrowly/Marvis"
BRANCH = "main"
API_ROOT = "https://api.github.com"


def sh(args, binary=False, check=True):
    r = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and r.returncode != 0:
        sys.exit("命令失败：%s\n%s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
    return r.stdout if binary else r.stdout.decode("utf-8").strip()


def api(method, path, payload=None):
    """传输层走 curl：本机 git 的 schannel 和 Python 的 urllib 都可能 TLS 握手失败，
       而 curl 直连是通的（2026-10-02 实测）。
       --ssl-no-revoke（2026-10-04 增补）：schannel 的证书吊销检查可能因吊销服务器
       不可达而失败（CRYPT_E_REVOCATION_OFFLINE），跳过它——GitHub 的证书链不受影响。"""
    cmd = ["curl", "-sS", "--ssl-no-revoke",
           "-x", "http://127.0.0.1:7897",   # 2026-10-04 起 GitHub 走 Clash 代理（直连时通时断）
           "-m", "90",
           "--retry", "4", "--retry-all-errors", "--retry-delay", "2",
           "-X", method, API_ROOT + path,
           "-H", "Authorization: Bearer " + TOKEN,
           "-H", "Accept: application/vnd.github+json",
           "-H", "X-GitHub-Api-Version: 2022-11-28",
           "-H", "User-Agent: marvis-push"]
    if payload is not None:
        cmd += ["-H", "Content-Type: application/json; charset=utf-8", "--data-binary", "@-"]
        r = subprocess.run(cmd, input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        sys.exit("curl %s %s 失败：%s" % (method, path, r.stderr.decode("utf-8", "replace")[:300]))
    try:
        return json.loads(r.stdout) if r.stdout.strip() else {}
    except ValueError:
        sys.exit("返回不是 JSON：%s" % r.stdout.decode("utf-8", "replace")[:200])


def ident(raw, kind):
    m = re.search(("^%s (.*) <(.*)> (\\d+) ([+-]\\d{4})$" % kind).encode(), raw, re.M)
    if not m:
        sys.exit("提交里解析不到 %s 行" % kind)
    ts = int(m.group(3))
    off = m.group(4).decode()
    tz = datetime.timezone((1 if off[0] == "+" else -1) *
                           datetime.timedelta(hours=int(off[1:3]), minutes=int(off[3:5])))
    return {
        "name": m.group(1).decode("utf-8", "replace"),
        "email": m.group(2).decode("utf-8", "replace"),
        "date": datetime.datetime.fromtimestamp(ts, tz).replace(microsecond=0).isoformat(),
    }


TOKEN = sh(["gh", "auth", "token"])
local_head = sh(["git", "rev-parse", "HEAD"])
# git 的网络可能是坏的（schannel 握手失败），所以远端位置一律走 API 问
remote = api("GET", "/repos/%s/git/ref/heads/%s" % (REPO, BRANCH))["object"]["sha"]
if remote == local_head:
    print("远端已经是最新，不用推")
    sys.exit(0)

commits = sh(["git", "rev-list", "--reverse", "--no-merges", remote + "..HEAD"]).split()
if not commits:
    print("没有新的本地提交")
    sys.exit(0)
print("待推送 %d 个提交，远端当前 %s" % (len(commits), remote[:9]))

cursor = remote           # 远端分支当前指向，作为第一个新提交的 parent
for c in commits:
    raw_commit = sh(["git", "cat-file", "commit", c], binary=True)
    header, _, message = raw_commit.partition(b"\n\n")
    parents = re.findall(b"^parent ([0-9a-f]{40})$", header, re.M)
    base = sh(["git", "rev-parse", c + "^"]) if parents else None

    if base:
        parts = sh(["git", "diff-tree", "-r", "-z", "--no-renames", "--no-commit-id",
                    "--name-status", base, c]).split("\0")
    else:  # 根提交
        parts = sh(["git", "diff-tree", "-r", "-z", "--no-renames", "--no-commit-id",
                    "--name-status", "--root", c]).split("\0")

    tree = []
    k = 0
    while k + 1 < len(parts):
        status, path = parts[k], parts[k + 1]
        k += 2
        if not path:
            continue
        if status == "D":
            tree.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        spec = (c + ":" + path) if not base else None
        if spec:
            mode_out = sh(["git", "ls-tree", "-z", c, "--", path]).split("\0")[0]
            mode = mode_out.split(" ", 1)[0]
        else:
            mode = sh(["git", "ls-tree", "-z", c, "--", path]).split("\0")[0].split(" ", 1)[0]
        blob = sh(["git", "cat-file", "blob", c + ":" + path], binary=True)
        r = api("POST", "/repos/%s/git/blobs" % REPO,
                {"content": base64.b64encode(blob).decode("ascii"), "encoding": "base64"})
        tree.append({"path": path, "mode": mode, "type": "blob", "sha": r["sha"]})
        print("  blob %s %s (%d B)" % (status, path, len(blob)))

    base_tree = api("GET", "/repos/%s/commits/%s" % (REPO, cursor))["commit"]["tree"]["sha"]
    new_tree = api("POST", "/repos/%s/git/trees" % REPO, {"base_tree": base_tree, "tree": tree})
    new_commit = api("POST", "/repos/%s/git/commits" % REPO, {
        "message": message.decode("utf-8", "replace"),
        "tree": new_tree["sha"],
        "parents": [cursor],
        "author": ident(header, "author"),
        "committer": ident(header, "committer"),
    })
    print("  ✅ %s → %s  %s" % (c[:9], new_commit["sha"][:9],
                               message.decode("utf-8", "replace").splitlines()[0][:52]))
    cursor = new_commit["sha"]

api("PATCH", "/repos/%s/git/refs/heads/%s" % (REPO, BRANCH), {"sha": cursor})
print("\n已把 %s 更新到 %s（本地 HEAD %s）" % (BRANCH, cursor[:9], local_head[:9]))
if cursor != local_head:
    print("⚠ SHA 与本地不一致，跑 git fetch 后用 reset --soft 对齐")
