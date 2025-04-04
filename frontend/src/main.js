import { createApp } from 'vue';
import App from './App.vue';
import '@/assets/css/main.css';
import router from './router';
import i18n from '@/translations/i18n';
import { global } from './scripts/global.js';
import { store } from './scripts/store.js';
import { network } from './scripts/network.js';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import './plugins/font-awesome';
import { toastOptions } from './plugins/vue-toastification';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const app = createApp(App);

app.config.globalProperties.$global = global;
app.config.globalProperties.$store = store;
app.config.globalProperties.$network = network;
app.config.globalProperties.$t = i18n.global.t;

app.component('fai', FontAwesomeIcon);

app.use(Toast, toastOptions);
app.use(router);
app.use(i18n);

app.mount('#app');
