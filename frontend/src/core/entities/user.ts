interface UserProps {
    id: number
    username: string
    isActive: boolean
}

export class User {
    public readonly id: number
    public readonly username: string
    public readonly isActive: boolean

    constructor({ id, username, isActive }: UserProps) {
        this.id = id
        this.username = username
        this.isActive = isActive
    }

    get displayName(): string {
        return this.username.toUpperCase()
    }

    activate(): User {
        return new User({
            id: this.id,
            username: this.username,
            isActive: true,
        })
    }
}
