<template>
	<div class="ov-wrap-content" ref="graphContainer" @click="floatingHeader.display = false" @contextmenu.prevent="displayHeaderField">
		<OntologyViewerHeader
			:exportRunning="exportRunning"
			:isLoading="isLoading"
			:floatingHeader="floatingHeader"
			ref="graphHeader"
			@downloadPNG="downloadPNG"
			@fitToView="fitToView"
			@reloadGraph="reloadGraph"
		/>
		<LoadingSpinner v-if="isLoading" :displayText="$t('ovLoadingGraph')" :wrapperClass="'ov-wrap-content'" />
		<OntologyElementDetails :details="details" @resetDetails="resetDetails" />
		<div class="ov-graph" ref="graph"></div>
	</div>
</template>

<script>
import LoadingSpinner from '@/components/general/LoadingSpinner.vue';
import OntologyElementDetails from '@/components/ontology/OntologyElementDetails.vue';
import OntologyViewerHeader from '@/components/ontology/OntologyViewerHeader.vue';
import { ONTOLOGY_ELEMENT, ONTOLOGY_OPERATION, GRAPH_TYPE } from '@/enums/enums';
import * as d3 from 'd3';
import * as $rdf from 'rdflib';
/**
 * @vuese
 * @group Ontology
 * Ontology viewer that renders rdf turtle data into a graph
 */
