export const MAINTENANCE_MODE =
  process.env.NEXT_PUBLIC_MAINTENANCE_MODE === 'true';

export const MAINTENANCE_MESSAGE =
  process.env.NEXT_PUBLIC_MAINTENANCE_MESSAGE ??
  "Expanding coverage — Call of Duty and Rainbow Six Siege are coming online. We'll be back shortly.";
