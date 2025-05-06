<template>
	<div class="re-wrap-content">
		<LoadingSpinner v-if="isLoading" :wrapperClass="'re-wrap-content'" />
		<h2>{{ $t('reRegistration') }}</h2>
		<div class="re-wrap-general">
			<h3>{{ $t('reGeneralInformation') }}</h3>
			<div class="re-wrap-general-fields" @keyup.enter="allInformationEntered ? registerUser() : null">
				<InputField v-model="newUser.user.firstName" :placeholder="$t('reFirstName')" :labelText="$t('reFirstName')" />
				<InputField v-model="newUser.user.lastName" :placeholder="$t('reLastName')" :labelText="$t('reLastName')" />
				<InputField v-model="newUser.user.dateOfBirth" :labelText="$t('reDateOfBirth')" :inputType="'date'" @newValue="checkDOB" />
				<SelectField v-model="newUser.user.gender" :placeholder="$t('reSelectGender')" :labelText="$t('reGender')" :options="genderOptions" />
			</div>
		</div>
		<div class="re-wrap-user" @keyup.enter="allInformationEntered ? registerUser() : null">
			<h3>{{ $t('reUserInformation') }}</h3>
			<div class="re-wrap-user-fields">
				<SelectField v-model="newUser.access.role" :placeholder="$t('reSelectRole')" :labelText="$t('reRole')" :options="roleOptions" />
				<div class="re-wrap-functionalities">
					<p>{{ $t('reFunctionalities') }}?</p>
					<div class="re-wrap-user-checkboxes">
						<InputField
							v-for="permission in permissions"
							:key="permission"
							v-model="newUser.access.permissionsRequested[permission]"
							:labelText="$t(permission)"
							:inputType="'checkbox'"
						/>
					</div>
				</div>
			</div>
		</div>
		<div class="re-wrap-access" @keyup.enter="allInformationEntered ? registerUser() : null">
			<h3>{{ $t('reAccessInformation') }}</h3>
			<div class="re-wrap-access-fields">
				<InputField
					v-model="newUser.credentials.email"
					:placeholder="$t('reEmail')"
					:labelText="$t('reEmail')"
					:inputType="'email'"
					@newValue="checkEmail"
				/>
				<div class="re-wrap-password">
					<transition name="fade">
						<div v-if="showPasswordHint" class="re-wrap-password-hint">
							<p>
								<fai
									v-if="!$global.checkPasswordLength(newUser.credentials.password)"
									icon="fas fa-circle-xmark"
									class="re-invalid"
								/>
								<fai v-else icon="fas fa-circle-check" class="re-valid" />
								<span>{{ $t('rePasswordLength') }}</span>
							</p>
							<p>
								<fai
									v-if="!$global.checkPasswordUpperCase(newUser.credentials.password)"
									icon="fas fa-circle-xmark"
									class="re-invalid"
								/>
								<fai v-else icon="fas fa-circle-check" class="re-valid" />
								<span>{{ $t('reUpperCaseLetter') }}</span>
							</p>
							<p>
								<fai
									v-if="!$global.checkPasswordLowerCase(newUser.credentials.password)"
									icon="fas fa-circle-xmark"
									class="re-invalid"
								/>
								<fai v-else icon="fas fa-circle-check" class="re-valid" />
								<span>{{ $t('reLowerCaseLetter') }}</span>
							</p>
							<p>
								<fai
									v-if="!$global.checkPasswordSpecialLetter(newUser.credentials.password)"
									icon="fas fa-circle-xmark"
									class="re-invalid"
								/>
								<fai v-else icon="fas fa-circle-check" class="re-valid" />
								<span>{{ $t('reSpecialLetter') }}</span>
							</p>
						</div>
					</transition>
					<InputField
						v-model="newUser.credentials.password"
						:placeholder="$t('rePassword')"
						:labelText="$t('rePassword')"
						:inputType="'password'"
						:autocompleteType="'new-password'"
						@newValue="checkPassword"
						@focus="showPasswordHint = true"
						@blur="showPasswordHint = false"
					/>
				</div>
				<InputField
					v-model="passwordRepeat"
					:placeholder="$t('rePasswordRepeat')"
					:labelText="$t('rePasswordRepeat')"
					:inputType="'password'"
					:autocompleteType="'new-password'"
					@newValue="checkPasswordRepeat"
				/>
			</div>
		</div>
		<div class="re-wrap-links">
			<div class="re-wrap-legal-notice">
				<p>
					<InputField v-model="acceptedLegalNotice" :inputType="'checkbox'" />
					<span class="re-underline-text" @click="toTermsOfUse">{{ $t('reTermsOfUse') }}</span>
					<span>{{ $t('reAnd') }}</span>
					<span class="re-underline-text" @click="toDataPrivacy">{{ $t('reDataPrivacy') }}</span>
					<span>{{ $t('reAccept') }}</span>
				</p>
			</div>
			<em class="re-login-text">
				<span>{{ $t('reAccountAvailable') }}</span
				>?
				<span>{{ $t('reGoTo') }}</span>
				<span class="re-underline-text" @click="$emit('openLogin')">{{ $t('reLogin') }}</span
				>.
			</em>
		</div>
		<div class="re-wrap-btn">
			<button :class="allInformationEntered ? 'app-success-btn' : 'app-disabled-btn'" @click="registerUser">
				{{ $t('reFinishRegistration') }}
			</button>
		</div>
	</div>
