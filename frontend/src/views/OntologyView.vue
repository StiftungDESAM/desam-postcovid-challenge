<template>
	<div class="ov-wrap-content">
		<h2>{{ $t('ovOntologyView') }}</h2>
		<div class="ov-wrap-viewer">
			<OntologyViewer :rdfData="rdf" />
		</div>
		<div class="ov-wrap-buttons">
			<button
				v-if="currentUser.access.permissionsGranted.includes(permENUM.ONTOLOGY_UPLOAD)"
				class="app-default-btn"
				@click="$refs.fileInput.click()"
			>
				<span>{{ $t('ovUploadFile') }}</span> <fai icon="fas fa-upload" />
			</button>
			<input type="file" ref="fileInput" @change="uploadFile" :accept="['.rdf', '.owl']" style="display: none" />
			<button v-if="currentUser.access.permissionsGranted.includes(permENUM.ONTOLOGY_EXPORT)" class="app-default-btn" @click="exportOntology">
				<span>{{ $t('ovExportOntology') }}</span> <fai icon="fas fa-download" />
			</button>
			<button v-if="uploadedRdf && displayUploaded" class="app-default-btn" @click="changeDisplaySource">
				<span>{{ $t('ovDisplayExistingOntology') }}</span> <fai icon="fas fa-eye" />
			</button>
			<button v-if="uploadedRdf && displayExisting" class="app-default-btn" @click="changeDisplaySource">
				<span>{{ $t('ovDisplayUploadedOntology') }}</span> <fai icon="fas fa-eye" />
			</button>
			<button v-if="uploadedRdf" class="app-default-btn" @click="requestOntologyDiff">
				<span>{{ $t('ovDisplayDiffGraph') }}</span> <fai icon="fas fa-code-compare" />
			</button>
			<button v-if="uploadedRdf" class="app-success-btn" @click="submitOntology">
				<span>{{ $t('ovSubmitUploadedOntology') }}</span> <fai icon="fas fa-paper-plane" />
			</button>
		</div>
	</div>
</template>

<script>
import OntologyViewer from '@/components/ontology/OntologyViewer.vue';
import rdfOntology from '@/assets/dummy/rdfOntology.json';
import modifiedOntology from '@/assets/dummy/modifiedOntology.json';
import * as rdf from 'rdflib';
import { PERMISSION, TOAST_TYPE } from '@/enums/enums';
/**
 * @vuese
 * @group OntologyView
 * Displays the OntologyViewer and a detail view about selected nodes or edges
 */
