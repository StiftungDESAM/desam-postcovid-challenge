<template>
	<div class="ho-wrap-content">
		<h1 class="ho-heading">{{ $t('hoPostCovidChallenge') }}</h1>
		<transition name="fade">
			<div v-if="stats" class="ho-wrap-counters">
				<Counter v-for="stat in stats" :key="stat.type" :stat="stat" />
			</div>
		</transition>
		<div v-if="!stats" class="ho-loading-data-placeholder">{{ $t('hoLoadingStats') }}...</div>
		<div v-if="currentUser" class="ho-wrap-dashboard">
			<Dashboard />
		</div>
		<h2 class="ho-subheading">{{ $t('hoHighlightedStudies') }}</h2>
		<transition name="fade">
			<div v-if="highlights" class="ho-wrap-highlights">
				<StudyHighlights v-for="highlight in highlights" :key="highlight.id" :highlight="highlight" />
			</div>
		</transition>
		<div v-if="highlights?.length == 0" class="ho-no-highlights">
			<p>{{ $t('hoNoHighlightsAvailable') }}</p>
		</div>
		<div v-if="!highlights" class="ho-loading-data-placeholder">{{ $t('hoLoadingHighlights') }}...</div>
		<div class="ho-wrap-buttons">
			<button class="app-success-btn" @click="showVideo">{{ $t('hoShowVideoTour') }} <fai icon="fas fa-video" /></button>
			<button class="app-success-btn" @click="downloadExampleData">{{ $t('hoDownloadExampleData') }} <fai icon="fas fa-download" /></button>
		</div>
		<div v-if="showVideoStream" class="ho-wrap-video-stream" @click="hideVideo">
			<template v-if="canPlayVideo">
				<video v-if="showVideo" ref="videoPlayer" width="640" height="360" controls @click.stop="" @error="canPlayVideo = false">
					<source :src="videoSrc" type="video/mp4" />
					<div class="ho-video-fallback">
						{{ $t('hoBrowserDoesntSupportVideo') }}
						<button class="app-default-btn" @click="downloadVideo">{{ $t('hoDownloadVideo') }} <fai icon="fas fa-video" /></button>
					</div>
				</video>
			</template>
			<template v-else>
				<div class="ho-video-fallback">
					<p>{{ $t('hoVideoCantBePlayed') }}</p>
					<button class="app-default-btn" @click="downloadVideo">{{ $t('hoDownloadVideo') }} <fai icon="fas fa-video" /></button>
				</div>
			</template>
		</div>
		<div v-if="!currentUser" class="ho-wrap-registration-login">
			<em class="ho-motivation-text">
				<span>{{ $t('hoContributeData') }}</span>
				<span>{{ $t('hoCreateAccount') }}</span>
			</em>
			<button class="app-default-btn" @click="openRegistration">{{ $t('hoOpenRegistration') }}</button>
			<em class="ho-login-text">
				<span>{{ $t('hoAccountAvailable') }}</span>
				<span>{{ $t('hoGoTo') }}</span>
				<span @click="openLogin">{{ $t('hoLogin') }}</span
				>.
			</em>
		</div>
		<div v-show="showLogin || showRegistration" class="ho-center-content" @click="closeWindow(false)" @mousedown="clickDownRegistered = true">
			<Login
				v-show="showLogin"
				@click.stop
				@mousedown.stop
				@openRegistration="openRegistration"
				@closeLogin="closeWindow($event)"
				@loginUser="loginUser"
			/>
			<Registration v-show="showRegistration" @click.stop @mousedown.stop @openLogin="openLogin" @closeRegistration="closeWindow($event)" />
		</div>
	</div>
</template>

<script>
import { TOAST_TYPE, MSG_TYPE, ROUTE } from '@/enums/enums';
import { useRouter } from 'vue-router';
import { useRoute } from 'vue-router';
import Counter from '@/components/home/Counter.vue';
import Dashboard from '@/components/home/Dashboard.vue';
import StudyHighlights from '@/components/home/StudyHighlights.vue';
import Login from '@/components/home/Login.vue';
import Registration from '@/components/home/Registration.vue';
import videoSrc from '@/assets/img/TourVideo_Music.mp4';
import codebookSrc from '@/assets/example/codebook.csv';
import dataSrc from '@/assets/example/data.csv';
import codebookPreVitaCovSrc from '@/assets/example/Codebook  MVP_mnppvcovpromis.csv';
import dataPreVitaCovSrc from '@/assets/example/Daten MVP_mnppvcovpromis.csv';