</template>

<script>
import { GENDER, ROLE, ROUTE, PERMISSION, TOAST_TYPE, REQUEST_STATUS } from '@/enums/enums';
import { useRouter } from 'vue-router';
import InputField from '@/components/general/InputField.vue';
import SelectField from '@/components/general/SelectField.vue';
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
/**
 * @vuese
 * @group Home
 * Provides registration functionality
 */
export default {
	name: 'Registration',
	components: {
		InputField,
		SelectField,
		LoadingSpinner,
	},
	emits: ['openLogin', 'closeRegistration'],
	props: {},
	watch: {},
	setup() {
		const router = useRouter();
		return { router };
	},
	data() {
		return {
			genderOptions: Object.values(GENDER),
			roleOptions: Object.values(ROLE).filter((it) => ![ROLE.SUPER_ADMIN, ROLE.ADMIN].includes(it)),
			permissions: Object.values(PERMISSION).filter((it) => ![PERMISSION.SUPER_ADMIN, PERMISSION.ADMIN].includes(it)),
			newUser: {
				user: {
					firstName: null,
					lastName: null,
					dateOfBirth: null,
					gender: null,
				},
				access: {
					role: null,
					permissionsRequested: {},
				},
				credentials: {
					email: null,
					password: null,
				},
			},
			passwordRepeat: null,
			acceptedLegalNotice: false,
			isLoading: false,
			showPasswordHint: false,
		};
	},
	computed: {
		allInformationEntered() {
			let allInfoValid = true;

			if (!this.newUser.user.firstName) allInfoValid = false;
			else if (!this.newUser.user.lastName) allInfoValid = false;
			else if (!this.$global.dobIsValid(this.newUser.user.dateOfBirth)) allInfoValid = false;
			else if (!this.newUser.user.gender) allInfoValid = false;
			else if (!this.newUser.access.role) allInfoValid = false;
			else if (!Object.values(this.newUser.access.permissionsRequested).some((it) => it)) allInfoValid = false;
			else if (!this.$global.emailIsValid(this.newUser.credentials.email)) allInfoValid = false;
			else if (!this.$global.passwordIsValid(this.newUser.credentials.password, false)) allInfoValid = false;
			else if (this.newUser.credentials.password != this.passwordRepeat) allInfoValid = false;

			return allInfoValid && this.acceptedLegalNotice;
		},
	},
	methods: {
		toTermsOfUse() {
			const routeData = this.router.resolve({ name: ROUTE.LEGAL_NOTICE, hash: '#term-of-use' });
			window.open(routeData.href, '_blank');
		},
		toDataPrivacy() {
			const routeData = this.router.resolve({ name: ROUTE.LEGAL_NOTICE, hash: '#data-privacy' });
			window.open(routeData.href, '_blank');
		},
		checkDOB(dob) {
			if (dob && !dob.startsWith('0') && !this.$global.dobIsValid(dob)) this.$global.showToast(TOAST_TYPE.WARN, this.$t('reInvalidDate'));
		},
		checkEmail(email) {
			if (email && !this.$global.emailIsValid(email)) this.$global.showToast(TOAST_TYPE.WARN, this.$t('reInvalidEmail'));
		},
		checkPassword() {
			this.$global.passwordIsValid(this.newUser.credentials.password, true);
		},
		checkPasswordRepeat() {
			if (this.newUser.credentials.password != this.passwordRepeat) this.$global.showToast(TOAST_TYPE.WARN, this.$t('rePasswordsDontMatch'));
		},
		registerUser() {
			this.isLoading = true;

			let user = JSON.parse(JSON.stringify(this.newUser));
			user.access.permissionsRequested = Object.keys(user.access.permissionsRequested).filter((key) => user.access.permissionsRequested[key]);
			user.access.role = [user.access.role];

			this.$network.postData('/api/user/registration', user, null, (err, data) => {
				try {
					if (!err) {
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('reRegistrationSuccessfull'));
						this.$emit('closeRegistration', true);
					} else if (err.status == REQUEST_STATUS.CONFLICT) this.$global.showToast(TOAST_TYPE.WARN, this.$t('reEmailAlreadyUsed'));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
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
.re-wrap-content {
	max-width: 80vw;
	max-height: 90vh;
	padding: 20px;
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	overflow: auto;
	position: relative;
	background-color: var(--main-color-1);
}

.re-wrap-content h2 {
	font-size: 30px;
	text-align: center;
	font-weight: normal;
}

.re-wrap-general,
.re-wrap-user,
.re-wrap-access {
	width: 100%;
	margin: 10px 0px;
}

.re-wrap-general-fields,
.re-wrap-user-fields,
.re-wrap-access-fields {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
	position: relative;
}

.re-wrap-general h3,
.re-wrap-user h3,
.re-wrap-access h3 {
	margin-bottom: 10px;
	text-decoration: underline;
	font-weight: normal;
}

.re-wrap-functionalities {
	flex: 1 1 200px;
	margin: 0px 10px;
}

.re-wrap-functionalities p {
	margin-bottom: 10px;
}

.re-wrap-user-checkboxes {
	display: flex;
	justify-content: flex-start;
	align-items: flex-start;
	flex-flow: wrap;
}

.re-wrap-user-checkboxes > div {
	max-width: 200px;
}

.re-wrap-links {
	width: 100%;
	text-align: center;
	margin: 5px 0px;
}

.re-wrap-legal-notice {
	margin-bottom: 10px;
}

.re-wrap-legal-notice p {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.re-wrap-legal-notice div,
.re-wrap-legal-notice p span,
.re-login-text span {
	margin-left: 5px;
	display: inline-block;
	flex: 0 0 0px;
}

.re-underline-text {
	text-decoration: underline;
	cursor: pointer;
}

.re-wrap-btn {
	width: 100%;
	text-align: center;
}

.re-wrap-btn button {
	margin-top: 10px;
	padding: 10px 20px;
	font-size: 20px;
}

.re-wrap-password {
	flex: 1 1 200px;
	position: relative;
}

.re-wrap-password-hint {
	width: calc(100% - 20px);
	padding: 5px 10px;
	position: absolute;
	top: -110px;
	left: 50%;
	transform: translateX(-50%);
	z-index: 10;
	white-space: nowrap;
	border: 1px solid var(--main-color-light);
	border-radius: 5px;
	background-color: var(--main-color-1);
}

.re-wrap-password-hint p {
	width: 100%;
	margin: 5px 0px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.re-wrap-password-hint p svg {
	flex: 1 1 25px;
	margin-right: 10px;
	font-size: 20px;
}

.re-wrap-password-hint p span {
	flex: 1 1 100%;
	max-width: calc(100% - 25px);
	white-space: wrap;
}

.re-invalid * {
	color: var(--main-color-error);
}

.re-valid * {
	color: var(--main-color-success);
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
.fade-enter-to,
.fade-leave-from {
	opacity: 1;
}
</style>
