import { MSG_TYPE, ROUTE } from '@/enums/enums.js';
import { network } from '../scripts/network.js';
import { store } from '../scripts/store.js';
import router from '@/router';

// Checks the access of the user to certain routes
// TODO: Change to correct route and test
export async function checkAccess(to, from, next) {
	return new Promise((resolve, reject) => {
		let user = store.getCurrentUser();
		network.getData(`/api/check-access?permission=${to.meta.permissions.join(',')}`, null, null, (err, data) => {
			// TODO: Remove mocked check
			if (user?.access?.permissionsGranted.includes(to.meta.permissions[0]) || to.meta.permissions.length == 0) {
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
			// if (err) {
			// 	next(false);
			// 	reject(new Error('Error'));
			// } else {
			// 	next();
			// 	resolve();
			// }
		});
	});
}
