declare const db: {
  query(sql: string, params: unknown[]): Promise<User | undefined>;
};

export interface User {
  id: string;
  name: string;
  email: string;
}

/**
 * Gets the user.
 *
 * @param {string} id - The user's UUID
 * @returns {Promise<User | null>} The user
 */

export async function getUserById(id: string): Promise<User | null> {
  const row = await db.query('SELECT * FROM users WHERE id = $1', [id]);
  return row ?? null;
}

/**
 * Parses a raw JSON payload into a User.
 */
export function parseUser(raw: string): User {
  return JSON.parse(raw) as User;
}