export default {
	name: 'OntologyView',
	components: { OntologyViewer },
	emits: [],
	props: {},
	setup() {
		const permENUM = PERMISSION;
		return { permENUM };
	},
	data() {
		return {
			currentUser: this.$store.getCurrentUser(),
			isLoading: false,
			rdf: null,
			diffRdf: null,
			uploadedRdf: null,
			originalRdf: null,
			displayExisting: true,
			displayUploaded: false,
			rdfOntology: rdfOntology.rdf,
			modifiedOntology: modifiedOntology.rdf,
		};
	},
	created() {
		this.queryOntology();
	},
	mounted() {},
	beforeDestroy() {},
	methods: {
		queryOntology() {
			this.isLoading = true;

			this.$network.getData('/api/ontology/', null, null, (err, data) => {
				try {
					if (!err) {
						this.originalRdf = data.rdf;
						this.rdf = data.rdf;
					} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					// TODO: Remove mocked data
					// if (err) {
					// 	// if(!err){
					// 	this.originalRdf = this.rdfOntology;
					// 	this.rdf = this.rdfOntology;
					// } else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		uploadFile(e) {
			const file = e.target.files[0];
			e.target.value = '';
			if (!file) return;

			if (!file.name.endsWith('.rdf') && !file.name.endsWith('.owl')) {
				this.$global.showToast(TOAST_TYPE.ERROR, this.$t('ovOnlyRDFFilesAllowed'));
				return;
			}

			if (file.name.endsWith('.owl')) {
				const formData = new FormData();
				formData.append('file', file);

				this.sendFileToBackend(formData);
			} else {
				const reader = new FileReader();
				reader.onload = async (e) => {
					try {
						let fileData = e.target.result.toString();

						const isValidTurtle = await this.isTurtleSyntax(fileData);
						if (!isValidTurtle) this.$global.showToast(TOAST_TYPE.ERROR, this.$t('ovOnlyRDFFilesAllowed'));
						else {
							this.diffRdf = null;
							this.uploadedRdf = fileData;
							this.changeDisplaySource();
						}
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, error);
					}
				};

				reader.readAsText(file);
			}
		},
		async isTurtleSyntax(content) {
			try {
				const store = rdf.graph();
				const baseUri = 'http://example.org/';
				const mimeType = 'text/turtle';

				rdf.parse(content, store, baseUri, mimeType);
				return true;
			} catch (error) {
				return false;
			}
		},
		sendFileToBackend(file) {
			this.isLoading = true;

			this.$network.postData(
				'/api/ontology/file-to-rdf',
				file,
				{
					token: this.$store.getToken(),
					headers: {
						'Content-Type': 'multipart/form-data',
					},
				},
				(err, data) => {
					try {
						if (!err) {
							this.diffRdf = null;
							this.uploadedRdf = data.rdf;
							this.changeDisplaySource();
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				}
			);
		},
		changeDisplaySource() {
			if (this.displayExisting) this.rdf = this.uploadedRdf;
			else this.rdf = this.originalRdf;

			this.displayExisting = !this.displayExisting;
			this.displayUploaded = !this.displayUploaded;
		},
		requestOntologyDiff() {
			if (!this.diffRdf) {
				this.isLoading = true;

				this.$network.postData('/api/ontology/diff', { rdf: this.uploadedRdf }, null, (err, data) => {
					try {
						if (!err) {
							this.diffRdf = data.rdf;
							this.rdf = this.diffRdf;
						} else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
					} catch (error) {
						this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
					} finally {
						this.isLoading = false;
					}
				});
			} else this.rdf = this.diffRdf;
		},
		submitOntology() {
			this.isLoading = true;

			this.$network.postData('/api/ontology/', { rdf: this.uploadedRdf }, null, (err, data) => {
				try {
					if (!err) this.$global.showToast(TOAST_TYPE.SUCCESS, this.$t('ovSubmittedOntologySuccessfully'));
					else this.$global.showToast(TOAST_TYPE.ERROR, this.$t(err.msg));
				} catch (error) {
					this.$global.showToast(TOAST_TYPE.ERROR, this.$t('errUnexpectedError'));
				} finally {
					this.isLoading = false;
				}
			});
		},
		exportOntology() {
			const blob = new Blob([this.originalRdf], { type: 'text/turtle' });

			const a = document.createElement('a');
			a.href = URL.createObjectURL(blob);
			a.download = `ontology_${this.$global.formatDate(new Date(), null, true)}.rdf`;

			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(a.href);
		},
	},
};
</script>

<style scoped>
.ov-wrap-content {
	width: 100%;
}

.ov-wrap-content h2 {
	margin-bottom: 10px;
	font-weight: normal;
	text-decoration: underline;
	text-align: start;
}

.ov-wrap-viewer {
	width: 100%;
	height: 80vh;
	min-width: 500px;
	position: relative;
	overflow: hidden;
	border: 1px solid var(--main-color-light);
	box-sizing: border-box;
}

.ov-wrap-buttons {
	width: 100%;
	margin: 20px 0px;
	display: flex;
	justify-content: center;
	align-items: stretch;
	flex-flow: wrap;
	gap: 5px 10px;
}

.ov-wrap-buttons button {
	flex: 1 1 250px;
	min-height: 40px;
	font-size: 15px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.ov-wrap-buttons button svg {
	margin-left: 10px;
	font-size: 20px;
}
</style>
