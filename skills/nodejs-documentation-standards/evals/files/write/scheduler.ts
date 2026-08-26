export interface Job {
  cancel(): void;
}

export const MAX_RETRIES = 3;

export class RateLimitError extends Error {
  retryAfter: number;

  constructor(retryAfter: number) {
    super('rate limit exceeded');
    this.retryAfter = retryAfter;
  }
}

export function schedule(intervalMs: number, fn: () => Promise<void>): Job {
  const interval = Math.max(intervalMs, 100);
  const timer = setInterval(() => {
    fn().catch(() => clearInterval(timer));
  }, interval);
  return { cancel: () => clearInterval(timer) };
}
