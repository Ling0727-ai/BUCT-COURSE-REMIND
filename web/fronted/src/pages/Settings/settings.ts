import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables/useToast';

import { mapAuthError } from '@/pages/Auth/auth';
import { updateEmail, updateStudentInfo, getUserInfo, getDataStatus, refreshCourseData } from './settings.api';
import { DataStatus, EmailSettings, StudentInfo, StudentInfoUpdatePayload } from './settings.data';

export function useSettingsService() {
    const router = useRouter();
    const { showToast } = useToast();

    // State
    const studentInfo = reactive<StudentInfo>({
        studentId: '',
        sPassword: ''
    });

    const emailSettings = reactive<EmailSettings>({
        email: ''
    });

    const dataStatus = reactive<DataStatus>({
        hasData: false,
        lastUpdate: null,
        nextAutoRefresh: null,
        hoursUntilRefresh: null
    });

    const refreshing = ref(false);

    // Helpers
    const formatDateTime = (dateString: string | null) => {
        if (!dateString) return '未知';
        try {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZone: 'Asia/Shanghai'
            });
        } catch (error) {
            return '格式错误';
        }
    };

    const formatNextRefresh = (hours: number | null) => {
        if (hours === null || hours === undefined) return '未知';
        if (hours <= 0) return '即将刷新';
        if (hours < 1) {
            const minutes = Math.round(hours * 60);
            return `${minutes}分钟后`;
        }
        return `${Math.round(hours * 10) / 10}小时后`;
    };

    // Actions
    const goBack = () => {
        router.back();
    };

    const handleSaveEmailSettings = async () => {
        if (!emailSettings.email) {
            showToast('error', 'Error', '请填写邮箱地址');
            return;
        }

        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailSettings.email)) {
            showToast('error', 'Error', '邮箱格式不正确');
            return;
        }

        showToast('info', 'Info', '正在修改邮箱...');

        try {
            await updateEmail(emailSettings.email);
            showToast('success', 'Success', '邮箱修改成功！账号恢复和提醒邮箱已同步更新');
            await handleLoadUserInfo();
        } catch (error: unknown) {
            showToast('error', 'Error', mapAuthError(error, '修改失败'));
        }
    };

    const handleSaveStudentInfo = async () => {
        const payload: StudentInfoUpdatePayload = {};
        if (studentInfo.studentId && studentInfo.studentId.trim() !== '') {
            payload.student_id = studentInfo.studentId.trim();
        }

        // Only send password if it's not the mask
        if (studentInfo.sPassword && !/^•+$/.test(studentInfo.sPassword.trim())) {
            payload.s_password = studentInfo.sPassword;
        }

        if (Object.keys(payload).length === 0) {
            showToast('error', 'Error', '请填写学号或新密码');
            return;
        }

        showToast('info', 'Info', '正在保存学生信息...');

        try {
            await updateStudentInfo(payload);

            // Re-mask password on success
            const newPassword = payload.s_password;
            if (newPassword) {
                studentInfo.sPassword = '•'.repeat(Math.min(newPassword.length, 100));
            }
            showToast('success', 'Success', '学生信息保存成功！');
        } catch (error: unknown) {
            showToast('error', 'Error', mapAuthError(error, '保存失败'));
        }
    };

    const handleLoadDataStatus = async () => {
        try {
            const data = await getDataStatus();
            if (data.success) {
                dataStatus.hasData = data.has_data;
                dataStatus.lastUpdate = data.last_update;
                dataStatus.nextAutoRefresh = data.next_auto_refresh;
                dataStatus.hoursUntilRefresh = data.hours_until_refresh;
            }
        } catch (error) {
            console.warn('获取数据状态失败', error);
        }
    };

    const handleRefreshCourseData = async () => {
        if (refreshing.value) return;

        refreshing.value = true;
        showToast('info', 'Info', '正在刷新课程数据...');

        try {
            const data = await refreshCourseData();
            if (data.success) {
                showToast('success', 'Success', `数据刷新成功！共更新 ${data.count} 条记录`);
                await handleLoadDataStatus();
            } else {
                showToast('error', 'Error', data.error || '刷新失败');
            }
        } catch (error: unknown) {
            console.error('刷新数据错误:', error);
            showToast('error', 'Error', mapAuthError(error, '网络错误，请检查连接后重试'));
        } finally {
            refreshing.value = false;
        }
    };

    const handleLoadUserInfo = async () => {
        try {
            const data = await getUserInfo();
            studentInfo.studentId = data.student_id || '';
            if (data.has_student_password && data.student_password_length > 0) {
                studentInfo.sPassword = '•'.repeat(Math.min(data.student_password_length, 100));
            } else {
                studentInfo.sPassword = '';
            }
            emailSettings.email = data.email || '';
        } catch (error) {
            console.error('加载用户信息失败:', error);
        }
    };

    // Initialize
    handleLoadUserInfo();
    handleLoadDataStatus();

    return {
        studentInfo,
        emailSettings,
        dataStatus,
        refreshing,
        formatDateTime,
        formatNextRefresh,
        goBack,
        handleSaveEmailSettings,
        handleSaveStudentInfo,
        handleLoadDataStatus,
        handleRefreshCourseData
    };
}
