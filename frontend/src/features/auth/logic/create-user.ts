import { UserService } from "@/core/services/user"
import { useCreateUser } from "@/api/hooks"

export function useValidatedCreateUser() {
  const { mutate, ...rest } = useCreateUser()

  const createUser = async (username: string) => {
    const error = UserService.validateUsername(username)
    if (error) throw new Error(error)

    const user = await mutate({ username })
    return UserService.normalise(user)
  }

  return { createUser, ...rest }
}
