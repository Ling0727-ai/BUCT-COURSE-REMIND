export interface StudentInfo {
    studentId: string;
    sPassword?: string;
}

export interface StudentInfoUpdatePayload {
    student_id?: string;
    s_password?: string;
}

export interface EmailSettings {
    email: string;
}

export interface DataStatus {
    hasData: boolean;
    lastUpdate: string | null;
    nextAutoRefresh: string | null;
    hoursUntilRefresh: number | null;
}

export interface UserInfoResponse {
    student_id: string;
    has_student_password: boolean;
    student_password_length: number;
    email: string;
    success?: boolean;
    message?: string;
}

export interface DataStatusResponse {
    success: boolean;
    has_data: boolean;
    last_update: string | null;
    next_auto_refresh: string | null;
    hours_until_refresh: number | null;
    message?: string;
    error?: string;
}

export interface BasicApiResponse {
    success?: boolean;
    message?: string;
    error?: string;
}

export interface RefreshResponse extends BasicApiResponse {
    success: boolean;
    count?: number;
}
