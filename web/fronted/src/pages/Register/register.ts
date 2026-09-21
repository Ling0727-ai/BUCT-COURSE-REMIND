import { ref, reactive, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import rsaCrypto from '@/utils/rsa-crypto';
import { useToast } from '@/composables/useToast';
import { isValidEmail as isValidAuthEmail, mapAuthError, sendVerificationCode, verifyVerificationCode } from '@/pages/Auth/auth';
import { registerUser } from './register.api';
import { RegisterFormData } from './register.data';

export function useRegisterService() {
    const router = useRouter();
    const { showToast } = useToast();

    // State
    const formData = reactive<RegisterFormData>({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        captcha: '',
        studentId: '',
        sPassword: '',
        agreeTerms: false
    });

    const showPassword = ref(false);
    const showConfirmPassword = ref(false);
    const showSPassword = ref(false);

    // Focus states
    const usernameFocused = ref(false);
    const emailFocused = ref(false);
    const passwordFocused = ref(false);
    const confirmPasswordFocused = ref(false);
    const captchaFocused = ref(false);

    const loading = ref(false);
    const showSuccess = ref(false);
    const errorMessage = ref('');
    const captchaCooldown = ref(0);
    const captchaSent = ref(false);
    let captchaInterval: number | null = null; // using number for browser interval id

    // Computed
    const isValidEmail = computed(() => {
        return isValidAuthEmail(formData.email);
    });

    const passwordStrength = computed(() => {
        if (formData.password.length === 0) return '';
        if (formData.password.length < 6) return 'weak';
        if (formData.password.length < 10) return 'medium';
        return 'strong';
    });

    const strengthLabel = computed(() => {
        const map: Record<string, string> = {
            '': '',
            weak: '弱',
            medium: '中',
            strong: '强'
        };
        return map[passwordStrength.value] || '';
    });

    const isFormValid = computed(() => {
        return formData.username.length >= 3 &&
            isValidEmail.value &&
            formData.password.length >= 6 &&
            formData.password === formData.confirmPassword &&
            formData.captcha.length === 6 &&
            formData.agreeTerms;
    });

    // Actions
    const showErrorMsg = (msg: string) => {
        errorMessage.value = msg;
        showToast('error', 'Error', msg);
        setTimeout(() => { errorMessage.value = ''; }, 3000);
    };

    const handleSendCaptcha = async () => {
        if (!isValidEmail.value) {
            showErrorMsg('请输入有效的邮箱地址');
            return;
        }

        if (captchaCooldown.value > 0) return;

        try {
            const data = await sendVerificationCode(formData.email);

            captchaCooldown.value = 60;
            captchaSent.value = true;

            if (data.test_mode && data.verification_code) {
                 showToast('info', 'Test Mode', `Verification Code: ${data.verification_code}`);
            } else {
                 showToast('success', 'Sent', '验证码已发送到邮箱');
            }

            if (captchaInterval) clearInterval(captchaInterval);
            captchaInterval = window.setInterval(() => {
                captchaCooldown.value--;
                if (captchaCooldown.value <= 0) {
                    if (captchaInterval) clearInterval(captchaInterval);
                    captchaSent.value = false;
                }
            }, 1000);

        } catch (error: unknown) {
             showErrorMsg(mapAuthError(error, '发送验证码失败'));
        }
    };

    const handleRegister = async () => {
        if (!isFormValid.value) {
             showErrorMsg('请完善所有必填信息');
             return;
        }

        loading.value = true;
        errorMessage.value = '';

        try {
            //Verify code first
            await verifyVerificationCode(formData.email, formData.captcha);

            // Encrypt data
            const requestData = await rsaCrypto.createEncryptedRequest({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                student_id: formData.studentId || '',
                s_password: formData.sPassword || ''
            });

            // Register
            const data = await registerUser(requestData);

            // Success
            showSuccess.value = true;
            showToast('success', '注册成功', '正在跳转到登录页面...');

            // Reset form
            formData.username = '';
            formData.email = '';
            formData.password = '';
            formData.confirmPassword = '';
            formData.captcha = '';
            formData.studentId = '';
            formData.sPassword = '';
            formData.agreeTerms = false;

            if(data.data_refresh) {
                 const msg = data.data_refresh.message || (data.data_refresh.success ? `Refreshed ${data.data_refresh.count} records` : 'Refresh failed');
                 showToast(data.data_refresh.success ? 'success' : 'error', 'Data Refresh', msg);
            }

            setTimeout(() => {
                router.push('/login');
            }, 1500);

        } catch (error: unknown) {
            console.error('Register Error:', error);
            showErrorMsg(mapAuthError(error, '注册失败'));
        } finally {
            loading.value = false;
        }
    };

    // Lifecycle
    onUnmounted(() => {
        if (captchaInterval) {
            clearInterval(captchaInterval);
        }
    });

    return {
        formData,
        showPassword,
        showConfirmPassword,
        showSPassword,
        usernameFocused,
        emailFocused,
        passwordFocused,
        confirmPasswordFocused,
        captchaFocused,
        loading,
        showSuccess,
        errorMessage,
        captchaCooldown,
        captchaSent,
        isValidEmail,
        passwordStrength,
        strengthLabel,
        isFormValid,
        handleSendCaptcha,
        handleRegister
    };
}