/**
 * @vuese
 * @group Home
 * Home of the website
 */
export default {
	name: 'Home',
	components: {
		Counter,
		Dashboard,
		StudyHighlights,
		Login,
		Registration,
	},
	emits: ['loginUser', 'logoutUser'],
	props: {
		userLoggedInKey: {
			type: Boolean,
			required: true,
		},
	},
	watch: {
		userLoggedInKey: {
			handler: function () {
				this.currentUser = this.$store.getCurrentUser();
			},
		},
	},
	setup() {
		const router = useRouter();
		const route = useRoute();
		const routes = router.options.routes;
		const enumROUTE = ROUTE;

		return { routes, route, enumROUTE };
	},
	data() {
		return {
			currentUser: this.$store.getCurrentUser(),
			showLogin: false,
			showRegistration: false,
			clickDownRegistered: false,
			amountHighlights: 3,
			stats: null,
			highlights: null,
			showVideoStream: false,
			videoSrc: videoSrc,
			codebookSrc: codebookSrc,
			dataSrc: dataSrc,
			codebookPreVitaCovSrc: codebookPreVitaCovSrc,
			dataPreVitaCovSrc: dataPreVitaCovSrc,
			canPlayVideo: true,
		};
	},
	computed: {},
	created() {
		this.queryStatsAndHighlights();
	},
	mounted() {
		this.checkForQueryMsg();
		window.addEventListener('resize', this.resizeListener);
	},
	beforeUnmount() {
		window.removeEventListener('resize', this.resizeListener);
	},
	methods: {
		resizeListener() {
			if (document.querySelector('.ho-center-content') && (this.showLogin || this.showRegistration)) this.adjustLoadingPosition();
		},
		queryStatsAndHighlights() {
			this.$network.getData('/api/system/stats', null, null, (err, data) => {
				try {
					if (!err) this.stats = data;
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				}
			});

			this.$network.getData(`/api/system/highlights?amount=${this.amountHighlights}`, null, null, (err, data) => {
				try {
					if (!err) this.highlights = data;
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				}
			});
		},
		checkForQueryMsg() {
			let msg = this.route.query.msg;
			if (msg != null) {
				this.$nextTick(() => {
					if (msg == MSG_TYPE.UNAUTHORIZED) {
						this.$emit('logoutUser', true);
						this.$global.showToast(TOAST_TYPE.WARN, this.$t('warnUnauthorizedAccess'));
					} else if (msg == MSG_TYPE.FORBIDDEN) this.$global.showToast(TOAST_TYPE.WARN, this.$t('warnForbiddenAccess'));
					else if ([MSG_TYPE.REGISTRATION_FAILED, MSG_TYPE.PASSWORD_RESET_FAILED].includes(msg))
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errorLinkInvalid'));
					else if (msg == MSG_TYPE.CODE_EXPIRED) this.$global.showToast(TOAST_TYPE.WARN, this.$t('warnLinkExpired'));
					else if (msg == MSG_TYPE.REGISTRATION_SUCCESSFUL)
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('successRegistrationSuccessful'));
					else if (msg == MSG_TYPE.PASSWORD_RESET_SUCCESSFUL)
						this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('successPasswordResetSuccessful'));
					else if (msg == MSG_TYPE.LOGOUT_SUCCESS) this.$global.showToast(TOAST_TYPE.INFO, this.$t('infoLogoutSuccessful'));
				});
			}
			this.$router.push({ query: {} });
		},
		openRegistration() {
			this.showRegistration = true;
			this.showLogin = false;
			this.adjustLoadingPosition();
		},
		openLogin() {
			this.showLogin = true;
			this.showRegistration = false;
			this.adjustLoadingPosition();
		},
		adjustLoadingPosition() {
			let wrapper = document.documentElement;
			wrapper.style.overflowY = 'hidden';
			this.$nextTick(() => {
				document.querySelector('.ho-center-content').style.top = `${window.scrollY}px`;
			});
		},
		loginUser() {
			this.$emit('loginUser');
			this.closeWindow(true);
		},
		closeWindow(force) {
			if (force || this.clickDownRegistered) {
				this.showLogin = false;
				this.showRegistration = false;
				document.documentElement.style.overflowY = 'auto';
				this.clickDownRegistered = false;
			}
		},
		showVideo() {
			this.showVideoStream = true;
			this.$nextTick(async () => {
				const video = this.$refs.videoPlayer;

				try {
					await video.requestFullscreen?.();
				} catch (err) {
					console.warn('Fullscreen failed:', err);
				}

				try {
					await video.play();
				} catch (err) {
					console.warn('Playback failed:', err);
					this.canPlayVideo = false;
				}
			});
		},
		hideVideo() {
			this.$refs.videoPlayer.pause();
			this.$refs.videoPlayer.currentTime = 0;
			this.showVideoStream = false;
		},
		downloadVideo() {
			const link = document.createElement('a');
			link.href = this.videoSrc;
			link.download = 'video.mp4';
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		},
		async downloadExampleData() {
			try {
				await Promise.all([
					this.triggerDownload(this.codebookSrc, 'codebook.csv'),
					this.triggerDownload(this.dataSrc, 'data.csv'),
					this.triggerDownload(this.codebookPreVitaCovSrc, 'Codebook  MVP_mnppvcovpromis.csv'),
					this.triggerDownload(this.dataPreVitaCovSrc, 'Daten MVP_mnppvcovpromis.csv'),
				]);
			} catch (error) {
				console.log(error);
				this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errDownloadingFiles'));
			}
		},
		triggerDownload(fileUrl, fileName) {
			return new Promise((resolve, reject) => {
				const link = document.createElement('a');
				link.href = fileUrl;
				link.download = fileName;

				link.click();
				resolve();
			});
		},
	},
};
</script>

