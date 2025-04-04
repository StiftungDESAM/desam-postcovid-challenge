import { MSG_TYPE, REQUEST_STATUS, ROUTE, TOAST_TYPE } from '../enums/enums.js';
import i18n from '../translations/i18n.js';
import axios from 'axios';
import router from '@/router';
import camelcaseKeys from 'camelcase-keys';
import decamelizeKeys from 'decamelize-keys';
import { store } from './store.js';

export const network = {
	t: i18n.global.t,
	handleResponse(err, route, cb) {
		let status = this.getResponseStatus(err);

		let msg = status == REQUEST_STATUS.UNAUTHORIZED ? MSG_TYPE.UNAUTHORIZED : status == REQUEST_STATUS.FORBIDDEN ? MSG_TYPE.FORBIDDEN : null;

		const routeLogin = route.includes('login');
		const routeLogout = route.includes('logout');

		if (msg && !(routeLogin || routeLogout)) {
			store.setForceUserLogout(true);
			if (router.currentRoute.value.name == ROUTE.HOME) {
				router.replace({ name: ROUTE.HOME, query: { msg: msg } }).then(() => {
					window.location.reload();
				});
			} else router.push({ name: ROUTE.HOME, query: { msg: msg } });
		} else if (msg && routeLogin) cb({ msg: msg, status: status }, null);
		else if (routeLogout) cb(null, null);
		else cb({ msg: this.getResponseMsg(err), status: status }, null);
	},
	getResponseStatus(err) {
		return err.response && err.response.status ? err.response.status : REQUEST_STATUS.BAD_REQUEST;
	},
	getResponseMsg(err) {
		return err.response.data && err.response.data.msg
			? err.response.data.msg
			: `${this.t('errUnexpectedError')} (${this.getResponseStatus(err)})`;
	},
	getHeaders() {
		return store.getToken() ? { headers: { Authorization: `Bearer ${store.getToken()}` } } : {};
	},
	getData: async function (route, data, options, cb) {
		axios
			.get(route, { ...options, ...this.getHeaders(), params: decamelizeKeys(data, { deep: true }) })
			.then((res) => {
				cb(null, camelcaseKeys(res.data, { deep: true }));
			})
			.catch((err) => {
				this.handleResponse(err, route, cb);
			});
	},
	postData: async function (route, data, options, cb) {
		axios
			.post(route, decamelizeKeys(data, { deep: true }), { ...options, ...this.getHeaders() })
			.then((res) => {
				cb(null, camelcaseKeys(res.data, { deep: true }));
			})
			.catch((err) => {
				this.handleResponse(err, route, cb);
			});
	},
	putData: async function (route, data, options, cb) {
		axios
			.put(route, decamelizeKeys(data, { deep: true }), { ...options, ...this.getHeaders() })
			.then((res) => {
				cb(null, camelcaseKeys(res.data, { deep: true }));
			})
			.catch((err) => {
				this.handleResponse(err, route, cb);
			});
	},
	patchData: async function (route, data, options, cb) {
		axios
			.patch(route, decamelizeKeys(data, { deep: true }), { ...options, ...this.getHeaders() })
			.then((res) => {
				cb(null, camelcaseKeys(res.data, { deep: true }));
			})
			.catch((err) => {
				this.handleResponse(err, route, cb);
			});
	},
	deleteData: async function (route, data, options, cb) {
		axios
			.delete(route, { ...options, ...this.getHeaders(), data: decamelizeKeys(data, { deep: true }) })
			.then((res) => {
				cb(null, camelcaseKeys(res.data, { deep: true }));
			})
			.catch((err) => {
				this.handleResponse(err, route, cb);
			});
	},
};
