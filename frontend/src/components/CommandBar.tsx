export function CommandBar() {
  return (
    <div className="commandBar">
      <div>
        <span>Command prompt</span>
        <strong>“Sage, show next week’s audits”</strong>
      </div>
      <div>
        <span>Quick actions</span>
        <div className="commandButtons">
          <button type="button">Sync Outlook</button>
          <button type="button">Index documents</button>
          <button type="button">Send digest</button>
        </div>
      </div>
    </div>
  );
}