<style scoped>
.ho-heading {
	width: 100%;
	margin-bottom: 20px;
	font-size: 80px;
	font-weight: normal;
	text-align: center;
}

.ho-wrap-counters {
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
}

.ho-wrap-counters div {
	margin: auto;
}

.ho-wrap-highlights {
	width: 100%;
	margin: 10px 0px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	flex-flow: wrap;
}

.ho-no-highlights {
	width: 100%;
	margin-bottom: 20px;
	text-align: center;
}

.ho-subheading {
	width: 100%;
	margin: 30px 0px 10px 0px;
	font-size: 25px;
	font-weight: normal;
	text-align: start;
	text-decoration: underline;
}

.ho-loading-data-placeholder {
	width: 100%;
	margin: 20px 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 20px;
}

.ho-wrap-registration-login {
	width: 100%;
	margin: 25px 20px;
	text-align: center;
}

.ho-wrap-registration-login button {
	margin: 15px 0px;
	padding: 10px 20px;
	font-size: 20px;
}

.ho-wrap-buttons {
	width: 100%;
	margin: 25px 20px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: column;
	text-align: center;
	gap: 10px;
}

.ho-wrap-buttons button {
	min-width: fit-content;
	width: 450px;
	padding: 10px 20px;
	font-size: 20px;
}

.ho-motivation-text span {
	padding: 2px 0px;
	display: block;
}

.ho-login-text {
	display: block;
}

.ho-login-text span {
	padding-right: 5px;
}

.ho-login-text span:last-child {
	padding-right: 0px;
	text-decoration: underline;
	cursor: pointer;
}

.ho-center-content {
	width: 100vw;
	height: 100vh;
	position: absolute;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: var(--main-color-dark-80);
}

.ho-wrap-video-stream {
	width: 100vw;
	height: 100vh;
	position: fixed;
	top: 0px;
	left: 0px;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: var(--main-color-dark-bb);
}

.ho-wrap-video-stream video {
	border: 1px solid var(--main-color-light);
}

.ho-video-fallback {
	padding: 20px 10px;
	display: flex;
	justify-content: center;
	align-items: center;
	flex-flow: wrap;
	gap: 10px;
	border: 2px solid var(--main-color-light);
	border-radius: 20px;
	background-color: var(--main-color-1);
}

.ho-video-fallback p {
	flex: 1 1 100%;
	font-size: 20px;
	text-align: center;
}

.ho-video-fallback button {
	padding: 10px 30px;
	font-size: 20px;
	text-align: center;
}

.fade-enter-active,
.fade-leave-active {
	transition: opacity 1s ease;
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
