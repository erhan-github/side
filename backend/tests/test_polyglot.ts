
class UserManager {
    private users: User[];

    constructor() {
        this.users = [];
    }

    public addUser(user: User): void {
        this.users.push(user);
    }
}

interface User {
    id: string;
    name: string;
}

function globalHelper() {
    console.log("Helper");
}
