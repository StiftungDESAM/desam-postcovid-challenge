export const store = {
	data: {
		stayLoggedIn: false,
		forceUserLogout: false,
		user: null,
		token: null,
		tokenExpiration: null,
	},
	reinitializeStore: function () {
		// Check if user is forced to logout
		this.data.forceUserLogout = sessionStorage.getItem('forceUserLogout');

		if (!this.data.forceUserLogout) {
			this.data.forceUserLogout = false;

			// Check for stayLoggedIn
			this.data.stayLoggedIn = localStorage.getItem('stayLoggedIn') ? true : false;

			// Check for user
			const localStorageUser = localStorage.getItem('user');
			const sessionStorageUser = sessionStorage.getItem('user');
			if (this.data.stayLoggedIn) this.data.user = localStorageUser ? JSON.parse(localStorageUser) : null;
			else this.data.user = sessionStorageUser ? JSON.parse(sessionStorageUser) : null;

			// Check for token
			if (this.data.stayLoggedIn) this.data.token = localStorage.getItem('token') || null;
			else this.data.token = sessionStorage.getItem('token') || null;

			// Check for tokenExpiration
			if (this.data.stayLoggedIn) this.data.tokenExpiration = localStorage.getItem('tokenExpiration') || null;
			else this.data.tokenExpiration = sessionStorage.getItem('tokenExpiration') || null;
		}
	},
	getStayLoggedIn: function () {
		return this.data.stayLoggedIn;
	},
	setStayLoggedIn: function (stayLoggedIn) {
		this.data.stayLoggedIn = stayLoggedIn;

		if (stayLoggedIn) localStorage.setItem('stayLoggedIn', 'true');
		else localStorage.removeItem('stayLoggedIn');
	},
	getCurrentUser: function () {
		return this.data.user;
	},
	setCurrentUser: function (newUser) {
		this.data.user = newUser;

		if (this.data.stayLoggedIn) localStorage.setItem('user', JSON.stringify(newUser));
		else sessionStorage.setItem('user', JSON.stringify(newUser));
	},
	getToken: function () {
		return this.data.token;
	},
	setToken: function (token) {
		this.data.token = token;

		if (this.data.stayLoggedIn) localStorage.setItem('token', token);
		else sessionStorage.setItem('token', token);
	},
	getTokenExpiration: function () {
		return this.data.tokenExpiration;
	},
	setTokenExpiration: function (tokenExpiration) {
		this.data.tokenExpiration = tokenExpiration;

		if (this.data.stayLoggedIn) localStorage.setItem('tokenExpiration', tokenExpiration);
		else sessionStorage.setItem('tokenExpiration', tokenExpiration);
	},
	getForceUserLogout: function () {
		return this.data.forceUserLogout;
	},
	setForceUserLogout: function (force) {
		this.data.forceUserLogout = force;

		sessionStorage.setItem('forceUserLogout', force);
	},
	clearStore: function () {
		this.data = {
			stayLoggedIn: false,
			forceUserLogout: false,
			user: null,
			token: null,
			tokenExpiration: null,
		};

		localStorage.clear();
		sessionStorage.clear();
	},
};
