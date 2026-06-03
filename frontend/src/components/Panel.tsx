import type { ReactNode } from 'react';

type PanelProps = {
  title: string;
  subtitle: string;
  children: ReactNode;
  compact?: boolean;
  id?: string;
};

export function Panel({ title, subtitle, children, compact = false, id }: PanelProps) {
  return (
    <section className={`panel ${compact ? 'compact' : ''}`} id={id}>
      <div className="panelHeader">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  );
}
