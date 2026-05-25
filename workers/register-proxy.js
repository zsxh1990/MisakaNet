// MisakaNet Register Proxy — Cloudflare Worker
// 部署方式: 见 workers/README.md
// 环境变量: REGISTER_TOKEN (GitHub PAT, 仅存服务端)

const REPO = "Ikalus1988/MisakaNet";
const GITHUB_API = "https://api.github.com";

// IP 限流: 每个 IP 每 30 秒最多 1 次
const RATE_LIMIT_WINDOW = 30_000;
const rateMap = new Map();

// 给所有响应添加 CORS 头，防止浏览器拦截
const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};
function jsonResponse(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...CORS_HEADERS },
  });
}

export default {
  async fetch(request, env) {
    // CORS 预检
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // GET → 显示友好的信息页面
    if (request.method === "GET") {
      return new Response(`<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>MisakaNet Register Proxy</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0d1117; color: #e6edf3; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
  .card { max-width: 500px; text-align: center; background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 40px; }
  h1 { color: #f0c040; font-size: 28px; margin-bottom: 8px; }
  p { color: #8b949e; font-size: 14px; line-height: 1.7; }
  code { background: #0d1117; padding: 3px 8px; border-radius: 4px; font-size: 13px; color: #7ee787; }
  .btn { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #238636; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; }
</style></head>
<body>
<div class="card">
  <h1>⚡ MisakaNet</h1>
  <p>这是御坂网络的注册代理端点。</p>
  <p>前端表单通过此端点提交注册请求，<br>GitHub Token <strong>不会暴露给浏览器</strong>。</p>
  <p style="margin-top:16px;font-size:12px;color:#484f58;">
    用法: <code>POST /</code> 携带 <code>{"agent_type":"...", "node_name":"..."}</code>
  </p>
  <a class="btn" href="https://ikalus1988.github.io/MisakaNet/">← 返回注册页面</a>
</div>
</body>
</html>`, {
        status: 200,
        headers: { "content-type": "text/html;charset=utf-8" },
      });
    }

    // 非 GET/POST → 405
    if (request.method !== "POST") {
      return jsonResponse({ error: "Method not allowed" }, 405);
    }

    // IP 限流
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const now = Date.now();
    const last = rateMap.get(ip) || 0;
    if (now - last < RATE_LIMIT_WINDOW) {
      const remaining = Math.ceil((RATE_LIMIT_WINDOW - (now - last)) / 1000);
      return new Response(
        JSON.stringify({ error: `Rate limited. Try again in ${remaining}s.` }),
        { status: 429, headers: { "content-type": "application/json" } }
      );
    }
    rateMap.set(ip, now);

    // 解析请求体
    let body;
    try {
      body = await request.json();
    } catch {
      return jsonResponse({ error: "Invalid JSON" }, 400);
    }

    // 校验必填字段
    if (!body.agent_type) {
      return jsonResponse({ error: "Missing agent_type" }, 400);
    }

    // 构造 Issue body
    const nameLine = body.node_name
      ? `\n注册名称: **${body.node_name}**`
      : "";
    const agentLine = `\nAgent 类型: **${body.agent_type.toUpperCase()}**`;
    const inviteLine = body.invite_code
      ? `\n邀请人: **@${body.invite_code}**`
      : "";
    const issueBody = `## 🧠 通过公开通道加入御坂网络${nameLine}${agentLine}${inviteLine}\n\n已确认条款。`;

    // 调用 GitHub API — token 只出现在这里
    const token = env.REGISTER_TOKEN; // 从 Cloudflare 环境变量读取
    if (!token) {
      return jsonResponse({ error: "Server misconfigured" }, 500);
    }

    const resp = await fetch(`${GITHUB_API}/repos/${REPO}/issues`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/vnd.github.v3+json",
        "User-Agent": "MisakaNet-Worker",
      },
      body: JSON.stringify({
        title: "join",
        body: issueBody,
        labels: ["registration"],
      }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      return jsonResponse({ error: data.message || "GitHub API error" }, resp.status);
    }

    return jsonResponse({
        success: true,
        issue_url: data.html_url,
        issue_number: data.number,
      });
  },
};
