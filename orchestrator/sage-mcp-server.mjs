#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const SAGE_API_BASE = process.env.SAGE_API_BASE || "http://127.0.0.1:8000/api";
const SAGE_API_BASE_NORMALIZED = SAGE_API_BASE.replace(/\/$/, "");
const SAGE_EMAIL = process.env.SAGE_EMAIL || "";
const SAGE_PASSWORD = process.env.SAGE_PASSWORD || "";
const SAGE_REQUEST_TIMEOUT_MS = Number(process.env.SAGE_REQUEST_TIMEOUT_MS || 30000);
let cachedToken = process.env.SAGE_TOKEN || "";

function toolResult(data) {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(data, null, 2),
      },
    ],
  };
}

async function requestJson(path, options = {}, requiresAuth = true) {
  return requestJsonInternal(path, options, requiresAuth, true);
}

async function requestJsonInternal(path, options = {}, requiresAuth = true, allowAuthRetry = false) {
  const headers = {
    ...(options.headers || {}),
  };

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (requiresAuth) {
    const token = await ensureToken();
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${SAGE_API_BASE_NORMALIZED}${path}`, {
    ...options,
    headers,
    signal: AbortSignal.timeout(SAGE_REQUEST_TIMEOUT_MS),
  });

  const bodyText = await response.text();
  let body;
  try {
    body = bodyText ? JSON.parse(bodyText) : {};
  } catch {
    body = { raw: bodyText };
  }

  if (response.status === 401 && allowAuthRetry && requiresAuth && !process.env.SAGE_TOKEN) {
    cachedToken = "";
    return requestJsonInternal(path, options, requiresAuth, false);
  }

  if (!response.ok) {
    throw new Error(`Sage API ${response.status} ${response.statusText}: ${JSON.stringify(body)}`);
  }

  return body;
}

async function ensureToken() {
  if (cachedToken) {
    return cachedToken;
  }

  if (!SAGE_EMAIL || !SAGE_PASSWORD) {
    throw new Error("No auth available. Set SAGE_TOKEN or SAGE_EMAIL + SAGE_PASSWORD environment variables.");
  }

  const form = new URLSearchParams();
  form.set("username", SAGE_EMAIL);
  form.set("password", SAGE_PASSWORD);

  const response = await fetch(`${SAGE_API_BASE_NORMALIZED}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: form,
    signal: AbortSignal.timeout(SAGE_REQUEST_TIMEOUT_MS),
  });

  const rawBody = await response.text();
  let body;
  try {
    body = rawBody ? JSON.parse(rawBody) : {};
  } catch {
    body = { raw: rawBody };
  }

  if (!response.ok || !body.access_token) {
    throw new Error(`Sage login failed: ${JSON.stringify(body)}`);
  }

  cachedToken = body.access_token;
  return cachedToken;
}

function createMeetingTranscript(command, auditType) {
  if (!auditType) {
    return command;
  }
  return `${command} for ${auditType}`;
}

async function runMeetingCommand(command, topK, auditType) {
  const transcript = createMeetingTranscript(command, auditType);
  return requestJson("/integrations/meetings/command", {
    method: "POST",
    body: JSON.stringify({ transcript, top_k: topK }),
  });
}

async function runNotificationTest(channel, recipient, body, subject) {
  return requestJson(`/integrations/${channel}/test`, {
    method: "POST",
    body: JSON.stringify({ recipient, body, subject }),
  });
}

const server = new McpServer(
  {
    name: "sage-api-bridge",
    version: "1.0.0",
  },
  {
    instructions:
      "Use these tools to query schedule/checklist/sections, create and update tasks, and trigger WhatsApp or Teams test notifications in Sage.",
  },
);

server.tool("sage_health", "Get Sage backend and LLM health status.", async () => {
  const data = await requestJson("/health", { method: "GET" }, false);
  return toolResult(data);
});

