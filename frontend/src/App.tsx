import { useEffect, useState } from 'react';
import { api } from './lib/api';
import { MetricCard } from './components/MetricCard';
import { Panel } from './components/Panel';
import { CommandBar } from './components/CommandBar';

type Overview = {
  total_users: number;
  total_audits: number;
  upcoming_today: number;
  overdue_tasks: number;
  pending_messages: number;
};

type Audit = {
  id: string;
  title: string;
  client_name: string;
  audit_type: string;
  start_at: string;
  end_at: string;
  status: string;
};

type Task = {
  id: string;
  title: string;
  status: string;
  due_at?: string | null;
};

const fallbackOverview: Overview = {
  total_users: 0,
  total_audits: 0,
  upcoming_today: 0,
  overdue_tasks: 0,
  pending_messages: 0,
};

export default function App() {
  const [overview, setOverview] = useState<Overview>(fallbackOverview);
  const [audits, setAudits] = useState<Audit[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [status, setStatus] = useState('Connecting to Sage AI backend...');

  useEffect(() => {
    async function load() {
      try {
        const [overviewData, auditData, taskData] = await Promise.all([
          api.get<Overview>('/admin/overview'),
          api.get<Audit[]>('/audits'),
          api.get<Task[]>('/tasks'),
        ]);

        setOverview(overviewData);
        setAudits(auditData.slice(0, 5));
        setTasks(taskData.slice(0, 5));
        setStatus('Live');
      } catch (error) {
        setStatus('Running in offline preview mode');
      }
    }

    load();
  }, []);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div>
          <div className="brand">Sage AI</div>
          <p className="subtitle">Executive Assistant for ISO Auditing</p>
        </div>

        <nav className="nav">
          <a href="#overview">Overview</a>
          <a href="#audits">Audits</a>
          <a href="#tasks">Tasks</a>
          <a href="#messages">Messages</a>
          <a href="#settings">Settings</a>
        </nav>

        <div className="statusCard">
          <span className="statusLabel">System status</span>
          <strong>{status}</strong>
          <p>Self-hosted, private, and ready for Mac mini deployment.</p>
        </div>
      </aside>

      <main className="main">
        <section className="hero">
          <div>
            <span className="eyebrow">Executive command center</span>
            <h1>Sage coordinates schedules, reminders, tasks, and meeting follow-through.</h1>
            <p>
              Connect Outlook, WhatsApp, the local audit system, and document intelligence into one operational layer for auditors and managers.
            </p>
          </div>
          <CommandBar />
        </section>

        <section className="metrics" id="overview">
          <MetricCard label="Auditors" value={overview.total_users} hint="Active users" />
          <MetricCard label="Audits" value={overview.total_audits} hint="Tracked engagements" />
          <MetricCard label="Today" value={overview.upcoming_today} hint="Scheduled audits" />
          <MetricCard label="Overdue" value={overview.overdue_tasks} hint="Pending follow-ups" />
          <MetricCard label="Messages" value={overview.pending_messages} hint="Notification queue" />
        </section>

        <section className="grid">
          <Panel title="Upcoming audits" subtitle="Today and near-term schedule" id="audits">
            <div className="rows">
              {audits.length === 0 ? (
                <div className="empty">No audits loaded yet. Connect Outlook or the local audit system.</div>
              ) : (
                audits.map((audit) => (
                  <article key={audit.id} className="row">
                    <div>
                      <strong>{audit.title}</strong>
                      <p>{audit.client_name}</p>
                    </div>
                    <div className="meta">
                      <span>{audit.audit_type}</span>
                      <span>{new Date(audit.start_at).toLocaleString()}</span>
                    </div>
                  </article>
                ))
              )}
            </div>
          </Panel>

          <Panel title="Task board" subtitle="Active follow-ups and owner actions" id="tasks">
            <div className="rows">
              {tasks.length === 0 ? (
                <div className="empty">No tasks yet. Auditors can create them by message or meeting command.</div>
              ) : (
                tasks.map((task) => (
                  <article key={task.id} className="row">
                    <div>
                      <strong>{task.title}</strong>
                      <p>{task.status}</p>
                    </div>
                    <div className="meta">
                      <span>{task.due_at ? new Date(task.due_at).toLocaleDateString() : 'No due date'}</span>
                    </div>
                  </article>
                ))
              )}
            </div>
          </Panel>
        </section>

        <section className="footerGrid" id="messages">
          <Panel title="Messaging" subtitle="WhatsApp, Email, Teams adapters" compact>
            <p>
              Notifications are adapter-based so the transport can be swapped without changing the workflow engine. Friday digests and daily reminders can be sent to auditors and clients.
            </p>
          </Panel>

          <Panel title="Document intelligence" subtitle="ISO standards, checklists, templates" compact>
            <p>
              Search across local knowledge with Qdrant-backed retrieval, then show the exact section the auditor asked for during a meeting.
            </p>
          </Panel>

          <Panel title="Governance" subtitle="Roles, audit trail, conflict checks" compact id="settings">
            <p>
              Every action is logged. RBAC separates auditors, managers, and admins. Conflict detection runs before reminders are sent.
            </p>
          </Panel>
        </section>
      </main>
    </div>
  );
}
