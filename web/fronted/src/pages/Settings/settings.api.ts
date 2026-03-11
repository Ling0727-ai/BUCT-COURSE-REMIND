import {http} from '@/api/http';
import {
    BasicApiResponse,
    DataStatusResponse,
    RefreshResponse,
    StudentInfoUpdatePayload,
    UserInfoResponse
} from './settings.data';

export const updateEmail = (email: string) => {
    return http.post<BasicApiResponse>('/auth/update-email', {email});
};

export const updateStudentInfo = (payload: StudentInfoUpdatePayload) => {
    return http.post<BasicApiResponse>('/auth/update-student-info', payload);
};

export const getUserInfo = () => {
    return http.get<UserInfoResponse>('/auth/user-info');
};

export const getDataStatus = () => {
    return http.get<DataStatusResponse>('/course-data/status');
};

export const refreshCourseData = () => {
    return http.post<RefreshResponse>('/assignments/refresh-sync', {});
};

