<template>
	<div class="pr-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'pr-wrap-content'" />
		<h2 class="pr-header">{{ $t('prHeader') }}</h2>
		<div class="pr-wrap-inputs" @keyup.enter="resetPassword">
			<InputField
				v-model="passwordReset"
				:placeholder="$t('prReset')"
				:labelText="$t('prReset')"
				:inputType="'password'"
				@newValue="checkPassword"
			/>
			<InputField
				v-model="passwordResetRepeat"
				:placeholder="$t('prResetRepeat')"
				:labelText="$t('prResetRepeat')"
				:inputType="'password'"
				@newValue="checkPasswordRepeat"
			/>
		</div>
		<div class="pr-wrap-btn">
			<button :class="passwordsEntered ? 'app-default-btn' : 'app-disabled-btn'" @click="resetPassword">
				{{ $t('prConfirmPasswordReset') }}
			</button>
		</div>
	</div>
</template>

<script>
import { MSG_TYPE, TOAST_TYPE } from '@/enums/enums';
import { ROUTE } from '@/enums/enums.js';
import { useRoute } from 'vue-router';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import InputField from '@/components/general/InputField.vue';
/**
 * @vuese
 * @group Password Reset
 * Provides password reset functionalitys
 */
export default {
	name: 'PasswordReset',
	components: { InputField, LoadingSpinner },
	emits: [],
	props: {},
	watch: {},
	setup() {
		const route = useRoute();

		return { route };
	},
	data() {
		return {
			isLoading: false,
			passwordReset: null,
			passwordResetRepeat: null,
			resetCode: null,
		};
	},
	computed: {
		passwordsEntered() {
			let passwordsEntered = true;

			if (!this.$global.passwordIsValid(this.passwordReset, false)) passwordsEntered = false;
			else if (!this.passwordReset || this.passwordReset.trim() == '') passwordsEntered = false;
			else if (!this.passwordResetRepeat || this.passwordResetRepeat.trim() == '') passwordsEntered = false;
			else if (this.passwordReset !== this.passwordResetRepeat) passwordsEntered = false;

			return passwordsEntered;
		},
	},
	created() {
		this.resetCode = this.route.query.resetCode;
		if (!this.resetCode) this.$router.push({ name: ROUTE.HOME, query: { msg: MSG_TYPE.FORBIDDEN } });
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		checkPassword() {
			this.$global.passwordIsValid(this.passwordReset, true);
		},
		checkPasswordRepeat() {
			if (this.passwordReset != this.passwordResetRepeat) this.$global.showToast(TOAST_TYPE.WARN, this.$t('rePasswordsDontMatch'));
		},
		resetPassword() {
			this.isLoading = true;

			this.$network.postData('/api/user/password-reset', { resetCode: this.resetCode, password: this.passwordReset }, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('prPasswordResetSuccessfull'));
						this.$router.push({ name: ROUTE.HOME });
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
	},
};
</script>

<style scoped>
.pr-wrap-content {
	overflow: auto;
	position: relative;
}

.pr-header {
	margin-bottom: 20px;
	font-size: 30px;
	text-align: center;
	font-weight: normal;
}

.pr-wrap-inputs {
	max-width: 400px;
	margin: 10px 0px;
}

.pr-wrap-inputs {
	align-items: center;
	max-width: 400px;
	margin: 10px auto;
}

.pr-wrap-inputs > div {
	margin-bottom: 10px;
}

.pr-wrap-btn {
	width: 100%;
	text-align: center;
}

.pr-wrap-btn button {
	min-width: 200px;
	margin: 10px;
	padding: 10px 20px;
	font-size: 18px;
}
</style>