export default {
	name: 'OntologyViewer',
	components: { LoadingSpinner, OntologyElementDetails, OntologyViewerHeader },
	emits: ['selectElement'],
	props: {
		rdfData: {
			type: String,
			required: false,
			default: null,
		},
		selectedElement: {
			type: Number,
			required: false,
		},
		graphType: {
			type: String,
			required: false,
			default: GRAPH_TYPE.ONTOLOGY,
		},
	},
	watch: {
		rdfData: {
			handler: function () {
				this.reloadGraph();
			},
			deep: true,
		},
		selectedElement: {
			handler: function (newVal, oldVal) {
				if (newVal && !this.isLoading) this.clickElementByTag();
				else if (!newVal && oldVal && !this.isLoading) this.$refs.graph.click();
			},
		},
	},
	data() {
		return {
			baseStyle: {
				MAX_WIDTH: 200,
				PADDING_X: 10,
				PADDING_Y: 5,
				LINE_HEIGHT: 14,
				MAX_LINES: 3,
				FONT_SIZE: '14px',
				FONT_WEIGHT: 'bold',
			},
			dataStyle: {
				MAX_WIDTH: 300,
				PADDING_X: 10,
				PADDING_Y: 5,
				LINE_HEIGHT: 14,
				MAX_LINES: 5,
				FONT_SIZE: '14px',
				FONT_WEIGHT: 'bold',
			},
			ontologyConfig: {
				distance: 300,
				chargeStrength: -600,
				collisionComputation: (d) => d.rectWidth / 2 + 20,
			},
			dataConfig: {
				distance: 150,
				chargeStrength: -800,
				collisionComputation: (d) => d.rectWidth / 2 + 20,
			},
			isLoading: false,
			exportRunning: false,
			graph: null,
			store: null,
			simultaion: null,
			zoom: null,
			zoomGroup: null,
			details: null,
			floatingHeader: {
				display: false,
				x: 0,
				y: 0,
			},
		};
	},
	mounted() {
		this.isLoading = true;
		window.dispatchEvent(new Event('resize'));
		if (this.rdfData) this.createOntologyGraph();
	},
	beforeUnmount() {
		this.cleanupGraph();
	},
	methods: {
		createOntologyGraph() {
			this.parseRDFData();

			const {
				groupedNodes: groupedNodes,
				groupedData: groupedData,
				groupedRelationships: groupedRelationships,
			} = this.groupNodesDataAndRelationships();
			const { nodes: nodes, relationships: relationships } = this.computeNodesAndRelationships(groupedNodes, groupedData, groupedRelationships);

			this.drawGraph(nodes, relationships);
		},
		parseRDFData() {
			this.store = $rdf.graph();
			$rdf.parse(this.rdfData, this.store, 'http://example.org/', 'text/turtle');
		},
		groupNodesDataAndRelationships() {
			const groupedNodes = [];
			const groupedData = [];
			const groupedRelationships = [];
			let currentNodeGroup = [];
			let currentDataGroup = [];
			let currentRelationship = [];
			let currentNodeNeighbors = [];
			let currentDataNeighbors = [];

			this.store.statements.forEach((statement, idx) => {
				const s = this.getLocalName(statement.subject.value);
				const p = this.getLocalName(statement.predicate.value);
				const o = this.getLocalName(statement.object.value);
				const d = this.getLocalName(statement.object.datatype ? statement.object.datatype.value : null);

				let isNode = this.isNode(statement.subject);
				let isRelationship = this.isRelationship(statement.subject);
				let isData = this.isData(statement.subject);

				if (isNode && p == 'type' && currentNodeGroup.length != 0) {
					currentNodeGroup.push(currentNodeNeighbors);
					groupedNodes.push(currentNodeGroup);
					currentNodeNeighbors = [];
					currentNodeGroup = [{ s, p, o, d }];
				} else if (isNode && this.isRelationship(statement.predicate)) {
					currentNodeNeighbors.push({
						target: o,
						id: p,
						ONTOLOGY_ELEMENT: this.isNode(statement.object) ? ONTOLOGY_ELEMENT.NODE : ONTOLOGY_ELEMENT.DATA,
					});
				} else if (isNode) currentNodeGroup.push({ s, p, o, d });

				if (isRelationship && p == 'type' && currentRelationship.length != 0) {
					groupedRelationships.push(currentRelationship);
					currentRelationship = [{ s, p, o, d }];
				} else if (isRelationship) currentRelationship.push({ s, p, o, d });

				if (isData && p == 'type' && currentDataGroup.length != 0) {
					currentDataGroup.push(currentDataNeighbors);
					groupedData.push(currentDataGroup);
					currentDataNeighbors = [];
					currentDataGroup = [{ s, p, o, d }];
				} else if (isData && this.isRelationship(statement.predicate)) currentDataNeighbors.push({ target: o, id: p });
				else if (isData) currentDataGroup.push({ s, p, o, d });
			});

			currentNodeGroup.push(currentNodeNeighbors);
			groupedNodes.push(currentNodeGroup);

			currentDataGroup.push(currentDataNeighbors);
			if (currentDataGroup.length > 1) groupedData.push(currentDataGroup);

			groupedRelationships.push(currentRelationship);

			return { groupedNodes: groupedNodes, groupedData: groupedData, groupedRelationships: groupedRelationships };
		},
		getLocalName(uri) {
			try {
				const lastSlash = uri.lastIndexOf('/');
				const lastHash = uri.lastIndexOf('#');
				const separator = Math.max(lastSlash, lastHash);
				return uri.substring(separator + 1);
			} catch (error) {
				return null;
			}
		},
		isRelationship(element) {
			return element.value.includes('/relationship#');
		},
		isNode(element) {
			return element.value.includes('/node#');
		},
		isData(element) {
			return element.value.includes('/data#');
		},
		computeNodesAndRelationships(groupedNodes, groupedData, groupedRelationships) {
			let nodes = [];
			let relationships = [];

			groupedNodes.forEach((group) => {
				let node = { ONTOLOGY_ELEMENT: ONTOLOGY_ELEMENT.NODE };
				group.forEach((statement) => {
					if (!node[statement.p]) {
						if (Array.isArray(statement)) node.neighbors = statement;
						else if (statement.p == 'type') node.id = statement.s;
						else {
							if (statement.d == 'boolean') node[statement.p] = statement.o === 'true';
							else if (statement.d == 'long') node[statement.p] = Number(statement.o);
							else node[statement.p] = statement.o;
						}
					} else {
						if (Array.isArray(node[statement.p])) node[statement.p].push(statement.o);
						else node[statement.p] = [node[statement.p], statement.o];
					}
				});

				nodes.push(node);
			});

			groupedData.forEach((group) => {
				let data = { ONTOLOGY_ELEMENT: ONTOLOGY_ELEMENT.DATA };
				group.forEach((statement) => {
					if (!data[statement.p]) {
						if (Array.isArray(statement)) data.neighbors = statement;
						else if (statement.p == 'type') data.id = statement.s;
						else {
							if (statement.data == 'boolean') data[statement.p] = statement.o === 'true';
							else if (statement.data == 'long') data[statement.p] = Number(statement.o);
							else data[statement.p] = statement.o;
						}
					} else {
						if (Array.isArray(data[statement.p])) data[statement.p].push(statement.o);
						else data[statement.p] = [data[statement.p], statement.o];
					}
				});

				nodes.push(data);
			});

			groupedRelationships.forEach((group) => {
				let relationship = {};

				group.forEach((statement) => {
					if (!relationship[statement.p]) {
						if (statement.p == 'type') relationship.id = statement.s;
						else {
							if (statement.d == 'boolean') relationship[statement.p] = statement.o === 'true';
							else if (statement.d == 'long') relationship[statement.p] = Number(statement.o);
							else relationship[statement.p] = statement.o;
						}
					} else {
						if (Array.isArray(relationship[statement.p])) relationship[statement.p].push(statement.o);
						else relationship[statement.p] = [relationship[statement.p], statement.o];
					}
				});

				relationships.push(relationship);
			});

			// Map node neighbors
			nodes = this.mapNodeNeighbors(nodes, relationships);

			// Map source and target of relationship
			relationships = this.mapRelationshipSourceAndTarget(nodes, relationships);

			return { nodes: nodes, relationships: relationships };
		},
		mapNodeNeighbors(nodes, relationships) {
			return nodes.map((node) => {
				node.neighbors = node.neighbors.map((it) => {
					let rel = relationships.find((rel) => rel.id == it.id);
					it.name = rel.name;
					it.cardinality = rel.cardinality;
					it.deleted = rel.deleted;
					it.added = rel.added;
					it.modified = rel.modified;
					return it;
				});

				return node;
			});
		},
		// Duplicates relationships for the same nodes and maps their source and target nodes
		mapRelationshipSourceAndTarget(nodes, relationships) {
			let mappedRelationships = [];

			nodes.forEach((node) => {
				node.neighbors.forEach((neighbor) => {
					let relationship = relationships.find((rel) => rel.id == neighbor.id);
					let target = nodes.find((it) => it.id == neighbor.target && it.ONTOLOGY_ELEMENT == neighbor.ONTOLOGY_ELEMENT);

					if (relationship && target) {
						mappedRelationships.push({
							...relationship,
							target: target,
							source: node,
						});
					}
				});
			});

			return mappedRelationships;
		},
		drawGraph(nodes, relationships) {
			this.graph = d3.select(this.$refs.graph).append('svg').attr('width', '100%').attr('height', '100%');

			// Reset highlights when clicking outside the graph
			d3.select(this.$refs.graph).on('click', this.resetDetails);

			this.addZoom();

			this.startSimulation(nodes, relationships);

			this.updateSimulation(this.createRelationships(relationships), this.createRelationshipLabels(relationships), this.createNodes(nodes));
		},
		addZoom() {
			this.zoomGroup = this.graph.append('g');

			const zoom = d3
				.zoom()
				.scaleExtent([0.1, 3])
				.on('zoom', (event) => {
					this.zoomGroup.attr('transform', event.transform);

					this.zoomGroup
						.selectAll('.ov-node-label')
						.classed('ov-show-label', event.transform.k > 0.2)
						.classed('ov-hide-label', event.transform.k <= 0.2);
					this.zoomGroup
						.selectAll('.ov-relationship-label')
						.classed('ov-show-label', event.transform.k > 0.4)
						.classed('ov-hide-label', event.transform.k <= 0.4);
				});

			this.graph.call(zoom);
			this.zoom = zoom;
		},
		startSimulation(nodes, relationships) {
			const config = this.graphType == GRAPH_TYPE.ONTOLOGY ? this.ontologyConfig : this.dataConfig;
			this.simulation = d3
				.forceSimulation(nodes)
				.force(
					'ov-relationship',
					d3
						.forceLink(relationships)
						.id((d) => d.id)
						.distance(config.distance)
				)
				.force('charge', d3.forceManyBody().strength(config.chargeStrength))
				.force('collision', d3.forceCollide().radius(config.collisionComputation))
				.force('center', d3.forceCenter(this.$refs.graph.clientWidth / 2, this.$refs.graph.clientHeight / 2))
				.on('end', () => {
					// Prevent fit when not loading
					if (this.isLoading) {
						this.isLoading = false;
						this.fitToView();
						if (this.selectedElement) this.clickElementByTag();
					}
				});
		},
		getOperation(d) {
			return d.added
				? ONTOLOGY_OPERATION.ADDED
				: d.modified
					? ONTOLOGY_OPERATION.MODIFIED
					: d.deleted
						? ONTOLOGY_OPERATION.DELETED
						: ONTOLOGY_OPERATION.UNMODIFIED;
		},
		getColorByOperation(operation, type) {
			return operation == ONTOLOGY_OPERATION.ADDED
				? 'var(--main-color-success)'
				: operation == ONTOLOGY_OPERATION.MODIFIED
					? 'var(--main-color-warn)'
					: operation == ONTOLOGY_OPERATION.DELETED
						? 'var(--main-color-error)'
						: type == ONTOLOGY_ELEMENT.RELATIONSHIP
							? 'var(--main-color-relationship)'
							: type == ONTOLOGY_ELEMENT.LEAF
								? 'var(--main-color-leaf)'
								: type == ONTOLOGY_ELEMENT.STAKEHOLDER
									? 'var(--main-color-stakeholder)'
									: type == ONTOLOGY_ELEMENT.DATA
										? 'var(--main-color-data)'
										: 'var(--main-color-node)';
		},
		createArrowMarkers() {
			const keys = Object.keys(ONTOLOGY_OPERATION);

			for (let i = 0; i < keys.length; i++) {
				this.graph
					.append('defs')
					.append('marker')
					.attr('id', `arrow_${keys[i]}`)
					.attr('viewBox', '0 -5 10 10')
					.attr('refX', 5)
					.attr('refY', 0)
					.attr('markerWidth', 3)
					.attr('markerHeight', 3)
					.attr('orient', 'auto')
					.append('path')
					.attr('d', 'M0,-5L10,0L0,5')
					.attr('fill', this.getColorByOperation(keys[i], ONTOLOGY_ELEMENT.RELATIONSHIP));
			}
		},
		createRelationships(relationships) {
			this.createArrowMarkers();

			return this.zoomGroup
				.append('g')
				.selectAll('line')
				.data(relationships)
				.enter()
				.append('line')
				.attr('id', (d) => d.tag)
				.attr('stroke', (d) => this.getColorByOperation(this.getOperation(d), ONTOLOGY_ELEMENT.RELATIONSHIP))
				.attr('stroke-width', 3)
				.attr('marker-end', (d) => `url(#arrow_${this.getOperation(d)})`)
				.attr('class', 'ov-relationship')
				.attr('cursor', 'pointer')
				.on('click', this.relationshipClickListener);
		},
		createRelationshipLabels(relationships) {
			return this.zoomGroup
				.append('g')
				.selectAll('text')
				.data(relationships)
				.enter()
				.append('text')
				.text((d) => d.name)
				.attr('fill', 'var(--main-color-light)')
				.attr('font-size', this.baseStyle.FONT_SIZE)
				.attr('font-weight', this.baseStyle.FONT_WEIGHT)
				.attr('class', 'ov-relationship-label')
				.attr('cursor', 'pointer')
				.on('click', this.relationshipClickListener);
		},
		relationshipClickListener(e, d) {
			e.stopPropagation();

			if (
				!this.details ||
				(this.details.from == ONTOLOGY_ELEMENT.RELATIONSHIP && this.details.data.id !== d.id) ||
				this.details.from != ONTOLOGY_ELEMENT.RELATIONSHIP
			) {
				this.details = { from: ONTOLOGY_ELEMENT.RELATIONSHIP, data: d };
				this.$emit('selectElement', this.details);
				this.highlightRelationship(d);
			}
		},
		createNodes(nodes) {
			const nodeGroups = this.zoomGroup
				.append('g')
				.selectAll('g')
				.data(nodes)
				.enter()
				.append('g')
				.attr('class', 'ov-node')
				.attr('id', (d) => d.tag)
				.on('click', (e, d) => this.nodeClickListener(e, d, nodes))
				.call(this.nodeDragListener());

			let that = this;
			nodeGroups.each(function (d) {
				that.computeNodeText(d, this);
			});

			nodeGroups
				.insert('rect', 'text')
				.attr('width', (d) => d.rectWidth)
				.attr('height', (d) => d.rectHeight)
				.attr('x', (d) => -d.rectWidth / 2)
				.attr('y', (d) => -d.rectHeight / 2)
				.attr('rx', 5)
				.attr('fill', (d) =>
					this.getColorByOperation(
						this.getOperation(d),
						d.is_leaf
							? ONTOLOGY_ELEMENT.LEAF
							: d.is_stakeholder
								? ONTOLOGY_ELEMENT.STAKEHOLDER
								: d.ONTOLOGY_ELEMENT == ONTOLOGY_ELEMENT.DATA
									? ONTOLOGY_ELEMENT.DATA
									: ONTOLOGY_ELEMENT.NODE
					)
				)
				.attr('stroke', 'var(--main-color-dark)')
				.attr('stroke-width', 2)
				.attr('cursor', 'pointer');

			return nodeGroups;
		},
		nodeClickListener(e, d, nodes) {
			e.stopPropagation();
			let notSameElement = this.details?.from == ONTOLOGY_ELEMENT.RELATIONSHIP;
			let notSameID =
				[ONTOLOGY_ELEMENT.STAKEHOLDER, ONTOLOGY_ELEMENT.NODE, ONTOLOGY_ELEMENT.LEAF, ONTOLOGY_ELEMENT.DATA].includes(this.details?.from) &&
				this.details?.data.id !== d.id;

			if (!this.details || notSameElement || notSameID) {
				let mappedNeighbors = d.neighbors.map((it) => {
					let neighbor = nodes.find((node) => node.id == it.target);
					return {
						target: !neighbor
							? null
							: {
									id: neighbor.id,
									name: neighbor.name,
									deleted: neighbor.deleted,
									added: neighbor.added,
									modified: neighbor.modified,
								},
						name: it.name,
						cardinality: it.cardinality,
						added: it.added,
						deleted: it.deleted,
						modified: it.modified,
					};
				});

				nodes.forEach((node) => {
					let neighbor = node.neighbors.filter((n) => n.target == d.id)[0];
					if (neighbor) {
						mappedNeighbors.push({
							source: { id: node.id, name: node.name, deleted: node.deleted, added: node.added, modified: node.modified },
							name: neighbor.name,
							cardinality: neighbor.cardinality,
							deleted: neighbor.deleted,
							added: neighbor.added,
							modified: neighbor.modified,
						});
					}
				});

				this.details = {
					from: d.is_stakeholder
						? ONTOLOGY_ELEMENT.STAKEHOLDER
						: d.is_leaf
							? ONTOLOGY_ELEMENT.LEAF
							: d.ONTOLOGY_ELEMENT == ONTOLOGY_ELEMENT.DATA
								? ONTOLOGY_ELEMENT.DATA
								: ONTOLOGY_ELEMENT.NODE,
					data: { ...d, neighbors: mappedNeighbors },
				};
				this.$emit('selectElement', this.details);
				this.highlightNode(d);
			}
		},
		nodeDragListener() {
			return d3
				.drag()
				.on('start', (e, d) => {
					if (!e.active) this.simulation.alphaTarget(0.3).restart();
					d.fx = d.x;
					d.fy = d.y;
				})
				.on('drag', (e, d) => {
					d.fx = e.x;
					d.fy = e.y;
				})
				.on('end', (e, d) => {
					if (!e.active) this.simulation.alphaTarget(0);
					d.fx = null;
					d.fy = null;
				});
		},
		computeNodeText(d, that) {
			const group = d3.select(that);
			const words = d.name ? d.name.split(' ') : d.value ? d.value?.split(' ') : ['-'];
			let lines = [];
			let tempText = '';
			let style = d.ONTOLOGY_ELEMENT == ONTOLOGY_ELEMENT.DATA ? this.dataStyle : this.baseStyle;

			const temp = group.append('text').attr('font-size', style.FONT_SIZE).attr('font-weight', style.FONT_WEIGHT).attr('visibility', 'hidden');

			let maxLineWidth = 0;

			words.forEach((word) => {
				temp.text(tempText + (tempText ? ' ' : '') + word);
				if (temp.node().getBBox().width <= style.MAX_WIDTH - style.PADDING_X * 2) tempText += (tempText ? ' ' : '') + word;
				else {
					lines.push(tempText);
					maxLineWidth = Math.max(maxLineWidth, temp.node().getBBox().width);
					tempText = word;
				}
			});

			if (tempText) lines.push(tempText);
			maxLineWidth = Math.max(maxLineWidth, temp.node().getBBox().width);

			if (lines.length > style.MAX_LINES) {
				lines = lines.slice(0, style.MAX_LINES);
				lines[style.MAX_LINES - 1] = lines[style.MAX_LINES - 1].slice(0, -3) + '...';
			}

			temp.remove();

			d.rectWidth = Math.min(maxLineWidth + style.PADDING_X * 2, style.MAX_WIDTH);
			d.rectHeight = lines.length * style.LINE_HEIGHT + style.PADDING_Y * 2;

			lines.forEach((line, index) => {
				group
					.append('text')
					.text(line)
					.attr('font-size', style.FONT_SIZE)
					.attr('font-weight', style.FONT_WEIGHT)
					.attr('text-anchor', 'start')
					.attr('x', -d.rectWidth / 2 + style.PADDING_X)
					.attr('y', -d.rectHeight / 2 + style.PADDING_Y + style.LINE_HEIGHT * (index + 0.75))
					.attr('class', 'ov-node-label')
					.attr('fill', 'var(--main-color-dark)')
					.attr('cursor', 'pointer');
			});
		},
		resetHighlight(dimmed) {
			d3.selectAll('.ov-node').classed('ov-highlight', false).classed('ov-dimmed', dimmed);
			d3.selectAll('.ov-relationship').classed('ov-highlight', false).classed('ov-dimmed', dimmed);
			d3.selectAll('.ov-relationship-label').classed('ov-highlight', false).classed('ov-dimmed', dimmed);
		},
		highlightNode(node) {
			this.resetHighlight(true);

			// Highlight clicked node
			d3.selectAll('.ov-node')
				.filter((d) => d.id === node.id)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();

			// Highlight connected relationships
			const connectedRelationships = d3
				.selectAll('.ov-relationship')
				.filter((d) => d.source.id === node.id || d.target.id === node.id)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();

			// Highlight connected relationship labels
			d3.selectAll('.ov-relationship-label')
				.filter((d) => d.source.id === node.id || d.target.id === node.id)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();

			// Find and highlight connected nodes
			const connectedNodes = new Set();
			connectedRelationships.each((d) => {
				connectedNodes.add(d.source.id);
				connectedNodes.add(d.target.id);
			});

			d3.selectAll('.ov-node')
				.filter((d) => connectedNodes.has(d.id))
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();
		},
		highlightRelationship(relationship) {
			this.resetHighlight(true);

			// Highlight clicked relationship
			d3.selectAll('.ov-relationship')
				.filter((d) => d === relationship)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();

			// Highlight connected nodes
			d3.selectAll('.ov-node')
				.filter((d) => d.id === relationship.source.id || d.id === relationship.target.id)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();

			// Highlight relationship label
			d3.selectAll('.ov-relationship-label')
				.filter((d) => d === relationship)
				.classed('ov-highlight', true)
				.classed('ov-dimmed', false)
				.raise();
		},
		updateSimulation(relationship, relationshipLabel, node) {
			this.simulation.on('tick', () => {
				relationship
					.attr('x1', (d) => d.source.x)
					.attr('y1', (d) => d.source.y)
					.attr('x2', (d) => {
						const { x: x1, y: y1 } = d.source;
						const { x: x2, y: y2 } = d.target;
						const width = d.target.rectWidth;
						const height = d.target.rectHeight;
						return this.getRectBorderPoint(x1, y1, x2, y2, width, height).x;
					})
					.attr('y2', (d) => {
						const { x: x1, y: y1 } = d.source;
						const { x: x2, y: y2 } = d.target;
						const width = d.target.rectWidth;
						const height = d.target.rectHeight;
						return this.getRectBorderPoint(x1, y1, x2, y2, width, height).y;
					});

				node.attr('transform', (d) => `translate(${d.x}, ${d.y})`);
				relationshipLabel
					.attr('x', (d) => {
						const { x1, y1, x2, y2 } = this.getLineEndpoints(d);
						return (x1 + x2) / 2;
					})
					.attr('y', (d) => {
						const { x1, y1, x2, y2 } = this.getLineEndpoints(d);
						return (y1 + y2) / 2;
					});
			});
		},
		clickElementByTag() {
			const element = this.$refs.graph.querySelector(`[id="${this.selectedElement}"]`);
			if (element) element.dispatchEvent(new Event('click', { bubbles: true }));
		},
		getRectBorderPoint(x1, y1, x2, y2, width, height, offset = 5) {
			const dx = x2 - x1;
			const dy = y2 - y1;
			const halfWidth = width / 2;
			const halfHeight = height / 2;

			// Determine scaling factor to stop at border instead of center
			const scaleX = halfWidth / Math.abs(dx);
			const scaleY = halfHeight / Math.abs(dy);
			const scale = Math.min(scaleX, scaleY);

			// Compute the intersection point at the border
			let targetX = x2 - dx * scale;
			let targetY = y2 - dy * scale;

			// Adjust by offset to move slightly away from the node
			const length = Math.sqrt(dx * dx + dy * dy);
			targetX -= (dx / length) * offset;
			targetY -= (dy / length) * offset;

			return { x: targetX, y: targetY };
		},
		getLineEndpoints(d) {
			const { x: x1, y: y1 } = d.source;
			const { x: x2, y: y2 } = d.target;
			const width = d.target.rectWidth;
			const height = d.target.rectHeight;

			const end = this.getRectBorderPoint(x1, y1, x2, y2, width, height);

			return {
				x1,
				y1,
				x2: end.x,
				y2: end.y,
			};
		},
		resetDetails() {
			this.resetHighlight(false);
			this.$emit('selectElement', null);
			this.details = null;
		},
		fitToView() {
			const bounds = this.zoomGroup.node().getBBox();
			const svg = this.graph.node().getBoundingClientRect();

			const scale = Math.min(svg.width / bounds.width, svg.height / bounds.height) * 0.8;

			const translateX = svg.width / 2 - scale * (bounds.x + bounds.width / 2);
			const translateY = svg.height / 2 - scale * (bounds.y + bounds.height / 2);

			this.graph.transition().duration(750).call(this.zoom.transform, d3.zoomIdentity.translate(translateX, translateY).scale(scale));
		},
		downloadPNG() {
			if (!this.exportRunning) {
				this.exportRunning = true;
				const svgElement = this.$refs.graph.querySelector('svg');
				svgElement.querySelectorAll('*').forEach(this.convertStyles);

				const canvas = document.createElement('canvas');
				const ctx = canvas.getContext('2d');
				const img = new Image();

				// Get the zoom transform scale (from D3 zoom)
				const transform = d3.zoomTransform(svgElement);
				const zoomScale = transform.k; // Extract zoom level

				// Set a base resolution and adjust for zoom
				const baseScale = 3; // Default upscale
				const scaleFactor = baseScale / zoomScale;

				img.onload = () => {
					const link = document.createElement('a');

					// Set higher resolution for the canvas
					canvas.width = svgElement.clientWidth * scaleFactor;
					canvas.height = svgElement.clientHeight * scaleFactor;

					// Scale the context to maintain the quality
					ctx.scale(scaleFactor, scaleFactor);
					ctx.drawImage(img, 0, 0);

					link.href = canvas.toDataURL('image/png');
					link.download = `ontology_${this.$global.formatDate(new Date(), 'iso')}.png`;

					document.body.appendChild(link);
					link.click();
					document.body.removeChild(link);

					this.exportRunning = false;
				};

				const serializer = new XMLSerializer();
				const svgString = serializer.serializeToString(svgElement);
				img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
			}
		},
		convertStyles(element) {
			const computedStyle = window.getComputedStyle(element);
			element.setAttribute('fill', computedStyle.fill);
			element.setAttribute('stroke', computedStyle.stroke);
		},
		displayHeaderField(e) {
			if (!this.isLoading) {
				const rect = e.currentTarget.getBoundingClientRect();

				// Calculate the initial position of the floating header
				let x = e.clientX - rect.left;
				let y = e.clientY - rect.top;

				// Set the floating header's position before we calculate its dimensions
				this.floatingHeader.x = x;
				this.floatingHeader.y = y;
				this.floatingHeader.display = true;

				// Now we need to measure the actual dimensions of the floating header after rendering
				// Using nextTick to ensure the floating header is rendered and can be measured
				this.$nextTick(() => {
					const headerRect = this.$refs.graphHeader.$refs.floatingHeader.getBoundingClientRect();
					const containerRect = this.$refs.graphContainer.getBoundingClientRect();

					// Prevent overflow on the right edge
					if (x + headerRect.width > containerRect.width) x = x - headerRect.width;

					// Prevent overflow on the bottom edge
					if (y + headerRect.height > containerRect.height) y = y - (y + headerRect.height - containerRect.height);

					// Set the final adjusted positions
					this.floatingHeader.x = x;
					this.floatingHeader.y = y;
				});
			}
		},
		reloadGraph() {
			this.isLoading = true;
			this.details = null;
			this.$emit('selectElement', null);
			this.cleanupGraph();
			this.createOntologyGraph();
		},
		cleanupGraph() {
			if (this.graph) this.graph.remove();
			if (this.simulation) this.simulation.stop();
			if (this.store) this.store.close();

			this.graph = null;
			this.simulation = null;
			this.store = null;
			this.zoom = null;
			this.zoomGroup = null;
		},
	},
};
</script>

<style scoped>
.ov-wrap-content {
	width: 100%;
	height: 100%;
	position: relative;
	overflow: hidden !important;
	background-color: var(--main-color-dark);
}

.ov-graph {
	width: 100%;
	height: 100%;
}
</style>

<style>
.ov-node-label,
.ov-relationship-label {
	transition: opacity 0.5s ease;
}

.ov-highlight {
	opacity: 1 !important;
}

.ov-dimmed {
	opacity: 0.25 !important;
}

.ov-show-label {
	opacity: 1;
}

.ov-hide-label {
	opacity: 0;
}
</style>
