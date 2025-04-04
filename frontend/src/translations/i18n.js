import { createI18n } from 'vue-i18n';
import en from './en.json';
import de from './de.json';

const messages = {
	en,
	de,
};

const i18n = createI18n({
	legacy: false, // Required for Composition API
	locale: 'de', // Default language
	fallbackLocale: 'de',
	escapeParameterHtml: false,
	messages,
});

export default i18n;
