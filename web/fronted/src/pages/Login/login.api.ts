import {http} from '@/api/http';
import {LoginResponseData} from './login.data';

export const login = (data: Record<string, unknown>) => {
    return http.post<LoginResponseData>('/auth/login', data);
}

