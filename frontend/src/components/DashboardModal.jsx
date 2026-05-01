export default function DashboardModal({
  label,
  title,
  subtitle,
  onClose,
  children
}) {
  return (
    <div className="dashboard-modal-backdrop" role="presentation">
      <section
        className="dashboard-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dashboard-modal-title"
      >
        <div className="dashboard-modal-header">
          <div className="dashboard-modal-heading">
            <p className="section-label">{label}</p>
            <h2 id="dashboard-modal-title">{title}</h2>
            {subtitle ? <p className="section-copy">{subtitle}</p> : null}
          </div>

          <button className="secondary-button" type="button" onClick={onClose}>
            Fermer
          </button>
        </div>

        <div className="dashboard-modal-body">{children}</div>
      </section>
    </div>
  );
}
