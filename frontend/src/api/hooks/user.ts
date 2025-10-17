import {
    MutationMapper,
    HookFactory,
    UserResponse,
    CreateUserRequest,
    useCreateUser as useCreateUserGenerated,
} from "@/api/internal-utils"
import { User } from "@/core/entities/user"

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
        return new User({
            id: dto.id,
            username: dto.username,
            isActive: dto.is_active,
        })
    },
}

// Wrap Orval mutation hook.
// Naming: use<Operation><Entity>, where Operation is a verb and Entity is a noun.
export const useCreateUser = HookFactory.createMappedMutationHook(
    useCreateUserGenerated,
    createUserMapper
)

// Actual usage:
export const useCreateUserShort = HookFactory.createMappedMutationHook(
    useCreateUserGenerated,
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
            return new User({
                id: out.id,
                username: out.username,
                isActive: out.is_active,
            })
        },
    }
)

// Example usage.
const { mutate, ...rest } = useCreateUser()

async function handleSubmit() {
    try {
        const user = await mutate({ username: "alice" })
        console.log("Created user:", user)
    } catch (err) {
        console.error(err)
    }
}
