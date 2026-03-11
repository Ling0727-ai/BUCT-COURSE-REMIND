import {http} from '@/api/http';
import {RegisterRequest, RegisterResponse} from './register.data';

export const registerUser = (data: RegisterRequest | Record<string, unknown>) => {
    return http.post<RegisterResponse>('/auth/register', data);
};

