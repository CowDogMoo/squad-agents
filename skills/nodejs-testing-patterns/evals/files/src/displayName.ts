export interface User {
  firstName: string;
  lastName: string;
  preferredName?: string;
}

export interface UserService {
  getById(id: string): Promise<User | null>;
}

export async function getUserDisplayName(
  service: UserService,
  id: string,
): Promise<string> {
  const user = await service.getById(id);
  if (!user) {
    return 'Anonymous';
  }
  return user.preferredName ?? `${user.firstName} ${user.lastName}`;
}
