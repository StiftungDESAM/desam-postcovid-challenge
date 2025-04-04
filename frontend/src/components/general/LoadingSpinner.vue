<template>
	<div class="ls-wrap-content" ref="wrapper">
		<fai icon="fas fa-spinner" />
		<p v-if="displayText">{{ displayText }}</p>
	</div>
</template>

<script>
/**
 * @vuese
 * @group General
 * Displays a loading spinner
 */
export default {
	name: 'LoadingSpinner',
	props: {
		wrapperClass: {
			type: String,
			required: false,
		},
		displayText: {
			type: String,
			required: false,
			default: null,
		},
		positioning: {
			type: String,
			required: false,
			default: 'absolute',
		},
	},
	mounted() {
		this.$refs.wrapper.style.position = this.positioning || 'absolute';
		window.addEventListener('resize', this.resizeListener);
	},
	beforeUnmount() {
		window.removeEventListener('resize', this.resizeListener);
		if (this.wrapperClass) document.querySelector(`.${this.wrapperClass}`).style.overflowY = 'auto';
	},
	methods: {
		resizeListener() {
			if (document.querySelector('.ls-wrap-content') && this.wrapperClass) this.adjustLoadingPosition();
		},
		adjustLoadingPosition() {
			let wrapper = document.querySelector(`.${this.wrapperClass}`);
			wrapper.style.overflowY = 'hidden';
			this.$nextTick(() => {
				if (document.querySelector('.ls-wrap-content')) document.querySelector('.ls-wrap-content').style.top = `${wrapper.scrollY}px`;
			});
		},
	},
};
</script>

<style scoped>
.ls-wrap-content {
	width: 100%;
	height: 100%;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	z-index: 1;
	background-color: var(--main-color-dark-bb);
}

.ls-wrap-content ::v-deep(svg) {
	filter: drop-shadow(2px 2px 1px var(--main-color-dark));
	font-size: 55px;
	animation: spin 1.5s linear infinite;
}

.ls-wrap-content * {
	color: var(--main-color-5);
}

.ls-wrap-content p {
	margin-top: 10px;
}
</style>
