import { MSG_TYPE, ROUTE } from '@/enums/enums.js';
import { network } from '../scripts/network.js';
import router from '@/router';

// Checks the access of the user to certain routes
export async function checkAccess(to, from, next) {
	return new Promise((resolve, reject) => {
		if (to.meta.permissions.length > 0) {
			network.getData(`/api/user/access-check?permissions=${to.meta.permissions.join(';')}`, null, null, (err, data) => {
				if (!err) {
					next();
					resolve();
				} else {
					next(false);
					if (router.currentRoute.value.name == ROUTE.HOME) {
						router.replace({ name: ROUTE.HOME, query: { msg: MSG_TYPE.FORBIDDEN } }).then(() => {
							window.location.reload();
						});
					} else router.push({ name: ROUTE.HOME, query: { msg: MSG_TYPE.FORBIDDEN } });

					reject(new Error('Error'));
				}
			});
		} else {
			next();
			resolve();
		}
	});
}
