import { getStatusColor, getStatusLabel, cn } from '../lib/utils';

export default function OrderStatusBadge({ status }: { status: string }) {
  const colorClass = getStatusColor(status);
  return (
    <span className={cn("px-2.5 py-1 text-xs font-semibold rounded-full uppercase tracking-wide", colorClass)}>
      {getStatusLabel(status)}
    </span>
  );
}
