import { User } from "@/core/entities/user"

/**
* Core business-level service for user-related operations.
* It doesn’t know about React, HTTP, or storage.
*/
export const UserService = {
    /** Basic validation logic */
    validateUsername(username: string): string | null {
        if (!username.trim())
            return "Username cannot be empty"
        if (username.length < 3)
            return "Username must be at least 3 characters"
        if (/\s/.test(username))
            return "Username cannot contain spaces"
        return null
    },

    normalise(user: User): User {
        return new User({
            id: user.id,
            username: user.username.trim(),
            isActive: user.isActive,
        })
    },

}
