/** Unique id for idempotent test data — no run depends on or mutates shared records. */
export function uniqueId(): string {
  return `${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
}

export interface TestUser {
  email: string;
  password: string;
}

/** Generic user factory. Adjust the email domain / password policy to your SUT. */
export function newUser(overrides: Partial<TestUser> = {}): TestUser {
  return {
    email: `qa.lab+${uniqueId()}@example.com`,
    password: 'Sup3rSafe!42',
    ...overrides,
  };
}
