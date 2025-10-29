import React from 'react';
import { cn } from '../../lib/utils';

const statusConfig = {
  draft: {
    label: 'Draft',
    color: 'bg-gray-100 text-gray-800 border-gray-200'
  },
  section1_pending: {
    label: 'Section 1 Pending',
    color: 'bg-orange-100 text-orange-800 border-orange-200'
  },
  section1_approved: {
    label: 'Section 1 Approved',
    color: 'bg-blue-100 text-blue-800 border-blue-200'
  },
  section2_pending: {
    label: 'Section 2 Pending',
    color: 'bg-amber-100 text-amber-800 border-amber-200'
  },
  section2_approved: {
    label: 'Section 2 Approved',
    color: 'bg-cyan-100 text-cyan-800 border-cyan-200'
  },
  approved: {
    label: 'Approved',
    color: 'bg-green-100 text-green-800 border-green-200'
  },
  rejected: {
    label: 'Rejected',
    color: 'bg-red-100 text-red-800 border-red-200'
  },
  sent_back: {
    label: 'Sent Back',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200'
  }
};

const StatusBadge = ({ status, className }) => {
  const config = statusConfig[status] || statusConfig.draft;

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        config.color,
        className
      )}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
