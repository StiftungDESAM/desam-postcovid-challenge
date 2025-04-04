export const toastOptions = {
	transition: 'Vue-Toastification__bounce',
	maxToasts: 10,
	newestOnTop: true,
	position: 'top-right',
	timeout: 3000,
	closeOnClick: true,
	pauseOnFocusLoss: true,
	pauseOnHover: true,
	draggable: true,
	draggablePercent: 0.75,
	showCloseButtonOnHover: false,
	hideProgressBar: false,
	closeButton: 'button',
	icon: true,
	rtl: false,
	toastDefaults: {
		warning: {
			toastClassName: 'ap-warning-toast',
		},
	},
	filterBeforeCreate: (toast, toasts) => {
		return !toasts.some((t) => t.content === toast.content) ? toast : null;
	},
};
