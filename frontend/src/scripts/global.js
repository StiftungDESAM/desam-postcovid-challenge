import { SORT_ORDER, TOAST_TYPE } from '../enums/enums.js';
import { useToast } from 'vue-toastification';
import i18n from '../translations/i18n.js';

export const global = {
	toast: useToast(),
	t: i18n.global.t,
	showToast(type, msg) {
		if (type == TOAST_TYPE.INFO) this.toast.info(msg);
		else if (type == TOAST_TYPE.SUCCESS) this.toast.success(msg);
		else if (type == TOAST_TYPE.WARN) this.toast.warning(msg);
		else this.toast.error(msg);
	},
	emailIsValid(email) {
		const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
		return emailPattern.test(email);
	},
	dobIsValid(dob) {
		const age = new Date().getFullYear() - new Date(dob).getFullYear();
		return age >= 18 && age <= 120;
	},
	passwordIsValid(password, showToast = false) {
		if (password) {
			let isValid = true;
			let warnText = null;

			const uppercasePattern = /[A-Z]/;
			const digitPattern = /\d/;
			const specialCharPattern = /[!@#$%^&*()_+{}\[\]:;"'<>,.?/\\|`~]/;

			if (password.length < 9) {
				warnText = this.t('reInvalidPasswordLength');
				isValid = false;
			} else if (!uppercasePattern.test(password)) {
				warnText = this.t('reInvalidPasswordUpperCase');
				isValid = false;
			} else if (!digitPattern.test(password)) {
				warnText = this.t('reInvalidPasswordDigit');
				isValid = false;
			} else if (!specialCharPattern.test(password)) {
				warnText = this.t('reInvalidPasswordSpecialChar');
				isValid = false;
			}

			if (showToast && !isValid) this.showToast(TOAST_TYPE.WARN, warnText);

			return isValid;
		} else return false;
	},
	getNestedValue(obj, path) {
		return path.split('.').reduce((acc, key) => acc?.[key], obj);
	},
	sortArray(arr, sortBy, order) {
		return arr.sort((a, b) => {
			let valA = sortBy.map((prop) => this.getNestedValue(a, prop) || '').join(' ');
			let valB = sortBy.map((prop) => this.getNestedValue(b, prop) || '').join(' ');

			if (valA == null) valA = '';
			if (valB == null) valB = '';

			// Handle dates
			if (!isNaN(Date.parse(valA)) && !isNaN(Date.parse(valB))) {
				valA = new Date(valA);
				valB = new Date(valB);
			}
			// Handle booleans
			else if (typeof valA === 'boolean' && typeof valB === 'boolean') {
				valA = valA ? 1 : 0;
				valB = valB ? 1 : 0;
			}
			// Handle numbers
			else if (!isNaN(valA) && !isNaN(valB)) {
				valA = Number(valA);
				valB = Number(valB);
			}
			// Handle strings (case insensitive)
			else {
				valA = valA.toString().toLowerCase();
				valB = valB.toString().toLowerCase();
			}

			let comparison = valA > valB ? 1 : valA < valB ? -1 : 0;
			return order == SORT_ORDER.DESC ? -comparison : comparison;
		});
	},
	getPagination(amountElements, amountElementsPerPage) {
		let pages = [];
		let totalPages = Math.ceil(amountElements / amountElementsPerPage);

		if (amountElements > 1) {
			for (let i = 0; i < totalPages; i++) {
				let start = i * amountElementsPerPage;
				let end = Math.min(start + amountElementsPerPage - 1, amountElements - 1);

				pages.push({ start, end });
			}
		} else if (amountElements == 1) pages = [{ start: 1, end: null }];
		else pages = [{ start: 0, end: null }];

		return pages;
	},
	formatDate(inputDate, format, short) {
		let date = typeof inputDate === 'string' ? new Date(inputDate) : inputDate;
		if (format == 'de') {
			return date
				.toLocaleString('de-DE', {
					day: '2-digit',
					month: '2-digit',
					year: 'numeric',
					hour: !short ? '2-digit' : undefined,
					minute: !short ? '2-digit' : undefined,
					second: !short ? '2-digit' : undefined,
					hour12: false,
				})
				.replace(',', '');
		} else if (short) return date.toISOString().split('.')[0].split('T')[0];
		else return date.toISOString().split('.')[0];
	},
	valueIsNotAvailable(value, includeEmptyString = false, includeZero = false) {
		const isNullOrUndefined = value == null;
		const isEmpty = value === '';
		const isZero = value === 0;

		return isNullOrUndefined || (includeEmptyString && isEmpty) || (includeZero && isZero);
	},
};
