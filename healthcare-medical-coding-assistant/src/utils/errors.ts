class CustomError extends Error {
    constructor(message: string) {
        super(message);
        this.name = this.constructor.name;
    }
}

class NotFoundError extends CustomError {
    constructor(resource: string) {
        super(`${resource} not found.`);
    }
}

class ValidationError extends CustomError {
    constructor(message: string) {
        super(`Validation Error: ${message}`);
    }
}

class AuthenticationError extends CustomError {
    constructor() {
        super('Authentication failed.');
    }
}

class AuthorizationError extends CustomError {
    constructor() {
        super('You do not have permission to perform this action.');
    }
}

export {
    CustomError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError
};