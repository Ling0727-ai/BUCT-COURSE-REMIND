export interface RegisterFormData {
    username: string;
    email: string;
    password: string;
    confirmPassword: string;
    captcha: string;
    studentId: string;
    sPassword: string;
    agreeTerms: boolean;
}

export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    student_id?: string;
    s_password?: string;
    code?: string; // used in verify-code
}

export interface RegisterResponse {
    success?: boolean;
    message?: string;
    error?: string;
    data_refresh?: {
        success: boolean;
        count: number;
        message: string;
    };
}