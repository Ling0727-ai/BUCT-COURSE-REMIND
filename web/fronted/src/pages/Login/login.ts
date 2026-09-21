import { ref } from 'vue';
import { useRouter } from 'vue-router';
import rsaCrypto from '@/utils/rsa-crypto';
import { useToast } from '@/composables/useToast';
import { consumeAutoLogoutReason, mapAuthError, markLoginSuccess, persistLoginState } from '@/pages/Auth/auth';
import { SESSION_KEYS } from '@/config/session';
import { login } from './login.api';
import { UserInfo } from './login.data';

export function useLoginService() {
    const router = useRouter();
    const { showToast: showTopToast } = useToast();

    // State
    const username = ref('');
    const password = ref('');
    const usernameFocused = ref(false);
    const passwordFocused = ref(false);
    const showPassword = ref(false);
    const rememberMe = ref(false);
    const loading = ref(false);
    const showSuccess = ref(false);
    const showDataRefresh = ref(false);
    const dataRefreshLoading = ref(false);
    const dataRefreshMessage = ref('');
    const errorMessage = ref('');
    const showError = ref(false);
    const showForgotPasswordModal = ref(false);

    // Helpers
    const showErrorToast = (msg: string) => {
        errorMessage.value = msg;
        showError.value = true;
        setTimeout(() => {
            showError.value = false;
        }, 3000);
        showTopToast('error', 'Login Failed', msg);
    };

    // Actions
    const handleLogin = async () => {
        if (!username.value.trim() || !password.value.trim()) {
            showErrorToast('Please enter username/email and password');
            return;
        }

        loading.value = true;
        errorMessage.value = '';

        try {
            const requestData = await rsaCrypto.createEncryptedRequest({
                username: username.value,
                password: password.value
            });

            const data = await login(requestData);
            // login api now returns LoginResponseData directly (it calls .json() inside http wrapper)

            // Handle Success
            showSuccess.value = true;
            showTopToast('success', 'Login Successful', 'Welcome back');

            if (data.data_refresh) {
                const msg = data.data_refresh.message || 'Updating assignment data...';
                showTopToast(data.data_refresh.success ? 'info' : 'warning', 'Data Update', msg);

                if (data.data_refresh.success) {
                    dataRefreshMessage.value = data.data_refresh.message;
                    showDataRefresh.value = true;
                    dataRefreshLoading.value = false;
                    setTimeout(() => showDataRefresh.value = false, 3000);
                } else {
                    dataRefreshMessage.value = data.data_refresh.message;
                    showDataRefresh.value = true;
                    dataRefreshLoading.value = false;
                    setTimeout(() => showDataRefresh.value = false, 4000);
                }
            }

            const userInfo: UserInfo = {
                id: data.user.id,
                username: data.user.username,
                is_admin: data.user.is_admin,
                remember: rememberMe.value
            };

            persistLoginState(userInfo, rememberMe.value);

            try {
                markLoginSuccess();
            } catch (e) {
                console.warn('Failed to clear app timer:', e);
            }

            setTimeout(() => {
                router.push('/');
            }, 800);

        } catch (error: unknown) {
            console.error('Login Error:', error);
            showErrorToast(mapAuthError(error, 'Network error, please check connection'));
        } finally {
            loading.value = false;
            setTimeout(() => {
                showSuccess.value = false;
            }, 3000);
        }
    };

    const checkRememberedLogin = () => {
        const savedUser = localStorage.getItem(SESSION_KEYS.user);
        if (savedUser) {
            try {
                const user = JSON.parse(savedUser);
                if (user.remember) {
                    username.value = user.username;
                    rememberMe.value = true;
                }
            } catch (e) {
                localStorage.removeItem(SESSION_KEYS.user);
            }
        }
    };

    const showForgotPassword = () => {
        showForgotPasswordModal.value = true;
    };

    const closeForgotPassword = () => {
        showForgotPasswordModal.value = false;
    };

    const handleForgotPasswordSuccess = () => {
        showForgotPasswordModal.value = false;
        showSuccess.value = true;
        dataRefreshMessage.value = 'Password reset successful, please login with new password';
        setTimeout(() => {
            showSuccess.value = false;
        }, 3000);
    };

    const checkAutoLogout = () => {
        const autoLogoutMessage = consumeAutoLogoutReason();
        if (autoLogoutMessage) {
            errorMessage.value = autoLogoutMessage;
            showError.value = true;
            setTimeout(() => showError.value = false, 4000);
            showTopToast('info', 'Auto Logout', autoLogoutMessage);
        }
    };

    // Initializations
    checkRememberedLogin();
    checkAutoLogout();

    return {
        username,
        password,
        usernameFocused,
        passwordFocused,
        showPassword,
        rememberMe,
        loading,
        showSuccess,
        showDataRefresh,
        dataRefreshLoading,
        dataRefreshMessage,
        errorMessage,
        showError,
        showForgotPasswordModal,
        handleLogin,
        showForgotPassword,
        closeForgotPassword,
        handleForgotPasswordSuccess
    };
}
