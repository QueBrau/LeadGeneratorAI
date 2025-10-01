import React from 'react';

const LeadList = ({ leads, showDate = false }) => {
  if (!leads || leads.length === 0) {
    return (
      <div className="no-leads">
        <p>No leads found.</p>
      </div>
    );
  }

  return (
    <div className="lead-list">
      {leads.map((lead) => (
        <div key={lead.id} className="lead-item">
          <div className="lead-header">
            <h3 className="lead-title">{lead.title}</h3>
            <div className="lead-meta">
              <span className={`platform-badge ${lead.platform.toLowerCase()}`}>
                {lead.platform}
              </span>
              {showDate && lead.date && (
                <span className="lead-date">{lead.date}</span>
              )}
            </div>
          </div>
          
          {lead.snippet && (
            <p className="lead-snippet">{lead.snippet}</p>
          )}
          
          {lead.link && (
            <div className="lead-actions">
              <a 
                href={lead.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="view-link"
              >
                View Original Post →
              </a>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default LeadList;