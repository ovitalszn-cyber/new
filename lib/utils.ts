export function formatTime(timeStr: string): string {
  try {
    const date = new Date(timeStr);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (Math.abs(diffMins) < 60) {
      if (diffMins < 0) {
        return `${Math.abs(diffMins)}m ago`;
      }
      return `in ${diffMins}m`;
    }
    
    const diffHours = Math.floor(diffMins / 60);
    if (Math.abs(diffHours) < 24) {
      if (diffHours < 0) {
        return `${Math.abs(diffHours)}h ago`;
      }
      return `in ${diffHours}h`;
    }
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return timeStr;
  }
}

export function formatSportName(sport: string): string {
  return sport
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}




