<template>
	<div class="nf-wrap-content">
		<div class="nf-wrap-icon">
			<fai icon="fas fa-exclamation-triangle" />
		</div>

		<h1>{{ $t('nfPageNotFound') }}</h1>
		<p>{{ $t('nfPageNotFoundText') }}</p>

		<button @click="goBackOrHome" class="app-default-btn">{{ $t('nfGoBackButton') }}</button>
	</div>
</template>

<script>
import { routeHistory } from '@/router';
import { ROUTE } from '@/enums/enums';

/**
 * @vuese
 * @group NotFound
 * Displays a 404 error message when the requested page is not found.
 */

export default {
	name: 'NotFound',
	methods: {
		goBackOrHome() {
			const comingFromExternalSource = !routeHistory.referrer || !routeHistory.referrer.includes(window.location.hostname);

			if (window.history.length > 1 && !comingFromExternalSource) this.$router.go(-1);
			else this.$router.push({ name: ROUTE.HOME });
		},
	},
};
</script>

<style scoped>
.nf-wrap-content {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	text-align: center;
}

.nf-wrap-icon * {
	font-size: 75px;
	color: var(--main-color-warn);
}

h1 {
	font-size: 50px;
	margin: 20px 10px;
}

p {
	font-size: 25px;
	margin: 10px 0px 20px 0px;
}

button {
	padding: 10px 20px;
	border: none;
	border-radius: 5px;
	font-size: 17px;
	transition: background-color 0.3s ease;
	cursor: pointer;
	color: var(--main-color-light);
}
</style>
