import {
    MutationMapper,
    HookFactory,
    UserResponse,
    CreateUserRequest,
    useCreateUser,
} from "@/api/internal-utils"
import { User } from "@/api/models"

//TODO: Test query hooks.

// Bidirectional mapper for User create endpoint.
const createUserMapper: MutationMapper<
    { username: string },  //    FrontendRequest ->
    CreateUserRequest,     // -> BackendRequest ->
    UserResponse,          // -> BackendResponse ->
    User                   // -> FrontendResponse
> = {
    toRequest(model) {
        return {
            username: model.username
        }
    },
    fromResponse(dto) {
        return {
            id: dto.id,
            username: dto.username,
            isActive: dto.is_active,
        }
    },
}

// Wrap Orval mutation hook.
export const useCreateUserMutationExplicit = HookFactory.createMappedMutationHook(
    useCreateUser,
    createUserMapper
)

// Actual usage:
export const useCreateUserMutation = HookFactory.createMappedMutationHook(
    useCreateUser,
    {
        // "Frontend input to Backend request"
        toRequest(inp: { username: string }): CreateUserRequest {
            return {
                username: inp.username
                //username: 2
            }
        },
        // "from Backend response to Frontend output (model)"
        fromResponse(out: UserResponse): User {
            return {
                id: out.id,
                username: out.username,
                isActive: out.is_active,
            }
        },
    }
)

// Example usage.
const { mutate, ...rest } = useCreateUserMutation()

async function handleSubmit() {
    try {
        const user = await mutate({ username: "alice" })
        console.log("Created user:", user)
    } catch (err) {
        console.error(err)
    }
}
