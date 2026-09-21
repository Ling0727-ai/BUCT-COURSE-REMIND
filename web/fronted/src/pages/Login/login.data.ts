export interface LoginParams {
    username: string;
    password?: string;
}

export interface UserInfo {
    id: number;
    username: string;
    is_admin: boolean;
    remember: boolean;
}

export interface DataRefreshStatus {
    success: boolean;
    message: string;
}

export interface LoginResponseData {
    user: UserInfo;
    data_refresh?: DataRefreshStatus;
    success?: boolean;
    message?: string;
    error?: string;
}