server.tool(
  "sage_show_schedule",
  "Get upcoming audit schedule from meeting-assistant intent handling.",
  {
    topK: z.number().int().min(1).max(20).default(3),
  },
  async ({ topK }) => {
    const data = await runMeetingCommand("show schedule", topK);
    return toolResult(data);
  },
);

server.tool(
  "sage_open_checklist",
  "Open checklist context for an ISO audit type and return relevant doc snippets.",
  {
    auditType: z.string().optional(),
    topK: z.number().int().min(1).max(20).default(3),
  },
  async ({ auditType, topK }) => {
    const data = await runMeetingCommand("open checklist", topK, auditType);
    return toolResult(data);
  },
);

server.tool(
  "sage_show_section",
  "Show an ISO section reference with retrieved context.",
  {
    sectionRef: z.string().min(1),
    auditType: z.string().optional(),
    topK: z.number().int().min(1).max(20).default(3),
  },
  async ({ sectionRef, auditType, topK }) => {
    const data = await runMeetingCommand(`show section ${sectionRef}`, topK, auditType);
    return toolResult(data);
  },
);

server.tool(
  "sage_list_tasks",
  "List tasks in Sage.",
  {
    limit: z.number().int().min(1).max(200).default(20),
  },
  async ({ limit }) => {
    const tasks = await requestJson("/tasks/", { method: "GET" });
    return toolResult(tasks.slice(0, limit));
  },
);

server.tool(
  "sage_create_task",
  "Create a new task in Sage.",
  {
    title: z.string().min(1),
    description: z.string().optional(),
    priority: z.number().int().min(1).max(5).default(3),
    dueAt: z.string().datetime().optional(),
    reminderAt: z.string().datetime().optional(),
    ownerId: z.string().optional(),
    assigneeId: z.string().optional(),
    relatedAuditId: z.string().optional(),
  },
  async ({ title, description, priority, dueAt, reminderAt, ownerId, assigneeId, relatedAuditId }) => {
    const data = await requestJson("/tasks/", {
      method: "POST",
      body: JSON.stringify({
        title,
        description,
        priority,
        due_at: dueAt,
        reminder_at: reminderAt,
        owner_id: ownerId,
        assignee_id: assigneeId,
        related_audit_id: relatedAuditId,
      }),
    });
    return toolResult(data);
  },
);

server.tool(
  "sage_update_task_status",
  "Update an existing task status to open, in_progress, blocked, or done.",
  {
    taskId: z.string().min(1),
    status: z.enum(["open", "in_progress", "blocked", "done"]),
  },
  async ({ taskId, status }) => {
    const data = await requestJson(`/tasks/${taskId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    return toolResult(data);
  },
);

server.tool(
  "sage_send_whatsapp_test",
  "Send a WhatsApp test message via Sage notification integration.",
  {
    recipient: z.string().min(1),
    body: z.string().min(1),
    subject: z.string().optional(),
  },
  async ({ recipient, body, subject }) => {
    const data = await runNotificationTest("whatsapp", recipient, body, subject);
    return toolResult(data);
  },
);

server.tool(
  "sage_send_teams_test",
  "Send a Microsoft Teams test message via Sage notification integration.",
  {
    recipient: z.string().min(1),
    body: z.string().min(1),
    subject: z.string().optional(),
  },
  async ({ recipient, body, subject }) => {
    const data = await runNotificationTest("teams", recipient, body, subject);
    return toolResult(data);
  },
);

server.tool("sage_sync_outlook", "Sync Microsoft Graph calendar into Sage audits.", async () => {
  const data = await requestJson("/integrations/microsoft-graph/sync", {
    method: "POST",
    body: JSON.stringify({}),
  });
  return toolResult(data);
});

server.tool("sage_preview_outlook", "Preview Outlook calendar events via Sage Graph connector.", async () => {
  const data = await requestJson("/integrations/microsoft-graph/preview", {
    method: "GET",
  });
  return toolResult(data);
});

const transport = new StdioServerTransport();
await server.connect(transport);