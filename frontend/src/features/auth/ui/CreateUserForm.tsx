import { useState } from "react"
import { useValidatedCreateUser } from "@/features/auth/logic/create-user"
import { Input } from "@/shared/components/Input"
import { Button } from "@/shared/components/Button"


// NOTE: EXAMPLE ONLY! Re-implement from scratch.
export function CreateUserForm() {
    const { createUser, isPending, isSuccess, error } = useValidatedCreateUser()
    const [username, setUsername] = useState("")
    const [validationError, setValidationError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            const user = await createUser(username)
            console.log("Created:", user)
            setUsername("")
            setValidationError(null)
        } catch (err) {
            setValidationError(String(err))
        }
    }

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
                value={username}
                onChange={e => setUsername(e.target.value)}
                placeholder="Enter username"
            />
            <Button type="submit" disabled={isPending}>
                {isPending ? "Creating..." : "Create User"}
            </Button>

            {validationError && <p className="text-red-600">{validationError}</p>}
            {isSuccess && <p className="text-green-600">User created successfully.</p>}
            {error && <p className="text-red-600">{String(error)}</p>}
        </form>
    )
}
