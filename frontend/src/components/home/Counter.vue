<template>
	<div class="co-wrap-content">
		<p class="co-amount">{{ stat.amount }}</p>
		<p class="co-translation">{{ $t(stat.translation) }}</p>
	</div>
</template>

<script>
/**
 * @vuese
 * @group Home
 * Counter for stats about the system
 */
export default {
	name: 'Counter',
	props: {
		stat: {
			type: Object,
			required: true,
		},
	},
};
</script>

<style scoped>
.co-wrap-content {
	padding: 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
}

.co-amount {
	font-size: 50px;
	margin-bottom: 10px;
}

.co-translation {
	font-size: 25px;
}
</style>
